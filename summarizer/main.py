import os
import sys
import requests
from bs4 import BeautifulSoup
from langdetect import detect
import openai
from groq import Groq

# PDF libraries
import PyPDF2
import pdfplumber
from io import BytesIO

def extract_text_from_pdf(file_path):
    """
    Extract text from PDF using multiple methods for better reliability.
    Tries pdfplumber first (best for most PDFs), then falls back to PyPDF2.
    """
    text = ""
    
    # Method 1: Try pdfplumber (best for complex PDFs)
    try:
        print("Attempting PDF extraction with pdfplumber...")
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    print(f"  ✓ Extracted {len(page_text)} chars from page {page_num}")
        
        if len(text.strip()) > 100:
            print(f"✓ pdfplumber extracted {len(text)} characters")
            return text.strip()
    except Exception as e:
        print(f"pdfplumber failed: {e}")
    
    # Method 2:
    try:
        print("Attempting PDF extraction with PyPDF2...")
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "
"
                    print(f"  ✓ Extracted {len(page_text)} chars from page {page_num}")
        
        if len(text.strip()) > 100:
            print(f"✓ PyPDF2 extracted {len(text)} characters")
            return text.strip()
    except Exception as e:
        print(f"PyPDF2 failed: {e}")
    
    # If both methods fail
    if len(text.strip()) < 100:
        raise Exception( extraction failed or insufficient content. "
            f"Extracted only {len(text)} characters. "
            f"The PDF might be image-based (scanned) and require OCR."
        )
    
    return text.strip()


def extract_text_from_url(url):
    """Extract text from a web URL."""
    try:
        print(f"Processing URL: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        text = soup.get_text(separator='
', strip=True)
        print(f"Extracted {len(text)} characters from URL")
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from URL: {e}")


def summarize_with_openai(text, api_key):
    """Summarize text using OpenAI."""
    try:
        print("Attempting summarization using OpenAI...")
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise, business-friendly summaries with key bullet points."},
                {"role": "user", "content": f"Summarize the following content into 10 key business-friendly bullet points:

{text[:4000]}"}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        summary = response.choices[0].message.content
        print("Summary generated using OpenAI")
        return summary
    except Exception as e:
        print(f"OpenAI failed: {e}")
        raise


def summarize_with_groq(text, api_key):
    """Summarize text using Groq as fallback."""
    try:
        print("Attempting summarization using Groq fallback...")
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise, business-friendly summaries with key bullet points."},
                {"role": "user", "content": f"Summarize the following content into 10 key business-friendly bullet points:

{text[:4000]}"}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        summary = response.choices[0].message.content
        print("Summary generated using Groq")
        return summary
    except Exception as e:
        print(f"Groq failed: {e}")
        raise


def main():
    # Get inputs
    web_url = os.getenv("WEB_URL")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    print(f"DEBUG → WEB_URL: {web_url}")
    print(f"DEBUG → FILE EXISTS: {os.path.exists('input_file')}")
    
    # Determine source
    if os.path.exists("input_file"):
        print("Processing file...")
        
        # Check if it's a PDF
        with open("input_file", "rb") as f:
            header = f.read(4)
            is_pdf = header == b'%PDF'
        
        if is_pdf:
            print("Detected PDF file")
            text = extract_text_from_pdf("input_file")
        else:
            print("Detected text file")
            with open("input_file", "r", encoding="utf-8") as f:
                text = f.read()
    
    elif web_url and web_url.strip():
        text = extract_text_from_url(web_url)
    
    else:
        raise Exception("No valid input provided (neither file nor URL)")
    
    # Validate extracted content
    if len(text) < 100:
        raise Exception(f"Insufficient content extracted. Got {len(text)} characters.")
    
    print(f"✓ Successfully extracted {len(text)} characters")
    
    # Detect language
    try:
        lang = detect(text[:1000])
        print(f"Detected language: {lang}")
    except:
        lang = "en"
    
    # Summarize
    summary = None
    
    if openai_api_key:
        try:
            summary = summarize_with_openai(text, openai_api_key)
        except Exception as e:
            print(f"OpenAI summarization failed: {e}")
    
    if not summary and groq_api_key:
        try:
            summary = summarize_with_groq(text, groq_api_key)
        except Exception as e:
            print(f"Groq summarization failed: {e}")
    
    if not summary:
        raise Exception("All summarization methods failed")
    
    # Format output
    output = f"""### 📄 Key Insights

{summary}

---

### 🌍 Language Info
Detected: {lang}
Output: English

---

### ⏱ Generated via AI Automation
"""
    
    # Save to file
    with open("summary.txt", "w", encoding="utf-8") as f:
        f.write(output)
    
    print("\n" + "="*50)
    print(output)
    print("="*50)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"
❌ ERROR: {e}", file=sys.stderr)
        sys.exit(1)
