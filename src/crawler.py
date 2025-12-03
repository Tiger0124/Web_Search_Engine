"""Web crawler module for the search engine."""

import json
import re
import time
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None


class Crawler:
    """Web crawler for collecting web pages."""
    
    def __init__(self, base_url: str, max_pages: int = 100, delay: float = 1.0):
        """
        Initialize the crawler.
        
        Args:
            base_url: The starting URL for crawling.
            max_pages: Maximum number of pages to crawl.
            delay: Delay between requests in seconds.
        """
        self.base_url = base_url
        self.max_pages = max_pages
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.crawled_data: List[Dict] = []
        
    def _get_page_content(self, url: str) -> Optional[str]:
        """
        Fetch the content of a web page.
        
        Args:
            url: The URL to fetch.
            
        Returns:
            HTML content of the page or None if failed.
        """
        if requests is None:
            return None
            
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; SearchEngineBot/1.0)'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception:
            return None
    
    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """
        Extract all links from HTML content.
        
        Args:
            html: HTML content to parse.
            base_url: Base URL for resolving relative links.
            
        Returns:
            List of absolute URLs found in the page.
        """
        if BeautifulSoup is None:
            return []
            
        links = []
        soup = BeautifulSoup(html, 'html.parser')
        
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            absolute_url = urljoin(base_url, href)
            
            # Only include URLs from the same domain
            if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                links.append(absolute_url)
        
        return links
    
    def _extract_text(self, html: str) -> Dict[str, str]:
        """
        Extract text content from HTML.
        
        Args:
            html: HTML content to parse.
            
        Returns:
            Dictionary with title and body text.
        """
        if BeautifulSoup is None:
            return {'title': '', 'body': ''}
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Extract title
        title = ''
        if soup.title:
            title = soup.title.string or ''
        
        # Extract body text
        body = soup.get_text(separator=' ', strip=True)
        
        return {'title': title, 'body': body}
    
    def crawl(self) -> List[Dict]:
        """
        Start crawling from the base URL.
        
        Returns:
            List of crawled page data.
        """
        urls_to_visit = [self.base_url]
        
        while urls_to_visit and len(self.crawled_data) < self.max_pages:
            url = urls_to_visit.pop(0)
            
            if url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            
            html = self._get_page_content(url)
            if html is None:
                continue
            
            # Extract content
            content = self._extract_text(html)
            
            # Store the crawled data
            page_data = {
                'url': url,
                'title': content['title'],
                'content': content['body']
            }
            self.crawled_data.append(page_data)
            
            # Extract and add new links
            new_links = self._extract_links(html, url)
            for link in new_links:
                if link not in self.visited_urls:
                    urls_to_visit.append(link)
            
            # Respect crawl delay
            time.sleep(self.delay)
        
        return self.crawled_data
    
    def save_data(self, filepath: str) -> None:
        """
        Save crawled data to a JSON file.
        
        Args:
            filepath: Path to save the JSON file.
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.crawled_data, f, ensure_ascii=False, indent=2)
    
    def load_data(self, filepath: str) -> List[Dict]:
        """
        Load crawled data from a JSON file.
        
        Args:
            filepath: Path to the JSON file.
            
        Returns:
            List of crawled page data.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            self.crawled_data = json.load(f)
        return self.crawled_data
