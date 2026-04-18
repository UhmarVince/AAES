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
# Using the stable flash model
MODEL_NAME = 'gemini-1.5-flash' 

def get_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return []
    return []

def generate_content():
    history = get_history()
    available_links = [{"title": "Home", "url": "index.html"}]
    for post in history[-5:]: available_links.append({"title": post['title'], "url": f"{post['slug']}.html"})
    
    prompt = f"""
    You are a humble Philippine Structural Engineer. You are NOT an AI.
    
    TONE: Quietly technical, humble, and direct. 
    PROHIBITION: NEVER mention your title. NEVER say "Senior", "Expert", or "Master". NEVER brag.
    FORMAT: HTML only. NO dashes (-) or asterisks (*). 
    
    SOCIAL TASK (linkedin_teaser_body): Write a short, humble technical observation.
    - Paragraph 1: Mention a common structural challenge in PH simply.
    - Paragraph 2: Mention how a design choice helps resilience.
    - RULES: NO hashtags. NO links. NO titles. NO bragging. Just the 2 paragraphs.
    """
    
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME, contents=prompt,
                config={'response_mime_type': 'application/json', 'response_schema': BlogData}
            )
            return response.parsed
        except:
            time.sleep(10); continue

def post_to_linkedin(data, article_url):
    if not LINKEDIN_WEBHOOK_URL: return
    
    # We combine everything here so Make.com doesn't have to "think"
    clean_post = f"{data.linkedin_teaser_body}\n\nRead the technical analysis here: {article_url}"

    print("Sending final clean post to Make.com...")
    # WE ONLY SEND THE 'TEASER'. This prevents double links or metadata leaks.
    payload = { "teaser": clean_post }
    
    try:
        requests.post(LINKEDIN_WEBHOOK_URL, json=payload)
        print("Success!")
    except: pass

def main():
    try:
        data = generate_content()
        # Save files
        with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f: template = f.read()
        date_str = datetime.datetime.now().strftime("%B %d, %Y")
        html = template.replace("{{TITLE}}", data.title).replace("{{METADESC}}", data.meta_description).replace("{{DATE}}", date_str).replace("{{CONTENT}}", data.content_html)
        filename = f"{data.slug}.html"
        with open(filename, 'w', encoding='utf-8') as f: f.write(html)
        
        # Share
        article_url = f"{WEBSITE_URL}/{filename}"
        post_to_linkedin(data, article_url)
        
        # Update History
        history = get_history()
        history.append({"title": data.title, "slug": data.slug})
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f: json.dump(history, f)
        
    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    main()
