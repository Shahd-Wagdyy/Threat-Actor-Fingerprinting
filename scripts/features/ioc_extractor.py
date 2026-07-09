import json
import re
try:
    import pandas as pd
except ImportError:
    pd = None

# ==========================================
# LOAD POSTS
# ==========================================

INPUT_FILE = "data/processed/processed_posts.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    posts = json.load(f)

print(f"Loaded {len(posts)} posts")

# ==========================================
# REGEX PATTERNS
# ==========================================

IP_REGEX = r"(?:\d{1,3}\.){3}\d{1,3}"

DOMAIN_REGEX = r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b"

CVE_REGEX = r"CVE-\d{4}-\d{4,7}"

SHA256_REGEX = r"\b[a-fA-F0-9]{64}\b"

BTC_REGEX = r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b"

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

URL_REGEX = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:/[-\w.!@#$%^&*()_+=~]*)?"

# Expansion patterns
ETH_WALLET_REGEX = r"\b0x[a-fA-F0-9]{40}\b"
FILENAME_REGEX = r"\b[\w-]+\.(?:exe|dll|bat|sh|py|bin|zip|rar|7z|tmp)\b"
REGISTRY_REGEX = r"\bHKEY_(?:LOCAL_MACHINE|CURRENT_USER|USERS|CLASSES_ROOT|CURRENT_CONFIG)[\w\\]+\b"
MUTEX_REGEX = r"\b(?:Global|Local)\\[\w-]{10,}\b|\bBaseNamedObjects\\[\w-]{10,}\b"

# Threat-related keywords
HARMFUL_WORDS = [
    "leak", "malware", "ransomware", "hack", "bypass", "exploit", 
    "c2", "shell", "stealer", "botnet", "injector", "phish",
    "vulnerability", "darkweb", "onion", "bitcoin", "crypto",
    "password", "payload", "backdoor", "trojan", "worm"
]

# ==========================================
# EXTRACT IOCS
# ==========================================

def extract_from_text(text):
    """Utility to extract IOC counts and values from a single string"""
    ips = re.findall(IP_REGEX, text)
    domains = re.findall(DOMAIN_REGEX, text)
    cves = re.findall(CVE_REGEX, text)
    sha256s = re.findall(SHA256_REGEX, text)
    btc_wallets = re.findall(BTC_REGEX, text)
    eth_wallets = re.findall(ETH_WALLET_REGEX, text)
    emails = re.findall(EMAIL_REGEX, text)
    urls = re.findall(URL_REGEX, text)
    files = re.findall(FILENAME_REGEX, text)
    registry = re.findall(REGISTRY_REGEX, text)
    mutexes = re.findall(MUTEX_REGEX, text)

    # Harmful words detection
    found_harmful = [word for word in HARMFUL_WORDS if word in text.lower()]
    
    return {
        "ip_count": len(ips),
        "domain_count": len(domains),
        "cve_count": len(cves),
        "sha256_count": len(sha256s),
        "btc_wallet_count": len(btc_wallets),
        "eth_wallet_count": len(eth_wallets),
        "email_count": len(emails),
        "url_count": len(urls),
        "file_count": len(files),
        "registry_count": len(registry),
        "mutex_count": len(mutexes),
        "harmful_word_count": len(found_harmful),
        "ips": ips,
        "domains": domains,
        "cves": cves,
        "sha256s": sha256s,
        "btc_wallets": btc_wallets,
        "eth_wallets": eth_wallets,
        "emails": emails,
        "urls": urls,
        "files": files,
        "registry": registry,
        "mutexes": mutexes,
        "harmful_words": found_harmful
    }

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    print(f"Loaded {len(posts)} posts")
    
    rows = []
    for post in posts:
        text = post["text"]
        ioc_data = extract_from_text(text)
        
        row = {
            "doc_id": post["doc_id"],
            "language": post["language"],
            "channel": post["channel"],
            "ip_count": ioc_data["ip_count"],
            "domain_count": ioc_data["domain_count"],
            "cve_count": ioc_data["cve_count"],
            "sha256_count": ioc_data["sha256_count"],
            "btc_wallet_count": ioc_data["btc_wallet_count"],
            "email_count": ioc_data["email_count"],
            "ips": ",".join(ioc_data["ips"]),
            "domains": ",".join(ioc_data["domains"]),
            "cves": ",".join(ioc_data["cves"])
        }
        rows.append(row)

    # ==========================================
    # SAVE CSV
    # ==========================================
    if pd:
        df = pd.DataFrame(rows)
        OUTPUT_FILE = "data/processed/ioc_features.csv"
        df.to_csv(OUTPUT_FILE, index=False)
        print("\n================================")
        print(f"Saved IOC features to: {OUTPUT_FILE}")
        print("================================")
        
        # ==========================================
        # SHOW STATS
        # ==========================================
        print("\nIOC Statistics:\n")
        print("IPs found:", df["ip_count"].sum())
        print("Domains found:", df["domain_count"].sum())
        print("CVEs found:", df["cve_count"].sum())
        print("SHA256 hashes found:", df["sha256_count"].sum())
    else:
        print("\nWarning: pandas not found. Skipping CSV export and statistics.")

if __name__ == "__main__":
    main()