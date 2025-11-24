"""
Web content processor.
"""
from typing import Dict, Any, List
import aiohttp
from bs4 import BeautifulSoup
# Removed readability-lxml dependency - using BeautifulSoup directly
from app.processors.base import BaseProcessor, Chunk
import re


class WebProcessor(BaseProcessor):
    """Processor for web content."""
    
    async def process(
        self,
        url: str,
        user_id: str,
        metadata: Dict[str, Any] = None
    ) -> tuple[str, List[Chunk], Dict[str, Any]]:
        """
        Process web URL.
        Returns: (full_text, chunks, web_metadata)
        """
        # Fetch web page
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                html = await response.text()
        
        # Parse HTML directly
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script, style, nav, footer, etc.
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        
        # Get text directly from soup
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks_text = (phrase.strip() for line in lines for phrase in line.split("  "))
        full_text = '\n'.join(chunk for chunk in chunks_text if chunk)
        
        # Extract metadata
        title = soup.title.string if soup.title else "Untitled"
        
        # Try to get meta tags
        meta_desc = ""
        meta_author = ""
        meta_date = None
        
        meta_desc_tag = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "description"})
        if meta_desc_tag:
            meta_desc = meta_desc_tag.get("content", "")
        
        meta_author_tag = soup.find("meta", attrs={"name": "author"})
        if meta_author_tag:
            meta_author = meta_author_tag.get("content", "")
        
        # Try to find publish date
        date_tags = soup.find_all(["time", "meta"], attrs={"property": ["article:published_time", "published_time"]})
        if date_tags:
            meta_date = date_tags[0].get("content") or date_tags[0].get("datetime")
        
        web_metadata = {
            "source_type": "web",
            "url": url,
            "title": title,
            "description": meta_desc,
            "author": meta_author,
            "publish_date": meta_date,
            "domain": self._extract_domain(url)
        }
        if metadata:
            web_metadata.update(metadata)
        
        # Chunk content
        chunks = self.chunk_text(full_text, strategy="paragraph")
        
        # Add chunk metadata
        for chunk in chunks:
            chunk.metadata.update({
                "chunk_type": "web_content",
                "source_type": "web",
                "url": url
            })
        
        return full_text, chunks, web_metadata
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc

