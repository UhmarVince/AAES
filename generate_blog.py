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
    linkedin_teaser: str

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

# Initialize the GenAI Client
client = genai.Client(api_key=API_KEY)
# Using the most compatible model name for the new SDK
MODEL_NAME = 'gemini-2.0-flash' 

def get_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try:
                content = f.read()
                if not content.strip():
                    return []
                return json.loads(content)
            except Exception:
                return []
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
    
    TONE: Precise, technical, authoritative, and humble. NO marketing hype. NO AI filler words.
    CONTENT: Use NSCP 2015, ACI 318 principles. Focus on PH context (Seismic, Soil, Typhoons).
    SAFETY: DO NOT mention specific code Chapter or Section numbers. Mention the Code name (e.g. NSCP 2015) only.
    
    FORMAT: ABSOLUTELY NO dashes (-) and NO asterisks (*) for formatting. Use HTML tags only (<h2>, <h3>, <ul>, <li>, <strong>).
    INTERNAL LINKING: Include at least 2 links from this list: {json.dumps(available_links)}
    LINK STYLE: Use contextual, clickable words within paragraphs.
    
    SOCIAL STYLE (linkedin_teaser): Write a professional LinkedIn post for an engineering audience. 
    STRUCTURE: 1. Hook, 2. Technical summary, 3. Link ("Read the full technical analysis here: [link]").
    RULES: No hashtags allowed. No text allowed after the link.
    
    Already covered: {history_titles}
    
    TASK: Write a new technical 1200+ word structural engineering article for the Philippine market.
    """
    
    # RETRY LOGIC for 503/429/connection errors
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': BlogData,
                }
            )
            # Ensure we return the parsed data correctly
            if not response or not response.parsed:
                raise Exception("Empty response from AI")
            return response.parsed
        except Exception as e:
            err_str = str(e).lower()
            if ("503" in err_str or "unavailable" in err_str or "429" in err_str) and attempt < 2:
                print(f"API busy or unavailable. Retrying in 20 seconds... ({attempt+1}/3)")
                time.sleep(20)
                continue
            raise e

def post_to_linkedin(data, article_url):
    if not LINKEDIN_WEBHOOK_URL:
        print("LinkedIn Webhook URL not set. Skipping social share.")
        return

    print("Triggering LinkedIn share via Webhook...")
    payload = {
        "title": data.title,
        "teaser": data.linkedin_teaser,
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
        print(f"ERROR: Template file {TEMPLATE_FILE} missing!")
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
        print(f"ERROR: Gallery file {GALLERY_FILE} missing!")
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
        if not filename:
             return
        print(f"Article page created: {filename}")
        if update_gallery(data, filename):
            print("Gallery page updated successfully.")
        
        article_url = f"{WEBSITE_URL}/{filename}"
        post_to_linkedin(data, article_url)
        
        history = get_history()
        history.append({"title": data.title, "slug": data.slug, "date": datetime.datetime.now().isoformat()})
        save_history(history)
        print(f"Success! Blog post '{data.title}' is now live.")
    except Exception as e:
        print(f"Error during generation: {e}")
        raise e

if __name__ == "__main__":
    main()
