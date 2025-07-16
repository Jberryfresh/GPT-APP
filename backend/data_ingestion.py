"""
Data Ingestion and Preprocessing Module
======================================

This module handles various data sources and formats for training custom GPT models.
Supports text files, PDFs, web scraping, and structured data formats.

Author: Manus AI
Date: June 16, 2025
"""

import os
import json
import requests
import pandas as pd
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import logging
from dataclasses import dataclass
import mimetypes
import chardet
from urllib.parse import urljoin, urlparse
import time
import hashlib

# PDF processing
try:
    import PyPDF2
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PDF processing libraries not available. Install PyPDF2 and pdfplumber for PDF support.")

# Web scraping
try:
    from bs4 import BeautifulSoup
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False
    logging.warning("BeautifulSoup not available. Install beautifulsoup4 for web scraping support.")

logger = logging.getLogger(__name__)

@dataclass
class IngestionConfig:
    """Configuration for data ingestion."""
    supported_formats: List[str] = None
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    encoding_detection: bool = True
    web_scraping_delay: float = 1.0  # Delay between requests
    chunk_size: int = 8192  # For streaming downloads
    timeout: int = 30  # Request timeout
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ['.txt', '.md', '.json', '.csv', '.pdf', '.html']

class DataIngestionError(Exception):
    """Custom exception for data ingestion errors."""
    pass

class FileProcessor:
    """Handles processing of various file formats."""
    
    def __init__(self, config: IngestionConfig):
        self.config = config
        
    def detect_encoding(self, file_path: str) -> str:
        """Detect file encoding."""
        if not self.config.encoding_detection:
            return 'utf-8'
            
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except Exception as e:
            logger.warning(f"Encoding detection failed for {file_path}: {e}")
            return 'utf-8'
    
    def process_text_file(self, file_path: str) -> str:
        """Process plain text files."""
        encoding = self.detect_encoding(file_path)
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return content
        except UnicodeDecodeError:
            # Fallback to utf-8 with error handling
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            logger.warning(f"Used fallback encoding for {file_path}")
            return content
    
    def process_pdf_file(self, file_path: str) -> str:
        """Process PDF files."""
        if not PDF_AVAILABLE:
            raise DataIngestionError("PDF processing libraries not available")
        
        text_content = []
        
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
        except Exception as e:
            logger.warning(f"pdfplumber failed for {file_path}: {e}")
            
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            text_content.append(text)
            except Exception as e2:
                raise DataIngestionError(f"Failed to process PDF {file_path}: {e2}")
        
        return '\n\n'.join(text_content)
    
    def process_json_file(self, file_path: str) -> str:
        """Process JSON files."""
        encoding = self.detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding) as f:
            data = json.load(f)
        
        # Convert JSON to readable text
        if isinstance(data, dict):
            text_parts = []
            for key, value in data.items():
                if isinstance(value, (str, int, float)):
                    text_parts.append(f"{key}: {value}")
                elif isinstance(value, list):
                    text_parts.append(f"{key}: {', '.join(map(str, value))}")
                else:
                    text_parts.append(f"{key}: {json.dumps(value)}")
            return '\n'.join(text_parts)
        elif isinstance(data, list):
            return '\n'.join(json.dumps(item) for item in data)
        else:
            return json.dumps(data)
    
    def process_csv_file(self, file_path: str) -> str:
        """Process CSV files."""
        try:
            df = pd.read_csv(file_path)
            # Convert DataFrame to readable text
            text_parts = []
            for _, row in df.iterrows():
                row_text = ', '.join(f"{col}: {val}" for col, val in row.items() if pd.notna(val))
                text_parts.append(row_text)
            return '\n'.join(text_parts)
        except Exception as e:
            raise DataIngestionError(f"Failed to process CSV {file_path}: {e}")
    
    def process_html_file(self, file_path: str) -> str:
        """Process HTML files."""
        if not WEB_SCRAPING_AVAILABLE:
            # Fallback to reading as text
            return self.process_text_file(file_path)
        
        encoding = self.detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding) as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a single file and return metadata with content."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise DataIngestionError(f"File not found: {file_path}")
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > self.config.max_file_size:
            raise DataIngestionError(f"File too large: {file_size} bytes > {self.config.max_file_size}")
        
        # Determine file type
        file_extension = file_path.suffix.lower()
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        # Check if format is supported
        if file_extension not in self.config.supported_formats:
            raise DataIngestionError(f"Unsupported file format: {file_extension}")
        
        # Process based on file type
        try:
            if file_extension == '.pdf':
                content = self.process_pdf_file(str(file_path))
            elif file_extension == '.json':
                content = self.process_json_file(str(file_path))
            elif file_extension == '.csv':
                content = self.process_csv_file(str(file_path))
            elif file_extension in ['.html', '.htm']:
                content = self.process_html_file(str(file_path))
            else:
                content = self.process_text_file(str(file_path))
            
            # Generate content hash for deduplication
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            return {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_size': file_size,
                'file_extension': file_extension,
                'mime_type': mime_type,
                'content': content,
                'content_length': len(content),
                'content_hash': content_hash,
                'processed_at': time.time()
            }
            
        except Exception as e:
            raise DataIngestionError(f"Failed to process {file_path}: {e}")

