import json
try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import numpy as np
except ImportError:
    np = None

import re
from collections import Counter

try:
    from nltk.tokenize import sent_tokenize, word_tokenize
except ImportError:
    # Fallback tokenize
    sent_tokenize = lambda x: x.split('.')
    word_tokenize = lambda x: x.split()

try:
    import textstat
except ImportError:
    textstat = None

# ==========================================
# INPUT / OUTPUT
# ==========================================

INPUT_FILE = "data/processed/processed_posts.json"

OUTPUT_FILE = "data/processed/stylometric_features.csv"

# ==========================================
# LOAD DATA
# ==========================================

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    posts = json.load(f)

print(f"Loaded {len(posts)} processed posts")

# ==========================================
# FEATURE EXTRACTION FUNCTIONS
# ==========================================

def extract_features(text):

    features = {}

    # --------------------------
    # BASIC COUNTS
    # --------------------------

    sentences = sent_tokenize(text)

    words = word_tokenize(text)

    features["char_count"] = len(text)

    features["word_count"] = len(words)

    features["sentence_count"] = len(sentences)

    # --------------------------
    # SENTENCE LENGTH
    # --------------------------

    if len(sentences) > 0:
        sentence_lengths = [len(word_tokenize(s)) for s in sentences]
        if np:
            features["avg_sentence_length"] = np.mean(sentence_lengths)
        else:
            features["avg_sentence_length"] = sum(sentence_lengths) / len(sentence_lengths)
    else:
        features["avg_sentence_length"] = 0

    # --------------------------
    # PUNCTUATION FEATURES
    # --------------------------

    features["exclamation_count"] = text.count("!")

    features["question_count"] = text.count("?")

    features["emoji_count"] = len(
        re.findall(r'[😀-🙏]', text)
    )

    # --------------------------
    # UPPERCASE RATIO
    # --------------------------

    uppercase_chars = sum(1 for c in text if c.isupper())

    features["uppercase_ratio"] = (
        uppercase_chars / len(text)
        if len(text) > 0 else 0
    )

    # --------------------------
    # VOCABULARY RICHNESS
    # --------------------------

    unique_words = len(set(words))

    features["vocab_richness"] = (
        unique_words / len(words)
        if len(words) > 0 else 0
    )

    # --------------------------
    # READABILITY
    # --------------------------

    try:

        features["readability"] = (
            textstat.flesch_reading_ease(text)
        )

    except:

        features["readability"] = 0

    return features

# ==========================================
# PROCESS POSTS
# ==========================================

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    print(f"Loaded {len(posts)} processed posts")

    rows = []
    for post in posts:
        try:
            features = extract_features(post["text"])
            row = {
                "doc_id": post["doc_id"],
                "language": post["language"],
                "channel": post["channel"],
                **features
            }
            rows.append(row)
        except Exception as e:
            print(f"Error: {e}")

    # ==========================================
    # SAVE CSV
    # ==========================================
    if pd:
        df = pd.DataFrame(rows)
        df.to_csv(OUTPUT_FILE, index=False)
        print("\n================================")
        print(f"Saved features to: {OUTPUT_FILE}")
        print(f"Feature rows: {len(df)}")
        print("================================")
    else:
        print("\nWarning: pandas not found. Skipping CSV export.")

if __name__ == "__main__":
    main()