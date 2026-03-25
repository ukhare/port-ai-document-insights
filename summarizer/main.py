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
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


def main():
    web_url = os.getenv("WEB_URL")
    file_path = "input_file"

    print("DEBUG → WEB_URL:", web_url)
    print("DEBUG → FILE EXISTS:", os.path.exists(file_path))
    
    text = ""

    if web_url:
        text = extract_from_url(web_url)

    elif os.path.exists(file_path):
        if file_path.endswith(".pdf"):
            text = extract_from_pdf(file_path)
        elif file_path.endswith(".docx"):
            text = extract_from_docx(file_path)

    if not text:
        raise Exception("No content found")

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
