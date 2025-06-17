#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF scraper module for extracting content from PDF files.
"""

import logging
import asyncio
import time
import os
import tempfile
import aiohttp
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

# PDF processing libraries
import PyPDF2
import pdfplumber
from PIL import Image
import io

logger = logging.getLogger(__name__)


class PDFScraper:
    """Scraper for extracting content from PDF files."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the PDF scraper.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.temp_dir = tempfile.mkdtemp()
        logger.info("PDF scraper initialized")
    
    async def scrape(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape content from a PDF file.
        
        Args:
            task_data: Task data containing scraping parameters
            
        Returns:
            Scraped content
        """
        url = task_data.get('url')
        file_path = task_data.get('file_path')
        extract_images = task_data.get('extract_images', False)
        extract_tables = task_data.get('extract_tables', False)
        extract_metadata = task_data.get('extract_metadata', True)
        
        if not url and not file_path:
            raise ValueError("Either URL or file_path is required")
            
        logger.info(f"Scraping PDF: {url or file_path}")
        
        # Download PDF if URL is provided
        if url:
            file_path = await self._download_pdf(url)
        
        # Extract content from PDF
        content = await self._extract_content(file_path)
        
        # Build result
        result = {
            "source": url or file_path,
            "content": content["text"],
            "pages": content["pages"]
        }
        
        if extract_metadata:
            result["metadata"] = content["metadata"]
        
        if extract_images:
            result["images"] = await self._extract_images(file_path)
        
        if extract_tables:
            result["tables"] = await self._extract_tables(file_path)
        
        # Clean up temporary file if downloaded
        if url and os.path.exists(file_path):
            os.remove(file_path)
        
        return result
    
    async def _download_pdf(self, url: str) -> str:
        """Download PDF from URL.
        
        Args:
            url: URL to download from
            
        Returns:
            Path to downloaded file
        """
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path) or "document.pdf"
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        file_path = os.path.join(self.temp_dir, filename)
        
        timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes for large PDFs
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ValueError(f"Failed to download PDF: {response.status}")
                
                with open(file_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
        
        logger.info(f"Downloaded PDF to: {file_path}")
        return file_path
    
    async def _extract_content(self, file_path: str) -> Dict[str, Any]:
        """Extract text content from PDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with extracted content
        """
        content = {
            "text": "",
            "pages": [],
            "metadata": {}
        }
        
        try:
            # Use PyPDF2 for basic text extraction and metadata
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                if pdf_reader.metadata:
                    content["metadata"] = {
                        "title": pdf_reader.metadata.get('/Title', ''),
                        "author": pdf_reader.metadata.get('/Author', ''),
                        "subject": pdf_reader.metadata.get('/Subject', ''),
                        "creator": pdf_reader.metadata.get('/Creator', ''),
                        "producer": pdf_reader.metadata.get('/Producer', ''),
                        "creation_date": str(pdf_reader.metadata.get('/CreationDate', '')),
                        "modification_date": str(pdf_reader.metadata.get('/ModDate', '')),
                        "pages": len(pdf_reader.pages)
                    }
                
                # Extract text from each page
                all_text = []
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            content["pages"].append({
                                "page_number": page_num + 1,
                                "text": page_text.strip()
                            })
                            all_text.append(page_text)
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                
                content["text"] = "\n\n".join(all_text)
            
            # If PyPDF2 extraction was poor, try pdfplumber for better text extraction
            if len(content["text"]) < 100:  # Likely poor extraction
                logger.info("Attempting enhanced text extraction with pdfplumber")
                content = await self._extract_with_pdfplumber(file_path, content)
        
        except Exception as e:
            logger.error(f"Error extracting PDF content: {e}")
            raise
        
        return content
    
    async def _extract_with_pdfplumber(self, file_path: str, existing_content: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced text extraction using pdfplumber.
        
        Args:
            file_path: Path to PDF file
            existing_content: Existing content dictionary to update
            
        Returns:
            Updated content dictionary
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                all_text = []
                pages = []
                
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            pages.append({
                                "page_number": page_num + 1,
                                "text": page_text.strip()
                            })
                            all_text.append(page_text)
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num + 1} with pdfplumber: {e}")
                
                if all_text:  # Only update if we got better results
                    existing_content["text"] = "\n\n".join(all_text)
                    existing_content["pages"] = pages
                    existing_content["metadata"]["pages"] = len(pages)
        
        except Exception as e:
            logger.warning(f"Error with pdfplumber extraction: {e}")
        
        return existing_content
    
    async def _extract_images(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract images from PDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of image information
        """
        images = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        if '/XObject' in page['/Resources']:
                            xObject = page['/Resources']['/XObject'].get_object()
                            
                            for obj in xObject:
                                if xObject[obj]['/Subtype'] == '/Image':
                                    size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                                    images.append({
                                        "page": page_num + 1,
                                        "object_name": obj,
                                        "width": size[0],
                                        "height": size[1],
                                        "colorspace": str(xObject[obj].get('/ColorSpace', 'Unknown'))
                                    })
                    except Exception as e:
                        logger.warning(f"Error extracting images from page {page_num + 1}: {e}")
        
        except Exception as e:
            logger.warning(f"Error extracting images: {e}")
        
        return images
    
    async def _extract_tables(self, file_path: str) -> List[Dict[str, Any]]:
        """Extract tables from PDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of table data
        """
        tables = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_tables = page.extract_tables()
                        
                        for table_num, table in enumerate(page_tables):
                            if table and len(table) > 1:  # Must have at least header + 1 row
                                # Clean the table data
                                clean_table = []
                                for row in table:
                                    clean_row = [cell.strip() if cell else "" for cell in row]
                                    if any(clean_row):  # Skip empty rows
                                        clean_table.append(clean_row)
                                
                                if clean_table:
                                    tables.append({
                                        "page": page_num + 1,
                                        "table_number": table_num + 1,
                                        "rows": len(clean_table),
                                        "columns": len(clean_table[0]) if clean_table else 0,
                                        "data": clean_table,
                                        "header": clean_table[0] if clean_table else []
                                    })
                    
                    except Exception as e:
                        logger.warning(f"Error extracting tables from page {page_num + 1}: {e}")
        
        except Exception as e:
            logger.warning(f"Error extracting tables: {e}")
        
        return tables
    
    def __del__(self):
        """Clean up temporary directory."""
        try:
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
        except Exception:
            pass 