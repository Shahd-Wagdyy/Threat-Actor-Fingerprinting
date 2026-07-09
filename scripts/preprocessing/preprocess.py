import json
import re
try:
    import pandas as pd
except ImportError:
    pd = None
from langdetect import detect
from collections import Counter

# ==========================================
# INPUT / OUTPUT FILES
# ==========================================

INPUT_FILE = "data/raw/telegram_posts.json"

OUTPUT_FILE = "data/processed/processed_posts.json"

# ==========================================
# LOAD RAW POSTS
# ==========================================

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    posts = json.load(f)

print(f"Loaded {len(posts)} raw posts")

# ==========================================
# CLEANING FUNCTION
# ==========================================

def get_language(text):
    """Detect the language of the provided text"""
    try:
        return detect(text)
    except Exception:
        return "unknown"

def clean_text(text):

    # Lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\\S+", "[URL]", text)

    # Remove emails
    text = re.sub(r"\\S+@\\S+", "[EMAIL]", text)

    # Remove hashes
    text = re.sub(r"\\b[a-fA-F0-9]{32,64}\\b", "[HASH]", text)

    # Remove extra whitespace
    text = re.sub(r"\\s+", " ", text).strip()

    return text

def main():
    # ==========================================
    # LOAD RAW POSTS
    # ==========================================
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            posts = json.load(f)
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found.")
        return

    print(f"Loaded {len(posts)} raw posts")

    # ==========================================
    # PROCESS POSTS
    # ==========================================
    processed_posts = []
    for post in posts:
        try:
            cleaned_text = clean_text(post["text"])
            # Skip tiny posts
            if len(cleaned_text) < 10:
                continue
            # Detect language
            lang = detect(cleaned_text)
            processed_post = {
                "doc_id": post["doc_id"],
                "text": cleaned_text,
                "platform": post["platform"],
                "channel": post["channel"],
                "timestamp": post["timestamp"],
                "language": lang,
                "views": post.get("views", 0),
                "forwards": post.get("forwards", 0)
            }
            processed_posts.append(processed_post)
        except Exception:
            continue

    # ==========================================
    # REMOVE DUPLICATES
    # ==========================================
    unique_posts = {
        post["doc_id"]: post
        for post in processed_posts
    }
    final_posts = list(unique_posts.values())

    # ==========================================
    # SAVE OUTPUT
    # ==========================================
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            final_posts,
            f,
            ensure_ascii=False,
            indent=4
        )

    # ==========================================
    # DATASET STATISTICS
    # ==========================================
    languages = Counter([p["language"] for p in final_posts])
    print("\n========== DATASET STATS ==========")
    print(f"Processed posts: {len(final_posts)}")
    print(f"Languages: {dict(languages)}")
    print("===================================")

if __name__ == "__main__":
    main()