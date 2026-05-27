"""
Generate new classical books using AI when topics.txt runs low.

This script:
1. Checks if topics.txt has enough books (< 50 remaining)
2. Generates 100 new classical books using Pollinations AI
3. Appends them to topics.txt
"""

import os
import requests
from urllib.parse import quote
from pathlib import Path
import time
from dotenv import load_dotenv

load_dotenv()

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "")
POLLINATIONS_BASE_URL = "https://gen.pollinations.ai"

def generate_new_books(count=150):
    """Generate new classical books — never repeats a used title."""
    
    # Load ALL used books to prevent ANY repetition
    all_used_titles = set()
    if Path("used_topics.txt").exists():
        with open("used_topics.txt", "r", encoding="utf-8") as f:
            for line in f:
                if ": [BOOK] " in line:
                    title = line.split(": [BOOK] ")[1].strip().lower().split(" by ")[0]
                    all_used_titles.add(title)
    
    # Also load existing topics to avoid duplicates
    if Path("topics.txt").exists():
        with open("topics.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "[BOOK] " in line:
                    title = line.replace("[BOOK] ", "").strip().lower().split(" by ")[0]
                    all_used_titles.add(title)
    
    used_list = ", ".join(list(all_used_titles)[-100:]) if all_used_titles else "None"
    
    system = (
        "You are a literature expert and book curator. "
        f"Create a list of {count} story-driven books. "
        "TIER 1 — Classical literature (ancient to early 1900s): novels, epic poetry, drama, folk tales with strong narratives. "
        "TIER 2 — Modern classics (1900-1980): award-winning novels, popular fiction, adventure, sci-fi, mystery with compelling stories. "
        "TIER 3 — Modern books (1980-today): bestselling novels, critically acclaimed fiction, thrillers, fantasy, literary fiction with gripping plots. "
        "The ONLY requirement: the book must have a STORY (plot, characters, narrative arc). "
        "Exclude: pure philosophy, pure science, pure self-help, pure poetry collections, cookbooks, textbooks. "
        "Include diverse cultures and genres. "
        f"CRITICAL — NEVER repeat these already-used titles: {used_list}. "
        "Format: Title by Author - Genre "
        "Output ONLY books, one per line, no numbers."
    )
    
    all_books = []
    
    batches = count // 50
    for i in range(batches):
        prompt = f"List {50} classical books batch {i+1}"
        
        payload = {
            "model": "openai",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
            "Content-Type": "application/json"
        }

        url = f"{POLLINATIONS_BASE_URL}/v1/chat/completions"
        
        print(f"[books] Generating batch {i+1}/{batches} using PAID API...")
        
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=120)
            r.raise_for_status()
            response_json = r.json()
            content = response_json['choices'][0]['message']['content'].strip()
            
            for line in content.split('\n'):
                cleaned = line.strip()
                for prefix in ['- ', '* ', '• ']:
                    if cleaned.startswith(prefix):
                        cleaned = cleaned[len(prefix):]
                import re
                cleaned = re.sub(r'^\d+[\.\:\)]\s*', '', cleaned)
                if cleaned and ' by ' in cleaned and len(cleaned) > 10:
                    cleaned = re.sub(r'\s*\([^)]*\)', '', cleaned)
                    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                    if ' - ' in cleaned:
                        cleaned = cleaned.split(' - ')[0].strip()
                    # Check this title isn't already used
                    new_title = cleaned.lower().split(' by ')[0].strip()
                    if new_title not in all_used_titles and len(new_title) > 2:
                        all_used_titles.add(new_title)
                        all_books.append(cleaned)
            
            time.sleep(2)
        except Exception as e:
            print(f"[books] Error in batch {i+1}: {e}")
    
    print(f"[books] Generated {len(all_books)} unique new books (filtered from AI output)")
    return all_books[:count]

def check_and_update_topics():
    """Check topics.txt and add more if needed."""
    
    topics_file = Path('topics.txt')
    
    # Read existing topics
    if topics_file.exists():
        with open(topics_file, 'r', encoding='utf-8') as f:
            existing_topics = [line.strip() for line in f if line.strip()]
    else:
        existing_topics = []
    
    print(f"[books] Current books: {len(existing_topics)}")
    
    # Check if we need more books (5 posts/day = faster consumption)
    if len(existing_topics) < 100:
        print(f"[books] Low on books! Generating 150 more...")
        
        # Load existing titles to avoid duplicates in append
        existing_titles = set()
        for t in existing_topics:
            title = t.replace('[BOOK] ', '').lower().split(' by ')[0].strip()
            if title:
                existing_titles.add(title)
        
        new_books = generate_new_books(150)
        
        # Only append truly unique books
        added = 0
        with open(topics_file, 'a', encoding='utf-8') as f:
            for book in new_books:
                title = book.lower().split(' by ')[0].strip()
                if title not in existing_titles:
                    existing_titles.add(title)
                    f.write(f"[BOOK] {book}\n")
                    added += 1
        
        print(f"[books] Added {added} truly new books (filtered {len(new_books) - added} duplicates)")
        print(f"[books] Total books now: {len(existing_topics) + added}")
    else:
        print(f"[books] Enough books available ({len(existing_topics)})")

if __name__ == '__main__':
    check_and_update_topics()
