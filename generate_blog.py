import os
import json
import datetime
import requests
import time
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv

# --- DATA MODEL ---
class BlogData(BaseModel):
    title: str
    slug: str
    category: str
    meta_description: str
    excerpt: str
    content_html: str
    linkedin_teaser_body: str 

# --- CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
LINKEDIN_WEBHOOK_URL = os.getenv("LINKEDIN_WEBHOOK_URL") 
HISTORY_FILE = "blog_history.json"
TEMPLATE_FILE = "blog-template.html"
GALLERY_FILE = "blog.html"
WEBSITE_URL = "https://aa-engineers.net"

# Initialize Client
client = genai.Client(api_key=API_KEY)
# Using the current 2026 standard model
MODEL_NAME = 'gemini-2.5-flash' 

def get_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return []
    return []

def generate_content():
    history = get_history()
    history_titles = [post['title'] for post in history]
    
    # DIAGNOSTIC: List models if we hit a 404
    try:
        prompt = f"""
        You are a humble Philippine Structural Engineer. Use contextual links: index.html, services.html.
        TONE: Quietly technical, humble, and direct. NO titles (Senior/Expert).
        FORMAT: HTML only. NO dashes (-) or asterisks (*). 
        SOCIAL TASK (linkedin_teaser_body): Write 2 short, humble technical paragraphs. 
        RULES: NO hashtags. NO links. NO titles. Just body text.
        Already covered: {history_titles}
        """

        # RETRY LOGIC for busy server
        for attempt in range(5):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME, contents=prompt,
                    config={'response_mime_type': 'application/json', 'response_schema': BlogData}
                )
                if response and response.parsed:
                    return response.parsed
                time.sleep(10)
            except Exception as e:
                err_msg = str(e).lower()
                if "404" in err_msg:
                    print("Model 404 Detected. Available models for your account:")
                    for m in client.models.list(): print(f" - {m.name}")
                    raise e
                if ("503" in err_msg or "429" in err_msg) and attempt < 4:
                    print(f"API Busy. Retrying in 15s... ({attempt+1}/5)")
                    time.sleep(15); continue
                raise e
    except Exception as e:
        print(f"Generation Error: {e}")
        raise e

def update_gallery(data, filename):
    if not os.path.exists(GALLERY_FILE): return False
    with open(GALLERY_FILE, 'r', encoding='utf-8') as f: gallery_html = f.read()
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    new_card = f"""
            <!-- Auto-Generated Card -->
            <article class="blog-card" onclick="location.href='{filename}'">
                <div class="card-image"><div class="abstract-pattern"></div><img src="logo.png" style="width: 60px; opacity: 0.5;"></div>
                <div class="card-content">
                    <span class="category-tag">{data.category}</span>
                    <h2 class="card-title">{data.title}</h2>
                    <p class="card-excerpt">{data.excerpt}</p>
                    <div class="card-footer"><span>{date_str}</span><span>10 min read</span></div>
                </div>
            </article>
    """
    marker = '<div class="blog-gallery" id="blog-gallery">'
    if marker in gallery_html:
        parts = gallery_html.split(marker)
        with open(GALLERY_FILE, 'w', encoding='utf-8') as f:
            f.write(parts[0] + marker + new_card + parts[1])
        return True
    return False

def main():
    print("--- AAES Automated Blog Engine ---")
    try:
        data = generate_content()
        print(f"Topic: {data.title}")
        
        # Create Article
        with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f: template = f.read()
        date_str = datetime.datetime.now().strftime("%B %d, %Y")
        html = template.replace("{{TITLE}}", data.title).replace("{{METADESC}}", data.meta_description).replace("{{DATE}}", date_str).replace("{{CONTENT}}", data.content_html)
        filename = f"{data.slug}.html"
        with open(filename, 'w', encoding='utf-8') as f: f.write(html)
        
        # Update Gallery
        update_gallery(data, filename)

        # Share on LinkedIn
        if LINKEDIN_WEBHOOK_URL:
            article_url = f"{WEBSITE_URL}/{filename}"
            clean_post = f"{data.linkedin_teaser_body}\n\nRead the technical analysis here: {article_url}"
            requests.post(LINKEDIN_WEBHOOK_URL, json={ "teaser": clean_post })
            print("LinkedIn update sent.")
        
        # History
        history = get_history()
        history.append({"title": data.title, "slug": data.slug})
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f: json.dump(