class WebScraper:
    """Handles web scraping for data collection."""
    
    def __init__(self, config: IngestionConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape content from a single URL."""
        if not WEB_SCRAPING_AVAILABLE:
            raise DataIngestionError("Web scraping libraries not available")
        
        try:
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title"
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup.body
            
            if main_content:
                text = main_content.get_text()
            else:
                text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Generate content hash
            content_hash = hashlib.md5(clean_text.encode()).hexdigest()
            
            return {
                'url': url,
                'title': title_text,
                'content': clean_text,
                'content_length': len(clean_text),
                'content_hash': content_hash,
                'scraped_at': time.time(),
                'status_code': response.status_code
            }
            
        except Exception as e:
            raise DataIngestionError(f"Failed to scrape {url}: {e}")
    
    def scrape_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape content from multiple URLs with rate limiting."""
        results = []
        
        for i, url in enumerate(urls):
            try:
                result = self.scrape_url(url)
                results.append(result)
                logger.info(f"Scraped {url} ({i+1}/{len(urls)})")
                
                # Rate limiting
                if i < len(urls) - 1:
                    time.sleep(self.config.web_scraping_delay)
                    
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")
                continue
        
        return results

class DataIngestionPipeline:
    """Main pipeline for data ingestion from various sources."""
    
    def __init__(self, config: IngestionConfig = None):
        self.config = config or IngestionConfig()
        self.file_processor = FileProcessor(self.config)
        self.web_scraper = WebScraper(self.config)
        self.ingested_data = []
    
    def ingest_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Ingest data from multiple files."""
        results = []
        
        for file_path in file_paths:
            try:
                result = self.file_processor.process_file(file_path)
                results.append(result)
                logger.info(f"Processed file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                continue
        
        self.ingested_data.extend(results)
        return results
    
    def ingest_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Ingest data from web URLs."""
        results = self.web_scraper.scrape_urls(urls)
        self.ingested_data.extend(results)
        return results
    
    def ingest_directory(self, directory_path: str, recursive: bool = True) -> List[Dict[str, Any]]:
        """Ingest all supported files from a directory."""
        directory = Path(directory_path)
        
        if not directory.exists():
            raise DataIngestionError(f"Directory not found: {directory_path}")
        
        # Find all supported files
        file_paths = []
        pattern = "**/*" if recursive else "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.config.supported_formats:
                file_paths.append(str(file_path))
        
        logger.info(f"Found {len(file_paths)} supported files in {directory_path}")
        return self.ingest_files(file_paths)
    
    def save_ingested_data(self, output_path: str):
        """Save ingested data to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.ingested_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(self.ingested_data)} ingested items to {output_path}")
    
    def get_content_texts(self) -> List[str]:
        """Extract just the text content from ingested data."""
        return [item['content'] for item in self.ingested_data if item.get('content')]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about ingested data."""
        if not self.ingested_data:
            return {"total_items": 0}
        
        total_items = len(self.ingested_data)
        total_content_length = sum(item.get('content_length', 0) for item in self.ingested_data)
        
        # File type distribution
        file_types = {}
        for item in self.ingested_data:
            if 'file_extension' in item:
                ext = item['file_extension']
                file_types[ext] = file_types.get(ext, 0) + 1
            elif 'url' in item:
                file_types['web'] = file_types.get('web', 0) + 1
        
        return {
            "total_items": total_items,
            "total_content_length": total_content_length,
            "average_content_length": total_content_length / total_items if total_items > 0 else 0,
            "file_type_distribution": file_types
        }

# Example usage and utility functions
def create_sample_documents(output_dir: str = "/tmp/sample_docs"):
    """Create sample documents for testing ingestion."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Sample text file
    with open(f"{output_dir}/sample.txt", "w") as f:
        f.write("""
        This is a sample text document for testing the data ingestion pipeline.
        It contains multiple paragraphs and various types of content.
        
        The ingestion system should be able to process this file and extract
        the text content for training purposes.
        """)
    
    # Sample JSON file
    sample_data = {
        "title": "Sample Data",
        "description": "This is sample structured data",
        "items": [
            {"name": "Item 1", "value": 100},
            {"name": "Item 2", "value": 200}
        ]
    }
    
    with open(f"{output_dir}/sample.json", "w") as f:
        json.dump(sample_data, f, indent=2)
    
    # Sample CSV file
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'occupation': ['Engineer', 'Designer', 'Manager']
    })
    df.to_csv(f"{output_dir}/sample.csv", index=False)
    
    # Sample HTML file
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sample HTML Document</title>
    </head>
    <body>
        <h1>Sample Content</h1>
        <p>This is a sample HTML document with structured content.</p>
        <div>
            <h2>Section 1</h2>
            <p>This section contains important information.</p>
        </div>
    </body>
    </html>
    """
    
    with open(f"{output_dir}/sample.html", "w") as f:
        f.write(html_content)
    
    return output_dir

if __name__ == "__main__":
    # Example usage
    print("Data Ingestion Pipeline")
    print("=" * 30)
    
    # Create sample documents
    sample_dir = create_sample_documents()
    print(f"Created sample documents in: {sample_dir}")
    
    # Initialize ingestion pipeline
    config = IngestionConfig(
        max_file_size=50 * 1024 * 1024,  # 50MB
        web_scraping_delay=2.0
    )
    
    pipeline = DataIngestionPipeline(config)
    
    # Ingest sample directory
    results = pipeline.ingest_directory(sample_dir)
    print(f"Ingested {len(results)} files")
    
    # Show statistics
    stats = pipeline.get_statistics()
    print(f"Statistics: {stats}")
    
    # Save results
    pipeline.save_ingested_data(f"{sample_dir}/ingestion_results.json")
    print("Ingestion completed successfully!")

