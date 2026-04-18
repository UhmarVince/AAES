import os
import json
import datetime
import re
from google import genai
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
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
    You are an expert Structural Engineer in the Philippines. You are NOT an AI assistant; you are a senior professional structural engineer writing for a technical audience.
    
    TONE AND VOICE:
    - Sound like an experienced, grounded engineer. 
    - Be precise, technical, and authoritative.
    - HUMILITY: Do NOT claim AAES is the "best," "no. 1," or "leader." Avoid marketing hype. Focus solely on expertise and facts.
    - NO AI-sounding introductory or concluding phrases. Start and end directly.
    - Use clear, professional English with perfect grammar.
    
    SEO & LINKING:
    - TARGET: Rank #1 for structural engineering in the Philippines by providing the most technical and valuable content.
    - INTERNAL LINKING: You MUST include at least 2 organic internal links to other AAES content. Use the list of available links below.
    - Format links as <a href="url">Link Text</a>.
    
    AVAILABLE INTERNAL LINKS:
    {json.dumps(available_links, indent=2)}
    
    CONTENT RULES:
    - NEVER mention third-party brand names.
    - Use ONLY verified facts from trusted sources (NSCP 2015, ACI 318, etc.).
    - Focus on the Philippine context (local soil, seismic zones, typhoons).
    - NO DASHES (-) and NO ASTERISKS (*) in the content for formatting. Use ONLY HTML tags (<h2>, <h3>, <p>, <ul>, <li>, <strong>).
    
    TOPIC CONTEXT:
    Already covered topics: {history_titles}
    
    TASK:
    1. Brainstorm a NEW, unique topic about structural engineering in the Philippines.
    2. Write a professional, data-driven article (Minimum 1200 words).
    
    OUTPUT FORMAT (JSON):
    {{
        "title": "Technical, Keyword-Rich Title",
        "slug": "url-friendly-slug",
        "category": "Technical Guide / Engineering Analysis",
        "meta_description": "Under 160 chars",
        "excerpt": "A professional 1-2 sentence technical summary",
        "content_html": "The full article body in HTML. Deep technical precision is mandatory."
    }}
    
    Return ONLY the JSON.
    """
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    
    # More robust JSON extraction
    content = response.text
    try:
        start_idx = content.find('{')
        if start_idx == -1:
            raise ValueError("No JSON object found in response")
        
        # Use raw_decode to get only the first valid JSON object
        data, index = json.JSONDecoder(strict=False).raw_decode(content[start_idx:])
        return data
    except Exception as e:
        print(f"FAILED TO PARSE JSON. RAW RESPONSE: {content}")
        raise e

def create_article_page(data):
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()
    
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    
    html = template.replace("{{TITLE}}", data['title'])
    html = html.replace("{{METADESC}}", data['meta_description'])
    html = html.replace("{{DATE}}", date_str)
    html = html.replace("{{CONTENT}}", data['content_html'])
    
    filename = f"{data['slug']}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    return filename

def update_gallery(data, filename):
    with open(GALLERY_FILE, 'r', encoding='utf-8') as f:
        gallery_html = f.read()
    
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    
    # Create the new card HTML
    new_card = f"""
            <!-- Auto-Generated Card: {data['title']} -->
            <article class="blog-card" onclick="location.href='{filename}'">
                <div class="card-image">
                    <div class="abstract-pattern"></div>
                    <img src="logo.png" style="width: 60px; opacity: 0.5; filter: grayscale(1);">
                </div>
                <div class="card-content">
                    <span class="category-tag">{data['category']}</span>
                    <h2 class="card-title">{data['title']}</h2>
                    <p class="card-excerpt">{data['excerpt']}</p>
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
        print(f"Topic Selected: {data['title']}")
        
        filename = create_article_page(data)
        print(f"Article page created: {filename}")
        
        if update_gallery(data, filename):
            print("Gallery page updated successfully.")
        
        # Update history
        history = get_history()
        history.append({
            "title": data['title'],
            "slug": data['slug'],
            "date": datetime.datetime.now().isoformat()
        })
        save_history(history)
        
        print(f"Success! Blog post '{data['title']}' is now live.")
        
    except Exception as e:
        print(f"Error during generation: {e}")
        # Explicitly re-raise to fail the CI/CD job
        raise e

if __name__ == "__main__":
    main()
