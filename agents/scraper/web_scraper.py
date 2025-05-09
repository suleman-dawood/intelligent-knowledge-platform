#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web scraper module for extracting content from websites.
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebScraper:
    """Scraper for extracting content from web pages."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the web scraper.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Set default rate limiting
        self.rate_limit = config.get('web_scraper', {}).get('rate_limit', 1)  # requests per second
        self.last_request_time = 0
        
        # User agent rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        self.user_agent_index = 0
        
        logger.info("Web scraper initialized")
    
    async def scrape(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape content from a web page.
        
        Args:
            task_data: Task data containing scraping parameters
            
        Returns:
            Scraped content
        """
        url = task_data.get('url')
        selector = task_data.get('selector')
        include_metadata = task_data.get('include_metadata', True)
        extract_links = task_data.get('extract_links', False)
        follow_links = task_data.get('follow_links', False)
        max_depth = task_data.get('max_depth', 1)
        max_links = task_data.get('max_links', 10)
        
        if not url:
            raise ValueError("URL is required")
            
        logger.info(f"Scraping web page: {url}")
        
        # Apply rate limiting
        self._apply_rate_limit()
        
        # Fetch the page
        html_content = await self._fetch_url(url)
        
        # Parse the content
        content, metadata = await self._parse_content(html_content, url, selector)
        
        # Build the result
        result = {
            "url": url,
            "content": content
        }
        
        # Add metadata if requested
        if include_metadata:
            result["metadata"] = metadata
            
        # Extract and potentially follow links
        if extract_links or follow_links:
            links = self._extract_links(html_content, url)
            
            if extract_links:
                result["links"] = links
                
            if follow_links and max_depth > 1:
                # Limit the number of links to follow
                links_to_follow = links[:max_links]
                
                # Follow each link
                follow_results = []
                for link in links_to_follow:
                    try:
                        # Apply rate limiting for each request
                        self._apply_rate_limit()
                        
                        # Recursively scrape the linked page (with decreased depth)
                        link_result = await self.scrape({
                            "url": link,
                            "selector": selector,
                            "include_metadata": include_metadata,
                            "extract_links": False,  # Don't extract links from followed pages
                            "follow_links": False,   # Don't follow links from followed pages
                            "max_depth": max_depth - 1
                        })
                        
                        follow_results.append(link_result)
                    except Exception as e:
                        logger.warning(f"Error following link {link}: {e}")
                        
                result["followed_links"] = follow_results
        
        return result
    
    async def _fetch_url(self, url: str) -> str:
        """Fetch content from a URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string
        """
        # Rotate user agents
        user_agent = self._get_next_user_agent()
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        try:
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                async with session.get(url) as response:
                    # Check if the request was successful
                    if response.status != 200:
                        raise ValueError(f"Failed to fetch URL: {url}, status code: {response.status}")
                        
                    return await response.text()
        except Exception as e:
            logger.error(f"Error fetching URL {url}: {e}")
            raise
    
    async def _parse_content(
        self, 
        html_content: str, 
        url: str, 
        selector: Optional[str]
    ) -> tuple[str, Dict[str, Any]]:
        """Parse HTML content.
        
        Args:
            html_content: HTML content to parse
            url: URL of the page
            selector: CSS selector to extract content
            
        Returns:
            Tuple of (extracted content, metadata)
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract metadata
        metadata = self._extract_metadata(soup, url)
        
        # Extract content based on selector
        if selector:
            elements = soup.select(selector)
            
            if not elements:
                logger.warning(f"No elements found with selector: {selector}")
                content = ""
            else:
                content = "\n".join(element.get_text().strip() for element in elements)
        else:
            # If no selector is provided, extract the main content (removing navigation, etc.)
            # For a more robust implementation, this would use more advanced content extraction
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
                
            # Get text
            content = soup.get_text()
            
            # Collapse whitespace
            lines = (line.strip() for line in content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = '\n'.join(chunk for chunk in chunks if chunk)
        
        return content, metadata
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata from a web page.
        
        Args:
            soup: BeautifulSoup object
            url: URL of the page
            
        Returns:
            Dictionary of metadata
        """
        metadata = {
            "url": url,
            "domain": urlparse(url).netloc,
            "timestamp": time.time()
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata["title"] = title_tag.string.strip()
            
        # Extract meta description
        description_tag = soup.find('meta', attrs={"name": "description"})
        if description_tag:
            metadata["description"] = description_tag.get("content", "").strip()
            
        # Extract meta keywords
        keywords_tag = soup.find('meta', attrs={"name": "keywords"})
        if keywords_tag:
            metadata["keywords"] = keywords_tag.get("content", "").strip()
            
        # Extract author
        author_tag = soup.find('meta', attrs={"name": "author"})
        if author_tag:
            metadata["author"] = author_tag.get("content", "").strip()
            
        # Extract canonical URL
        canonical_tag = soup.find('link', attrs={"rel": "canonical"})
        if canonical_tag:
            metadata["canonical_url"] = canonical_tag.get("href", "").strip()
            
        return metadata
    
    def _extract_links(self, html_content: str, base_url: str) -> List[str]:
        """Extract links from HTML content.
        
        Args:
            html_content: HTML content
            base_url: Base URL for resolving relative links
            
        Returns:
            List of absolute URLs
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract all links
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Skip empty links and javascript/mailto links
            if not href or href.startswith(('javascript:', 'mailto:', 'tel:')):
                continue
                
            # Convert relative URLs to absolute
            if not href.startswith(('http://', 'https://')):
                # Handle relative URLs
                base = base_url.rstrip('/')
                if href.startswith('/'):
                    # Absolute path
                    parsed_url = urlparse(base_url)
                    href = f"{parsed_url.scheme}://{parsed_url.netloc}{href}"
                else:
                    # Relative path
                    href = f"{base}/{href}"
                    
            links.append(href)
            
        # Remove duplicates while preserving order
        unique_links = []
        for link in links:
            if link not in unique_links:
                unique_links.append(link)
                
        return unique_links
    
    def _get_next_user_agent(self) -> str:
        """Get the next user agent from the rotation.
        
        Returns:
            User agent string
        """
        agent = self.user_agents[self.user_agent_index]
        self.user_agent_index = (self.user_agent_index + 1) % len(self.user_agents)
        return agent
    
    def _apply_rate_limit(self) -> None:
        """Apply rate limiting to avoid overloading servers."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        # If we've made a request too recently, sleep for the remaining time
        if time_since_last_request < 1.0 / self.rate_limit:
            sleep_time = (1.0 / self.rate_limit) - time_since_last_request
            time.sleep(sleep_time)
            
        self.last_request_time = time.time() 