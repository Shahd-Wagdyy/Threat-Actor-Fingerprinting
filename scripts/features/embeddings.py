import json
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import os

# ==========================================
# INPUT / OUTPUT
# ==========================================

INPUT_FILE = "data/processed/processed_posts.json"

OUTPUT_FILE = "data/embeddings/post_embeddings.npy"

METADATA_FILE = "data/embeddings/post_metadata.csv"

# ==========================================
# LOAD POSTS
# ==========================================

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    posts = json.load(f)

print(f"Loaded {len(posts)} posts")

# ==========================================
# LOAD MULTILINGUAL MODEL
# ==========================================

print("\nLoading LaBSE model...")

model = SentenceTransformer(
    "sentence-transformers/LaBSE"
)

print("Model loaded.")

# ==========================================
# EXTRACT TEXTS
# ==========================================

texts = [
    post["text"]
    for post in posts
]

# ==========================================
# GENERATE EMBEDDINGS
# ==========================================

print("\nGenerating embeddings...")

embeddings = model.encode(
    texts,
    show_progress_bar=True,
    convert_to_numpy=True
)

print(f"Embeddings shape: {embeddings.shape}")

# ==========================================
# SAVE EMBEDDINGS
# ==========================================

os.makedirs("data/embeddings", exist_ok=True)

np.save(OUTPUT_FILE, embeddings)

# ==========================================
# SAVE METADATA
# ==========================================

metadata_rows = []

for post in posts:

    metadata_rows.append({

        "doc_id": post["doc_id"],

        "language": post["language"],

        "channel": post["channel"],

        "timestamp": post["timestamp"]

    })

metadata_df = pd.DataFrame(metadata_rows)

metadata_df.to_csv(
    METADATA_FILE,
    index=False
)

# ==========================================
# DONE
# ==========================================

print("\n================================")
print(f"Saved embeddings to: {OUTPUT_FILE}")
print(f"Saved metadata to: {METADATA_FILE}")
print("================================")