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


def extract_text_from_pdf(file_path):
    """
    Extract text from PDF using multiple methods for better reliability.
    """
    text = ""
    
    # Method 1: Try pdfplumber (best for most PDFs)
    try:
        print("Attempting PDF extraction with pdfplumber...")
        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"  PDF has {total_pages} pages")
            
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "
"
                    print(f"  ✓ Page {page_num}/{total_pages}: extracted {len(page_text)} chars")
                else:
                    print(f"  ⚠ Page {page_num}/{total_pages}: no text extracted")
        
        if len(text.strip()) > 100:
            print(f"✓ pdfplumber successfully extracted {len(text)} characters")
            return text.strip()
        else:
            print(f"⚠ pdfplumber extracted insufficient text ({len(text)} chars)")
    except Exception as e:
        print(f"❌ pdfplumber failed: {e}")
    
    # Method 2: Fallback to PyPDF2
    try:
        print("
Attempting PDF extraction with PyPDF2...")
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            print(f"  PDF has {total_pages} pages")
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "
"
                    print(f"  ✓ Page {page_num}/{total_pages}: extracted {len(page_text)} chars")
                else:
                    print(f"  ⚠ Page {page_num}/{total_pages}: no text extracted")
        
        if len(text.strip()) > 100:
            print(f"✓ PyPDF2 successfully extracted {len(text)} characters")
            return text.strip()
        else:
            print(f"⚠ PyPDF2 extracted insufficient text ({len(text)} chars)")
    except Exception as e:
        print(f"❌ PyPDF2 failed: {e}")
    
    # If both methods fail
    raise Exception(
        f"PDF text extraction failed. Extracted only {len(text)} characters. "
        f"This PDF might be:\n"
        f"  • Image-based (scanned document requiring OCR)\n"
        f"  • Encrypted or password-protected
"
        f"  • Corrupted or malformed
"
        f"  • Using unsupported encoding"
    )


def extract_text_from_url(url):
    """Extract text from a web URL."""
    try:
        print(f"Processing URL: {url}")
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
        
        text = soup.get_text(separator='
', strip=True)
        print(f"✓ Extracted {len(text)} characters from URL")
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
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates concise, business-friendly summaries with key bullet points."
                },
                {
                    "role": "user",
                    "content": f"Summarize the following content into 10 key business-friendly bullet points:\n
{text[:4000]}"
                }
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        summary = response.choices[0].message.content
        print("✓ Summary generated using OpenAI")
        return summary
    except Exception as e:
        print(f"❌ OpenAI failed: {e}")
        raise


def summarize_with_groq(text, api_key):
    """Summarize text using Groq as fallback."""
    try:
        print("Attempting summarization using Groq fallback...")
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates concise, business-friendly summaries with key bullet points."
                },
                {
                    "role": "user",
                    "content": f"Summarize the following content into 10 key business-friendly bullet points:

{text[:4000]}"
                }
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        summary = response.choices[0].message.content
        print("✓ Summary generated using Groq")
        return summary
    except Exception as e:
        print(f"❌ Groq failed: {e}")
        raise


def main():
    print("="*60)
    print("AI DOCUMENT INSIGHTS - STARTING")
    print("="*60)
    
    # Get inputs
    web_url = os.getenv("WEB_URL")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    groq_api_GROQ_API_KEY")
    
    print(f"
📋 Configuration:")
    print(f"  WEB_URL: {web_url if web_url else 'Not provided'}")
    print(f"  File exists: {os.path.exists('input_file')}")
    print(f"  OpenAI API: {'✓ Configured' if openai_api_key else '✗ Not configured'}")
    print(f"  Groq API: {'✓ Configured' if groq_api_key else '✗ Not configured'}")
    print()
    
    # Determine source and extract text
    if os.path.exists("input_file"):
        print("📄 Processing file...")
        
        # Check if it's a PDF
        with open("input_file", "rb") as f:
            header = f.read(4)
            is_pdf = header == b'%PDF'
        
        if is_pdf:
            print("  Type: PDF document")
            text = extract_text_from_pdf("input_file")
        else:
            print("  Type: Text file")
            with open("input_file", "r", encoding="utf-8") as f:
                text = f.read()
            print(f"✓ Read {len(text)} characters from text file")
    
    elif web_url and web_url.strip():
        print("🌐 Processing web URL...")
        text = extract_text_from_url(web_url)
    
    else:
        raise Exception("❌ No valid input provided (neither file nor URL)")
    
    # Validate extracted content
    print(f"\n📊 Content validation:")
    print(f"  Total characters: {len(text)}")
    print(f"  Total words: {len(text.split())}")
    
    if len(text) < 100:
        raise Exception(
            f"Insufficient content extracted. Got only {len(text)} characters. "
            f"Minimum required: 100 characters."
        )
    
    print(f"  ✓ Content validation passed")
    
    # Detect language
    try:
        lang = detect(text[:1000])
        print(f"
🌍 Detected language: {lang}")
    except Exception as e:
        print(f"⚠ Language detection failed: {e}")
        lang = "en"
    
    # Summarize
    print(f"
🤖 Starting summarization...")
    summary = None
    
    if openai_api_key:
        try:
            summary = summarize_with_openai(text, openai_api_key)
        except Exception as e:
            print(f"OpenAI summarization failed, will try Groq: {e}")
    
    if not summary and groq_api_key:
        try:
            summary = summarize_with_groq(text, groq_api_key)
        except Exception as e:
            print(f"Groq summarization also failed: {e}")
    
    if not summary:
        raise Exception("❌ All summarization methods failed. Check API keys and quotas.")
    
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
    
    print("
" + "="*60)
    print("✅ SUMMARY GENERATED SUCCESSFULLY")
    print("="*60)
    print(output)
    print("="*60)
    print(f"
💾 Summary saved to: summary.txt")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"
{'='*60}")
        print(f"❌ ERROR: {e}")
        print(f"{'='*60}
")
        sys.exit(1)
            
