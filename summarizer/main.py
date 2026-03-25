import os
from utils import extract_from_url, extract_from_pdf, extract_from_docx
from langdetect import detect
from deep_translator import GoogleTranslator
from openai import OpenAI
from groq import Groq

# Initialize AI clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


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
Summarize the following content into TOP 10 business-friendly bullet points.

Content:
{text[:6000]}
"""

    # --- Try OpenAI first ---
    try:
        print("Attempting summarization using OpenAI...")

        res = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        print("Summary generated using OpenAI")

        return res.choices[0].message.content

    except Exception as e:
        print("OpenAI failed:", str(e))

    # --- Fallback to Groq ---
    try:
        print("Attempting summarization using Groq fallback...")

        res = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ✅ supported model
            messages=[{"role": "user", "content": prompt}]
        )

        print("Summary generated using Groq")

        return res.choices[0].message.content

    except Exception as e:
        print("Groq also failed:", str(e))
        raise Exception("Both OpenAI and Groq summarization failed.")


def main():
    web_url = os.getenv("WEB_URL", "").strip()

    if web_url in ("null", "None", ""):
        web_url = None

    file_path = "input_file"

    print("DEBUG → WEB_URL:", web_url)
    print("DEBUG → FILE EXISTS:", os.path.exists(file_path))

    text = ""

    # --- File processing ---
    if os.path.exists(file_path):
        print("Processing file...")

        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)

                if header[:4] == b'%PDF':
                    print("Detected PDF file")
                    text = extract_from_pdf(file_path)

                elif header[:2] == b'PK':
                    print("Detected DOCX file")
                    text = extract_from_docx(file_path)

                else:
                    print("Unknown format, trying PDF...")
                    text = extract_from_pdf(file_path)

        except Exception as e:
            print(f"Error reading file: {e}")
            text = extract_from_pdf(file_path)

    # --- URL processing ---
    elif web_url:
        print(f"Processing URL: {web_url}")
        text = extract_from_url(web_url)

    else:
        raise ValueError("No input provided. Please provide either a web_url or file_url.")

    if not text or len(text.strip()) < 50:
        raise Exception(f"Insufficient content extracted. Got {len(text)} characters.")

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
