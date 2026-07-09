from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError
from langdetect import detect

import json
import hashlib
import os
import asyncio
import pandas as pd

from tqdm import tqdm

# ==========================================
# TELEGRAM API CREDENTIALS
# ==========================================

api_id = 36740203
api_hash = "553456dc76d0806628243900552af077"

# ==========================================
# PUBLIC CHANNELS
# ==========================================

channels = [

    # ======================================
    # ENGLISH — Cybersecurity / Threat Intel
    # ======================================

    "vxunderground",
    "TheHackersNews",
    "cybersecuritynews",
    "daily_dark_web",
    "exploitin",
    "infosec",
    "offsec",
    "osint",
    "osintteam",
    "securityaffairs",
    "hackernews",
    "bugbounty",
    "redteamsec",
    "packetstormsecurity",
    "privacy",
    "technology",
    "opensourceintel",

    # ======================================
    # SPANISH — Ciberseguridad / Hacking
    # ======================================

    "ciberseguridad",
    "hacking_etico",
    "seguridadinformatica",
    "osint_es",
    "cyberespana",
    "hispahack",
    "hackers_es",
    "security_es",

    # ======================================
    # ARABIC — الأمن السيبراني / الهاكرز
    # ======================================

    "AnonymousArabic",
    "arabsecurity",
    "cyber_arab",
    "arabichackers",
    "arabic_osint",
    "cybersecurity_ar",
    "arab_infosec",

    # ======================================
    # GENERAL
    # ======================================

    "durov"
]

# ==========================================
# OUTPUT SETTINGS
# ==========================================

OUTPUT_JSON = "data/raw/telegram_posts.json"
OUTPUT_CSV = "data/raw/telegram_posts.csv"

POST_LIMIT_PER_CHANNEL = 20000

# ==========================================
# CREATE TELEGRAM CLIENT
# ==========================================

client = TelegramClient(
    "threatintel_session",
    api_id,
    api_hash
)

# ==========================================
# HASH FUNCTION
# ==========================================

def generate_doc_id(text):

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()

# ==========================================
# DETECT LANGUAGE
# ==========================================

def detect_language(text):

    try:
        return detect(text)

    except:
        return "unknown"

# ==========================================
# SCRAPE ONE CHANNEL
# ==========================================

async def scrape_channel(channel_name):

    posts = []

    print(f"\n[*] Scraping: {channel_name}")

    try:

        async for message in client.iter_messages(
            channel_name,
            limit=POST_LIMIT_PER_CHANNEL
        ):

            # Skip empty posts
            if not message.text:
                continue

            text = message.text.strip()

            # Skip tiny posts
            if len(text) < 5:
                continue

            # Detect language
            language = detect_language(text)

            # Reply count
            reply_count = 0

            if message.replies:

                reply_count = getattr(
                    message.replies,
                    "replies",
                    0
                )

            post = {

                "doc_id": generate_doc_id(text),

                "text": text,

                "platform": "telegram",

                "channel": channel_name,

                "timestamp": str(message.date),

                "language_hint": language,

                "views": message.views,

                "forwards": message.forwards,

                "reply_count": reply_count
            }

            posts.append(post)

    except FloodWaitError as e:

        wait_time = e.seconds + 5

        print(
            f"[!] Flood wait detected. "
            f"Sleeping {wait_time} seconds..."
        )

        await asyncio.sleep(wait_time)

        return await scrape_channel(channel_name)

    except Exception as e:

        print(f"[!] Error scraping {channel_name}: {e}")

    return posts

# ==========================================
# MAIN FUNCTION
# ==========================================

async def main():

    all_posts = []

    for channel in tqdm(channels):

        posts = await scrape_channel(channel)

        all_posts.extend(posts)

    # ======================================
    # REMOVE DUPLICATES
    # ======================================

    unique_posts = {
        post["doc_id"]: post
        for post in all_posts
    }

    final_posts = list(unique_posts.values())

    # ======================================
    # CREATE OUTPUT DIRECTORY
    # ======================================

    os.makedirs(
        "data/raw",
        exist_ok=True
    )

    # ======================================
    # SAVE JSON
    # ======================================

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            final_posts,
            f,
            ensure_ascii=False,
            indent=4
        )

    # ======================================
    # SAVE CSV
    # ======================================

    df = pd.DataFrame(final_posts)

    df.to_csv(
        OUTPUT_CSV,
        index=False
    )

    # ======================================
    # LANGUAGE STATS
    # ======================================

    print("\n================================")

    print("LANGUAGE DISTRIBUTION:")

    print(
        df["language_hint"]
        .value_counts()
        .head(20)
    )

    # ======================================
    # CHANNEL STATS
    # ======================================

    print("\n================================")

    print("TOP CHANNELS:")

    print(
        df["channel"]
        .value_counts()
        .head(20)
    )

    # ======================================
    # FINAL STATS
    # ======================================

    print("\n================================")

    print(f"Total posts collected: {len(final_posts)}")

    print(f"JSON saved to: {OUTPUT_JSON}")

    print(f"CSV saved to: {OUTPUT_CSV}")

    print("================================")

# ==========================================
# RUN SCRIPT
# ==========================================

with client:

    client.loop.run_until_complete(main())