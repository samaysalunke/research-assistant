"""
Simple Web Scraping Service
Basic web scraping using only requests and BeautifulSoup
"""

import asyncio
import re
import time
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import logging

from bs4 import BeautifulSoup
import requests

from core.config import get_settings

logger = logging.getLogger(__name__)

class SimpleWebScraper:
    """Simple web scraping service using requests and BeautifulSoup"""
    
    def __init__(self):
        self.settings = get_settings()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape content from URL using basic methods"""
        try:
            logger.info(f"Starting simple scraping for: {url}")
            
            # Use requests to get the page
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.session.get, url, 30
            )
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content
            content = self._extract_content(soup, url)
            
            logger.info(f"Successfully scraped {url}")
            return content
            
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {str(e)}")
            return {
                'text': f"Error scraping URL: {str(e)}",
                'title': 'Error',
                'url': url,
                'success': False,
                'error': str(e)
            }
    
    def _extract_content(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract content from BeautifulSoup object"""
        try:
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract title
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
            
            # Extract main content
            text = ""
            
            # Try to find main content areas
            main_selectors = [
                'main',
                'article',
                '.content',
                '.main-content',
                '#content',
                '#main',
                '.post-content',
                '.entry-content'
            ]
            
            for selector in main_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    text = main_content.get_text(separator=' ', strip=True)
                    break
            
            # If no main content found, use body
            if not text:
                body = soup.find('body')
                if body:
                    text = body.get_text(separator=' ', strip=True)
            
            # Clean up text
            text = self._clean_text(text)
            
            return {
                'text': text,
                'title': title,
                'url': url,
                'success': True,
                'content_type': 'web_page',
                'word_count': len(text.split()),
                'language': 'en'  # Default to English
            }
            
        except Exception as e:
            logger.error(f"Error extracting content: {str(e)}")
            return {
                'text': f"Error extracting content: {str(e)}",
                'title': 'Error',
                'url': url,
                'success': False,
                'error': str(e)
            }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text.strip()
