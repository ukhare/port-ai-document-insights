import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import docx

def extract_from_url(url):
    res = requests.get(url, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    return " ".join([p.text for p in soup.find_all("p")])

def extract_from_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_from_docx(path):
    doc = docx.Document(path)
    return " ".join([p.text for p in doc.paragraphs])