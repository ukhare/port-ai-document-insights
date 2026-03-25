import os
from utils import extract_from_url, extract_from_pdf, extract_from_docx
from langdetect import detect
from deep_translator import GoogleTranslator
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def translate_if_needed(text):
    try:
        lang = detect(text)
    except:
        lang = "unknown"

    if lang != "en":
        translated = GoogleTranslator(source='auto', target='en').translate(text[:4000])
        return translated, lang
    return text, lang

def summarize(text):
    prompt = f"""
Summarize into top 10 business-friendly bullet points.

Content:
{text[:6000]}
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


def main():
    # Get and clean web_url
    web_url = os.getenv("WEB_URL", "").strip()
    
    # Handle "null" string and empty values
    if web_url in ("null", "None", ""):
        web_url = None
    
    file_path = "input_file"

    print("DEBUG → WEB_URL:", web_url)
    print("DEBUG → FILE EXISTS:", os.path.exists(file_path))
    
    text = ""

    # Check file first (file_url takes precedence)
    if os.path.exists(file_path):
        print("Processing file...")
        # Detect file type by reading first bytes or use a default
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header[:4] == b'%PDF':
                    print("Detected PDF file")
                    text = extract_from_pdf(file_path)
                elif header[:2] == b'PK':  # DOCX is a ZIP file
                    print("Detected DOCX file")
                    text = extract_from_docx(file_path)
                else:
                    # Try PDF as default
                    print("Unknown format, trying PDF...")
                    text = extract_from_pdf(file_path)
        except Exception as e:
            print(f"Error reading file: {e}")
            # Fallback to PDF
            text = extract_from_pdf(file_path)
    
    elif web_url:
        print(f"Processing URL: {web_url}")
        text = extract_from_url(web_url)
    
    else:
        raise ValueError("No input provided. Please provide either a web_url or file_url.")

    if not text or len(text.strip()) < 50:
        raise Exception(f"Insufficient content extracted from input. Got {len(text)} characters.")

    translated_text, lang = translate_if_needed(text)

    summary = summarize(translated_text)

    output = f"""
### 📄 Key Insights

{summary}

---

### 🌍 Language Info
Detected: {lang}
Output: English

---

### ⏱ Generated via AI Automation
"""

    with open("summary.txt", "w") as f:
        f.write(output)

    print(output)


if __name__ == "__main__":
    main()
