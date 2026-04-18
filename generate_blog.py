import os
import json
import datetime
import re
import requests
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
LINKEDIN_WEBHOOK_URL = os.getenv("LINKEDIN_WEBHOOK_URL") 
WEBSITE_URL = "https://aa-engineers.net" # Update as needed

if not API_KEY:
    print("CRITICAL ERROR: GEMINI_API_KEY not found in environment variables.")
    # In CI, we want to fail fast
    exit(1)

HISTORY_FILE = "blog_history.json"
TEMPLATE_FILE = "blog-template.html"
GALLERY_FILE = "blog.html"

# Use the new google-genai Client
client = genai.Client(api_key=API_KEY)
MODEL_NAME = 'gemini-2.5-flash' # Updated to a newer supported model

def get_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def get_available_links():
    history = get_history()
    # Core pages
    links = [
        {"title": "Home", "url": "index.html"},
        {"title": "Our Services", "url": "services.html"},
        {"title": "Projects Gallery", "url": "projects.html"}
    ]
    # Existing articles
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
    You are an expert Senior Structural Engineer in the Philippines. You are NOT an AI asisstant.
    
    TONE: Precise, technical, authoritative, and humble. NO marketing hype. NEVER use AI-sounding introductory or concluding phrases (e.g., "In conclusion," "Dive deep into"). Start and end directly like a busy professional.
    CONTENT: Use NSCP 2015, ACI 318 principles. Focus on PH context (Seismic, Soil, Typhoons).
    SAFETY: DO NOT mention specific code Chapter or Section numbers (to avoid misinformation). Mention the Code itself (e.g. NSCP 2015) but skip the section numbers.
    
    FORMAT: ABSOLUTELY NO dashes (-) and NO asterisks (*) for formatting. Use HTML tags only (<h2>, <h3>, <ul>, <li>, <strong>).
    INTERNAL LINKING: Include at least 2 links from this list: {json.dumps(available_links)}
    LINK STYLE: Use contextual, clickable words within paragraphs. For example, instead of 'Learn more at <a>url</a>', use 'integrating <a>advanced seismic analysis</a> techniques'.
    SOCIAL STYLE (linkedin_teaser): Write a professional LinkedIn post. Keep hashtags at the VERY BOTTOM. Mandatory hashtag: #AAES.
    
    Already covered: {history_titles}
    
    TASK: Write a new technical 1200+ word structural engineering article for the Philippine market.
    """
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': BlogData,
        }
    )
    
    return response.parsed

def post_to_linkedin(data, article_url):
    if not LINKEDIN_WEBHOOK_URL:
        print("LinkedIn Webhook URL not set. Skipping social share.")
        return

    print("Triggering LinkedIn share via Webhook...")
    
    # We send a simple JSON to the webhook
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
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()
    
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    
    html = template.replace("{{TITLE}}", data.title)
    html = html.replace("{{METADESC}}", data.meta_description)
    html = html.replace("{{DATE}}", date_str)
    html = html.replace("{{CONTENT}}", data.content_html)
    
    filename = f"{data.slug}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    return filename

def update_gallery(data, filename):
    with open(GALLERY_FILE, 'r', encoding='utf-8') as f:
        gallery_html = f.read()
    
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    
    # Create the new card HTML
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
    
    # Inject after the gallery container start
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
    print(f"Using Model: {MODEL_NAME}")
    print("Generating unique topic and content...")
    
    try:
        data = generate_content()
        print(f"Topic Selected: {data.title}")
        
        filename = create_article_page(data)
        print(f"Article page created: {filename}")
        
        if update_gallery(data, filename):
            print("Gallery page updated successfully.")
        
        # Share on LinkedIn
        article_url = f"{WEBSITE_URL}/{filename}"
        post_to_linkedin(data, article_url)
        
        # Update history
        history = get_history()
        history.append({
            "title": data.title,
            "slug": data.slug,
            "date": datetime.datetime.now().isoformat()
        })
        save_history(history)
        
        print(f"Success! Blog post '{data.title}' is now live.")
        
    except Exception as e:
        print(f"Error during generation: {e}")
        # Explicitly re-raise to fail the CI/CD job
        raise e

if __name__ == "__main__":
    main()
