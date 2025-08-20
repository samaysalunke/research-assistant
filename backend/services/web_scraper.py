"""
Enhanced Web Scraping Service
Uses Playwright for dynamic content and newspaper3k for content extraction
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
import logging

# Try to import optional dependencies
try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Playwright not available, using fallback scraping methods")

try:
    from newspaper import Article, Config
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Newspaper3k not available, using fallback scraping methods")

from bs4 import BeautifulSoup
import requests

from core.config import get_settings

logger = logging.getLogger(__name__)

class EnhancedWebScraper:
    """Enhanced web scraping service with Playwright and newspaper3k"""
    
    def __init__(self):
        self.settings = get_settings()
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        if PLAYWRIGHT_AVAILABLE:
            await self._init_browser()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._cleanup()
        
    async def _init_browser(self):
        """Initialize Playwright browser"""
        if not PLAYWRIGHT_AVAILABLE:
            return
            
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            self.page = await self.browser.new_page()
            
            # Set user agent
            await self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            logger.info("Playwright browser initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Playwright browser: {str(e)}")
            raise
            
    async def _cleanup(self):
        """Clean up browser resources"""
        if not PLAYWRIGHT_AVAILABLE:
            return
            
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            logger.info("Playwright browser cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape content from URL using enhanced methods"""
        try:
            logger.info(f"Starting enhanced scraping for: {url}")
            
            # Try newspaper3k first (better for articles)
            if NEWSPAPER_AVAILABLE and self._is_article_url(url):
                content = await self._scrape_with_newspaper(url)
                if content and content.get('text'):
                    logger.info("Successfully scraped with newspaper3k")
                    return content
                    
            # Fallback to Playwright for dynamic content
            if PLAYWRIGHT_AVAILABLE:
                content = await self._scrape_with_playwright(url)
                if content and content.get('text'):
                    logger.info("Successfully scraped with Playwright")
                    return content
                
            # Final fallback to basic requests
            content = await self._scrape_with_requests(url)
            logger.info("Used basic requests fallback")
            return content
            
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {str(e)}")
            raise Exception(f"Failed to scrape URL: {str(e)}")
            
    def _is_article_url(self, url: str) -> bool:
        """Check if URL is likely an article"""
        article_domains = [
            'medium.com', 'dev.to', 'hashnode.dev', 'blog.', 'news.',
            'techcrunch.com', 'wired.com', 'arstechnica.com', 'github.com',
            'stackoverflow.com', 'reddit.com', 'hackernews.com'
        ]
        
        domain = urlparse(url).netloc.lower()
        return any(article_domain in domain for article_domain in article_domains)
        
    async def _scrape_with_newspaper(self, url: str) -> Dict[str, Any]:
        """Scrape using newspaper3k library"""
        if not NEWSPAPER_AVAILABLE:
            return {}
            
        try:
            config = Config()
            config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            config.request_timeout = 10
            config.fetch_images = False
            
            article = Article(url, config=config)
            article.download()
            article.parse()
            
            if article.text:
                return {
                    'text': article.text,
                    'title': article.title,
                    'authors': article.authors,
                    'publish_date': article.publish_date.isoformat() if article.publish_date else None,
                    'top_image': article.top_image,
                    'meta_description': article.meta_description,
                    'meta_keywords': article.meta_keywords,
                    'canonical_link': article.canonical_link,
                    'method': 'newspaper3k'
                }
                
        except Exception as e:
            logger.warning(f"Newspaper3k failed for {url}: {str(e)}")
            
        return {}
        
    async def _scrape_with_playwright(self, url: str) -> Dict[str, Any]:
        """Scrape using Playwright for dynamic content"""
        if not PLAYWRIGHT_AVAILABLE:
            return {}
            
        try:
            # Navigate to page
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for content to load
            await asyncio.sleep(2)
            
            # Scroll to load lazy content
            await self._scroll_page()
            
            # Extract content
            content = await self._extract_content_from_page()
            
            return {
                'text': content.get('text', ''),
                'title': content.get('title', ''),
                'method': 'playwright'
            }
            
        except Exception as e:
            logger.warning(f"Playwright failed for {url}: {str(e)}")
            
        return {}
        
    async def _scroll_page(self):
        """Scroll page to load lazy content"""
        if not PLAYWRIGHT_AVAILABLE:
            return
            
        try:
            # Scroll to bottom
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)
            
            # Scroll back to top
            await self.page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.warning(f"Error during page scrolling: {str(e)}")
            
    async def _extract_content_from_page(self) -> Dict[str, str]:
        """Extract content from Playwright page"""
        if not PLAYWRIGHT_AVAILABLE:
            return {'text': '', 'title': ''}
            
        try:
            # Extract title
            title = await self.page.title()
            
            # Extract main content using various selectors
            content_selectors = [
                'article',
                '[role="main"]',
                '.content',
                '.post-content',
                '.entry-content',
                '.article-content',
                'main',
                '.main-content'
            ]
            
            text_content = ""
            
            for selector in content_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        text = await element.inner_text()
                        if len(text) > len(text_content):
                            text_content = text
                except:
                    continue
                    
            # If no specific content found, get body text
            if not text_content:
                text_content = await self.page.inner_text('body')
                
            # Clean the text
            text_content = self._clean_text(text_content)
            
            return {
                'text': text_content,
                'title': title
            }
            
        except Exception as e:
            logger.error(f"Error extracting content: {str(e)}")
            return {'text': '', 'title': ''}
            
    async def _scrape_with_requests(self, url: str) -> Dict[str, Any]:
        """Fallback scraping using requests and BeautifulSoup"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
                
            # Extract title
            title = soup.title.string if soup.title else ''
            
            # Extract text
            text = soup.get_text()
            text = self._clean_text(text)
            
            return {
                'text': text,
                'title': title,
                'method': 'requests'
            }
            
        except Exception as e:
            logger.error(f"Requests fallback failed: {str(e)}")
            return {'text': '', 'title': '', 'method': 'requests'}
            
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
            
        # Remove extra whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Remove common unwanted patterns
        unwanted_patterns = [
            r'Cookie Policy',
            r'Privacy Policy',
            r'Terms of Service',
            r'Subscribe',
            r'Newsletter',
            r'Follow us',
            r'Share this',
            r'Related articles',
            r'Advertisement',
            r'Advertise',
            r'© \d{4}',
            r'All rights reserved'
        ]
        
        import re
        for pattern in unwanted_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
        # Clean up extra whitespace again
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
        
    async def get_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from URL"""
        try:
            async with EnhancedWebScraper() as scraper:
                content = await scraper.scrape_url(url)
                
                return {
                    'url': url,
                    'title': content.get('title', ''),
                    'text_length': len(content.get('text', '')),
                    'method_used': content.get('method', 'unknown'),
                    'has_content': bool(content.get('text')),
                    'estimated_reading_time': self._estimate_reading_time(content.get('text', '')),
                    'content_type': self._detect_content_type(url, content.get('text', ''))
                }
                
        except Exception as e:
            logger.error(f"Failed to get metadata for {url}: {str(e)}")
            return {
                'url': url,
                'error': str(e),
                'has_content': False
            }
            
    def _estimate_reading_time(self, text: str) -> int:
        """Estimate reading time in minutes"""
        if not text:
            return 0
            
        # Average reading speed: 200-250 words per minute
        word_count = len(text.split())
        return max(1, word_count // 225)
        
    def _detect_content_type(self, url: str, text: str) -> str:
        """Detect content type"""
        url_lower = url.lower()
        text_lower = text.lower()
        
        if any(keyword in url_lower for keyword in ['blog', 'article', 'post']):
            return 'article'
        elif any(keyword in url_lower for keyword in ['docs', 'documentation', 'guide']):
            return 'documentation'
        elif any(keyword in url_lower for keyword in ['news', 'report']):
            return 'news'
        elif len(text) > 5000:
            return 'long-form'
        else:
            return 'general'
