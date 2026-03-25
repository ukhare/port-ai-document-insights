import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import docx

def extract_from_url(url):
    """Extract text from a web URL with better content detection"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    res = requests.get(url, timeout=10, headers=headers)
    res.raise_for_status()
    
    soup = BeautifulSoupparser")
    
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()
    
    # Try multiple strategies to get content
    text = ""
    
    # Strategy 1: Look for main content areas
    main_content = soup.find('main') or soup.find('article') or soup.find(id='content')
    if main_content:
        paragraphs = main_content.find_all(['p', 'h1', 'h2', 'h3', 'li'])
        text = " ".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
    
    # Strategy 2: Fallback to all paragraphs
    if not text or len(text) < 100:
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
    
    # Strategy 3: Get all text as last resort
    if not text or len(text) < 100:
        text = soup.get_text(separator=' ', strip=True)
    
    print(f"Extracted {len(text)} characters from URL")
    return text

def extract_from_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    print(f"Extracted {len(text)} characters from PDF")
    return text

def extract_from_docx(path):
    doc = docx.Document(path)
    text = " ".join([p.text for p in doc.paragraphs])
    print(f"Extracted {len(text)} characters from DOCX")
    return text
