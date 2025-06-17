#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Academic scraper module for extracting content from academic sources.
"""

import logging
import asyncio
import time
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

# Academic libraries
import arxiv
from scholarly import scholarly, ProxyGenerator
import bibtexparser

logger = logging.getLogger(__name__)


class AcademicScraper:
    """Scraper for extracting content from academic sources."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the academic scraper.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Configure scholarly proxy if available
        try:
            pg = ProxyGenerator()
            if pg.FreeProxies():
                scholarly.use_proxy(pg)
                logger.info("Scholarly proxy configured")
        except Exception as e:
            logger.warning(f"Could not configure scholarly proxy: {e}")
        
        # Rate limiting
        self.rate_limit = config.get('academic_scraper', {}).get('rate_limit', 2)  # requests per second
        self.last_request_time = 0
        
        logger.info("Academic scraper initialized")
    
    async def scrape(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape academic content.
        
        Args:
            task_data: Task data containing scraping parameters
            
        Returns:
            Scraped academic content
        """
        source = task_data.get('source', 'arxiv')
        query = task_data.get('query')
        paper_id = task_data.get('paper_id')
        author = task_data.get('author')
        max_results = task_data.get('max_results', 10)
        include_abstract = task_data.get('include_abstract', True)
        include_full_text = task_data.get('include_full_text', False)
        
        if not query and not paper_id and not author:
            raise ValueError("Query, paper_id, or author is required")
        
        logger.info(f"Scraping academic content from {source}")
        
        # Apply rate limiting
        self._apply_rate_limit()
        
        if source.lower() == 'arxiv':
            return await self._scrape_arxiv(query, paper_id, max_results, include_abstract, include_full_text)
        elif source.lower() == 'google_scholar':
            return await self._scrape_google_scholar(query, author, max_results, include_abstract)
        elif source.lower() == 'bibtex':
            return await self._parse_bibtex(task_data.get('bibtex_content', ''))
        else:
            raise ValueError(f"Unsupported academic source: {source}")
    
    async def _scrape_arxiv(
        self, 
        query: Optional[str], 
        paper_id: Optional[str], 
        max_results: int, 
        include_abstract: bool,
        include_full_text: bool
    ) -> Dict[str, Any]:
        """Scrape papers from arXiv.
        
        Args:
            query: Search query
            paper_id: Specific paper ID
            max_results: Maximum number of results
            include_abstract: Whether to include abstracts
            include_full_text: Whether to download full text PDFs
            
        Returns:
            Scraped arXiv content
        """
        papers = []
        
        try:
            if paper_id:
                # Search for specific paper
                search = arxiv.Search(id_list=[paper_id])
            else:
                # Search by query
                search = arxiv.Search(
                    query=query,
                    max_results=max_results,
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending
                )
            
            for paper in search.results():
                paper_data = {
                    "id": paper.entry_id,
                    "arxiv_id": paper.get_short_id(),
                    "title": paper.title,
                    "authors": [author.name for author in paper.authors],
                    "published": paper.published.isoformat() if paper.published else None,
                    "updated": paper.updated.isoformat() if paper.updated else None,
                    "categories": paper.categories,
                    "primary_category": paper.primary_category,
                    "links": {
                        "abstract": paper.entry_id,
                        "pdf": paper.pdf_url
                    },
                    "journal_ref": paper.journal_ref,
                    "doi": paper.doi,
                    "comment": paper.comment
                }
                
                if include_abstract:
                    paper_data["abstract"] = paper.summary
                
                if include_full_text:
                    try:
                        # Download and extract PDF content
                        pdf_content = await self._download_and_extract_pdf(paper.pdf_url)
                        paper_data["full_text"] = pdf_content
                    except Exception as e:
                        logger.warning(f"Could not extract full text for {paper.get_short_id()}: {e}")
                        paper_data["full_text"] = None
                
                papers.append(paper_data)
        
        except Exception as e:
            logger.error(f"Error scraping arXiv: {e}")
            raise
        
        return {
            "source": "arxiv",
            "query": query,
            "paper_id": paper_id,
            "count": len(papers),
            "papers": papers
        }
    
    async def _scrape_google_scholar(
        self, 
        query: Optional[str], 
        author: Optional[str], 
        max_results: int,
        include_abstract: bool
    ) -> Dict[str, Any]:
        """Scrape papers from Google Scholar.
        
        Args:
            query: Search query
            author: Author name
            max_results: Maximum number of results
            include_abstract: Whether to include abstracts
            
        Returns:
            Scraped Google Scholar content
        """
        papers = []
        
        try:
            if author:
                # Search for author
                search_query = scholarly.search_author(author)
                author_info = next(search_query, None)
                
                if author_info:
                    author_info = scholarly.fill(author_info)
                    
                    # Get publications
                    for i, pub in enumerate(author_info['publications']):
                        if i >= max_results:
                            break
                        
                        try:
                            pub_filled = scholarly.fill(pub)
                            
                            paper_data = {
                                "title": pub_filled.get('title', ''),
                                "authors": pub_filled.get('author', '').split(' and ') if pub_filled.get('author') else [],
                                "year": pub_filled.get('year'),
                                "venue": pub_filled.get('venue', ''),
                                "citations": pub_filled.get('num_citations', 0),
                                "url": pub_filled.get('pub_url', ''),
                                "scholar_id": pub_filled.get('author_pub_id', ''),
                                "bibtex": pub_filled.get('bibtex', '')
                            }
                            
                            if include_abstract:
                                paper_data["abstract"] = pub_filled.get('abstract', '')
                            
                            papers.append(paper_data)
                            
                            # Rate limiting for Google Scholar
                            await asyncio.sleep(1)
                            
                        except Exception as e:
                            logger.warning(f"Error processing publication: {e}")
            
            elif query:
                # Search by query
                search_query = scholarly.search_pubs(query)
                
                for i, pub in enumerate(search_query):
                    if i >= max_results:
                        break
                    
                    try:
                        pub_filled = scholarly.fill(pub)
                        
                        paper_data = {
                            "title": pub_filled.get('title', ''),
                            "authors": pub_filled.get('author', '').split(' and ') if pub_filled.get('author') else [],
                            "year": pub_filled.get('year'),
                            "venue": pub_filled.get('venue', ''),
                            "citations": pub_filled.get('num_citations', 0),
                            "url": pub_filled.get('pub_url', ''),
                            "scholar_id": pub_filled.get('author_pub_id', ''),
                            "bibtex": pub_filled.get('bibtex', '')
                        }
                        
                        if include_abstract:
                            paper_data["abstract"] = pub_filled.get('abstract', '')
                        
                        papers.append(paper_data)
                        
                        # Rate limiting for Google Scholar
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        logger.warning(f"Error processing publication: {e}")
        
        except Exception as e:
            logger.error(f"Error scraping Google Scholar: {e}")
            raise
        
        return {
            "source": "google_scholar",
            "query": query,
            "author": author,
            "count": len(papers),
            "papers": papers
        }
    
    async def _parse_bibtex(self, bibtex_content: str) -> Dict[str, Any]:
        """Parse BibTeX content.
        
        Args:
            bibtex_content: BibTeX content string
            
        Returns:
            Parsed BibTeX data
        """
        papers = []
        
        try:
            bib_database = bibtexparser.loads(bibtex_content)
            
            for entry in bib_database.entries:
                paper_data = {
                    "id": entry.get('ID', ''),
                    "type": entry.get('ENTRYTYPE', ''),
                    "title": entry.get('title', ''),
                    "authors": self._parse_authors(entry.get('author', '')),
                    "year": entry.get('year', ''),
                    "journal": entry.get('journal', ''),
                    "booktitle": entry.get('booktitle', ''),
                    "volume": entry.get('volume', ''),
                    "number": entry.get('number', ''),
                    "pages": entry.get('pages', ''),
                    "publisher": entry.get('publisher', ''),
                    "doi": entry.get('doi', ''),
                    "url": entry.get('url', ''),
                    "abstract": entry.get('abstract', ''),
                    "keywords": entry.get('keywords', '').split(',') if entry.get('keywords') else []
                }
                
                papers.append(paper_data)
        
        except Exception as e:
            logger.error(f"Error parsing BibTeX: {e}")
            raise
        
        return {
            "source": "bibtex",
            "count": len(papers),
            "papers": papers
        }
    
    async def _download_and_extract_pdf(self, pdf_url: str) -> Optional[str]:
        """Download and extract text from PDF.
        
        Args:
            pdf_url: URL of the PDF
            
        Returns:
            Extracted text content or None
        """
        try:
            # Use the PDF scraper to extract content
            from agents.scraper.pdf_scraper import PDFScraper
            
            pdf_scraper = PDFScraper(self.config)
            result = await pdf_scraper.scrape({
                'url': pdf_url,
                'extract_images': False,
                'extract_tables': False,
                'extract_metadata': False
            })
            
            return result.get('content', '')
        
        except Exception as e:
            logger.warning(f"Error extracting PDF content: {e}")
            return None
    
    def _parse_authors(self, author_string: str) -> List[str]:
        """Parse author string into list of individual authors.
        
        Args:
            author_string: String containing author names
            
        Returns:
            List of author names
        """
        if not author_string:
            return []
        
        # Handle common BibTeX author separators
        authors = re.split(r'\s+and\s+|\s*,\s*', author_string)
        
        # Clean up author names
        cleaned_authors = []
        for author in authors:
            author = author.strip()
            if author:
                # Remove curly braces common in BibTeX
                author = re.sub(r'[{}]', '', author)
                cleaned_authors.append(author)
        
        return cleaned_authors
    
    def _apply_rate_limit(self) -> None:
        """Apply rate limiting to avoid overwhelming academic APIs."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < (1.0 / self.rate_limit):
            sleep_time = (1.0 / self.rate_limit) - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time() 