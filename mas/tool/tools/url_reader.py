from mas.tool.pool import ToolPool
from dataclasses import dataclass, field
from typing import List, Any
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


@ToolPool.register(
    name="read_url_html",
    description="extract main html content from url, return: main html content from the website, not including headers and footers."
)
def read_url(url: str) -> str:
    return Reader().read(url)




@dataclass
class Document:
    """Simple document structure for storing content"""
    name: str
    content: str

@dataclass
class Reader:
    """Class for reading and extracting main content from websites"""
    chunk: bool = False  # Changed default to False
    chunk_size: int = 1000

    def read(self, url: str) -> List[Document]:
        """Extract main content from a website URL"""
        # Fetch the webpage
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'header', 'footer', 'nav']):
            element.decompose()
        
        # Extract main content (focus on common content tags)
        main_content = soup.find('main') or soup.find('article') or soup.body
        if not main_content:
            main_content = soup  # Fallback to full page if no main content found
        
        # Get clean text, preserving paragraphs
        paragraphs = main_content.find_all(['p', 'h1', 'h2', 'h3', 'li'])
        text_content = "\n\n".join(
            para.get_text(strip=True) for para in paragraphs if para.get_text(strip=True)
        ) or main_content.get_text(strip=True)
        
        # Create document name from URL
        parsed_url = urlparse(url)
        doc_name = parsed_url.path.strip("/").replace("/", "_") or parsed_url.netloc
        
        # Create single document
        document = Document(
            name=doc_name,
            content=text_content.strip()
        )
        
        # Return chunked or single document
        if self.chunk:
            return self._chunk_document(document)
        return [document]

    def _chunk_document(self, document: Document) -> List[Document]:
        """Split document into chunks if needed"""
        if len(document.content) <= self.chunk_size:
            return [document]
        
        chunks = []
        start = 0
        idx = 0
        while start < len(document.content):
            end = start + self.chunk_size
            if end < len(document.content):
                while end > start and document.content[end] not in " \n":
                    end -= 1
                if end == start:
                    end = start + self.chunk_size  # Force cut if no break found
            chunk_text = document.content[start:end].strip()
            if chunk_text:
                chunks.append(Document(
                    name=f"{document.name}_{idx}",
                    content=chunk_text
                ))
            start = end + 1
            idx += 1
        return chunks

    async def async_read(self, url: str) -> List[Document]:
        """Async version of read (requires aiohttp)"""
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                for element in soup(['script', 'style', 'header', 'footer', 'nav']):
                    element.decompose()
                
                main_content = soup.find('main') or soup.find('article') or soup.body
                if not main_content:
                    main_content = soup
                
                paragraphs = main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li'])
                text_content = "\n\n".join(
                    para.get_text(strip=True) for para in paragraphs if para.get_text(strip=True)
                ) or main_content.get_text(strip=True)
                
                parsed_url = urlparse(url)
                doc_name = parsed_url.path.strip("/").replace("/", "_") or parsed_url.netloc
                
                document = Document(
                    name=doc_name,
                    content=text_content.strip()
                )
                
                if self.chunk:
                    return self._chunk_document(document)
                return [document]