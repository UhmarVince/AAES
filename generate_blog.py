import os
import json
import datetime
import re
import requests
import time
from google import genai
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

# --- DATA MODEL ---
class BlogData(BaseModel):
    title: str
    slug: str
    category: str
    meta_description: str
    excerpt: str
    content_html: str
    linkedin_teaser_body: str # The AI only writes the technical message

# --- CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("CRITICAL ERROR: GEMINI_API_KEY not found in environment variables.")
    exit(1)

LINKEDIN_WEBHOOK_URL = os.getenv("LINKEDIN_WEBHOOK_URL") 
HISTORY_FILE = "blog_history.json"
TEMPLATE_FILE = "blog-template.html"
GALLERY_FILE = "blog.html"
WEBSITE_URL = "https://aa-engineers.net"

client = genai.Client(api_key=API_KEY)
# Using the stable 2.5-flash for 2026
MODEL_NAME = 'gemini-2.5-flash' 

def get_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try:
                content = f.read()
                if not content.strip(): return []
                return json.loads(content)
            except Exception: return []
    return []

def get_available_links():
    history = get_history()
    links = [
        {"title": "Home", "url": "index.html"},
        {"title": "Our Services", "url": "services.html"},
        {"title": "Projects Gallery", "url": "projects.html"}
    ]
    for post in history:
        links.append({"title": post['title'], "url": f"{post['slug']}.html"})
    return links

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=4)

def generate_content():
    history = get_history()
    history_titles = [post['title'] for post in history]
    available_links = get_available_links()
    
    prompt = f"""
    You are an expert Senior Structural Engineer in the Philippines. You are NOT an AI assistant.
    
    TONE: Precise, technical, authoritative and humble. NEVER use AI filler phrases.
    FORMAT: Use HTML tags only (<h2>, <h3>, <ul>, <li>, <strong>). ABSOLUTELY NO dashes (-) or asterisks (*).
    SAFETY: Mention the Code name (NSCP 2015) only. Never mention specific Section numbers.
    INTERNAL LINKING: Include at least 2 links from this list: {json.dumps(available_links)}
    
    SOCIAL TASK (linkedin_teaser_body): Write a 2-paragraph professional message for LinkedIn.
    - Paragraph 1: A technical hook about an engineering challenge.
    - Paragraph 2: Insights into the structural engineering best practices used.
    - RULES: NO hashtags. NO links. NO filenames or .html in the text. ONLY the message body.
    
    Already covered: {history_titles}
    
    TASK: Write a new technical 1200+ word structural engineering article for the Philippine market.
    """
    
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': BlogData,
                }
            )
            return response.parsed
        except Exception as e:
            if ("503" in str(e) or "429" in str(e)) and attempt < 4:
                print(f"API busy. Retrying in 15 seconds... ({attempt+1}/5)")
                time.sleep(15)
                continue
            raise e

def post_to_linkedin(data, article_url):
    if not LINKEDIN_WEBHOOK_URL:
        print("LinkedIn Webhook URL not set. Skipping social share.")
        return

    # HARD-CODED STRUCTURE: We force the link to be at the very bottom
    final_post_text = f"{data.linkedin_teaser_body}\n\nRead the full technical analysis here: {article_url}"

    print("Triggering LinkedIn share via Webhook...")
    payload = {
        "title": data.title,
        "teaser": final_post_text, # This carries our perfect structure
        "url": article_url,
        "meta_description": data.meta_description
    }
    try:
        response = requests.post(LINKEDIN_WEBHOOK_URL, json=payload)
        if response.status_code in [200, 201, 202, 204]:
            print("Successfully triggered LinkedIn automation!")
        else:
            print(f"Webhook Trigger Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Webhook Error: {e}")

def create_article_page(data):
    if not os.path.exists(TEMPLATE_FILE):
        return None
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    html = template.replace("{{TITLE}}", data.title).replace("{{METADESC}}", data.meta_description).replace("{{DATE}}", date_str).replace("{{CONTENT}}", data.content_html)
    filename = f"{data.slug}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    return filename

def update_gallery(data, filename):
    if not os.path.exists(GALLERY_FILE):
        return False
    with open(GALLERY_FILE, 'r', encoding='utf-8') as f:
        gallery_html = f.read()
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    new_card = f"""
            <!-- Auto-Generated Card: {data.title} -->
            <article class="blog-card" onclick="location.href='{filename}'">
                <div class="card-image">
                    <div class="abstract-pattern"></div>
                    <img src="logo.png" style="width: 60px; opacity: 0.5; filter: grayscale(1);">
                </div>
                <div class="card-content">
                    <span class="category-tag">{data.category}</span>
                    <h2 class="card-title">{data.title}</h2>
                    <p class="card-excerpt">{data.excerpt}</p>
                    <div class="card-footer">
                        <span>{date_str}</span>
                        <span>10 min read</span>
                    </div>
                </div>
            </article>
    """
    marker = '<div class="blog-gallery" id="blog-gallery">'
    if marker in gallery_html:
        parts = gallery_html.split(marker)
        updated_html = parts[0] + marker + new_card + parts[1]
        with open(GALLERY_FILE, 'w', encoding='utf-8') as f:
            f.write(updated_html)
        return True
    return False

def main():
    print("--- AAES Automated Blog Engine ---")
    try:
        data = generate_content()
        print(f"Topic Selected: {data.title}")
        filename = create_article_page(data)
        if not filename: return
        
        if update_gallery(data, filename):
            print("Gallery page updated successfully.")
        
        article_url = f"{WEBSITE_URL}/{filename}"
        post_to_linkedin(data, article_url)
        
        history = get_history()
        history.append({"title": data.title, "slug": data.slug, "date": datetime.datetime.now().isoformat()})
        save_history(history)
        print(f"Success! Blog post live and shared.")
    except Exception as e:
        print(f"Error: {e}")
        raise e

if __name__ == "__main__":
    main()
