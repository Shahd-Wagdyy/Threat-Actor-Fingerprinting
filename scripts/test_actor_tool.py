#!/ python
"""
Interactive Threat Actor Fingerprinting Test Tool
Detects IOCs, harmful keywords, and linguistic fingerprinting (stylometry)
"""

import re
import json
import sys
import os
import csv
import math
from datetime import datetime

# Import NLTK for stylometry if possible
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    # Ensure resources are downloaded
    # nltk.download('punkt', quiet=True)
except ImportError:
    print("Warning: nltk not found. Stylometry will be limited.")
    sent_tokenize = lambda x: x.split('.')
    word_tokenize = lambda x: x.split()

try:
    import textstat
except ImportError:
    textstat = None

# ==========================================
# PATTERNS & KEYWORDS (Consolidated)
# ==========================================

IOC_PATTERNS = {
    "IP Address": r"(?:\d{1,3}\.){3}\d{1,3}",
    "Domain": r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b",
    "CVE": r"CVE-\d{4}-\d{4,7}",
    "SHA256 Hash": r"\b[a-fA-F0-9]{64}\b",
    "MD5 Hash": r"\b[a-fA-F0-9]{32}\b",
    "BTC Wallet": r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b",
    "Email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "URL": r"https?://[^\s]+",
}

THREAT_KEYWORDS = {
    "malware": ["malware", "trojan", "virus", "ransomware", "spyware", "backdoor"],
    "phishing": ["phishing", "phish", "spoof", "credential", "login", "bank"],
    "exploit": ["exploit", "vulnerability", "zero-day", "0-day", "payload", "rce"],
    "infrastructure": ["c2", "c&c", "botnet", "server", "proxy", "vpn"],
}

# ==========================================
# CLUSTER DATA LOADING
# ==========================================

CLUSTER_DATA = {} # {id: {"features": [...], "label": "..."}}
FEATURES_TO_MATCH = [
    'char_count', 'word_count', 'sentence_count', 
    'exclamation_count', 'question_count', 'emoji_count', 
    'uppercase_ratio', 'vocab_richness', 'readability'
]

def load_clusters():
    """Loads cluster averages and labels from project outputs"""
    global CLUSTER_DATA
    csv_path = "data/processed/clustered_posts.csv"
    profiles_dir = "outputs/profiles"
    
    if not os.path.exists(csv_path):
        return False
        
    print("[*] Loading cluster fingerprints for matching...")
    
    # 1. Get Cluster Averages from CSV
    cluster_stats = {} # {id: {feat: [values]}}
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cid = row['cluster']
                if cid == "-1": continue # Skip noise
                
                if cid not in cluster_stats:
                    cluster_stats[cid] = {feat: [] for feat in FEATURES_TO_MATCH}
                
                for feat in FEATURES_TO_MATCH:
                    try:
                        val = float(row[feat])
                        cluster_stats[cid][feat].append(val)
                    except (ValueError, KeyError):
                        continue
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return False

    # 2. Compute means and load labels from JSONs
    for cid, stats in cluster_stats.items():
        means = []
        for feat in FEATURES_TO_MATCH:
            vals = stats[feat]
            means.append(sum(vals) / len(vals) if vals else 0)
        
        label = f"Cluster {cid}"
        json_path = os.path.join(profiles_dir, f"cluster_{cid}.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                    label = profile.get("label", label)
            except:
                pass
        
        CLUSTER_DATA[cid] = {"features": means, "label": label}
    
    print(f"[+] Loaded {len(CLUSTER_DATA)} actor fingerprints.")
    return True

def find_closest_cluster(input_style):
    """Matches input style to the nearest cluster using Euclidean distance"""
    if not CLUSTER_DATA:
        return None, 0
        
    input_vec = [input_style.get(f, 0) for f in FEATURES_TO_MATCH]
    
    best_cid = None
    min_dist = float('inf')
    
    for cid, data in CLUSTER_DATA.items():
        # Simple Euclidean distance
        dist = 0
        for i in range(len(input_vec)):
            # Basic weight normalization: words/chars are much larger than ratios
            # We scale by the reference mean to avoid one feature dominating
            ref_val = data["features"][i]
            if ref_val != 0:
                dist += ((input_vec[i] - ref_val) / ref_val) ** 2
            else:
                dist += (input_vec[i]) ** 2
        
        dist = math.sqrt(dist)
        if dist < min_dist:
            min_dist = dist
            best_cid = cid
            
    # Calculate a pseudo-confidence (inverse of distance)
    # This is a guestimate: 1.0 = perfect match, 0.0 = very different
    confidence = max(0, 1 - (min_dist / 10)) 
    
    return CLUSTER_DATA[best_cid], confidence

# ==========================================
# ANALYSIS FUNCTIONS
# ==========================================

def extract_iocs(text):
    results = {}
    for name, pattern in IOC_PATTERNS.items():
        matches = list(set(re.findall(pattern, text, re.IGNORECASE)))
        if matches:
            results[name] = matches
    return results

def detect_threats(text):
    text_lower = text.lower()
    results = {}
    for category, keywords in THREAT_KEYWORDS.items():
        found = [k for k in keywords if k in text_lower]
        if found:
            results[category] = found
    return results

def extract_stylometry(text):
    try:
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        features = {
            "char_count": len(text),
            "word_count": len(words),
            "sentence_count": len(sentences),
            "exclamation_count": text.count("!"),
            "question_count": text.count("?"),
            "emoji_count": len(re.findall(r'[😀-🙏]', text)),
            "uppercase_ratio": sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            "vocab_richness": len(set(words)) / len(words) if words else 0,
        }
        
        if textstat:
            features["readability"] = textstat.flesch_reading_ease(text)
            
        return features
    except Exception as e:
        return {"error": str(e)}

def calculate_risk(iocs, threats):
    ioc_count = sum(len(v) for v in iocs.values())
    threat_count = sum(len(v) for v in threats.values())
    
    score = (ioc_count * 15) + (threat_count * 10)
    score = min(score, 100)
    
    if score >= 70: return "CRITICAL", score
    if score >= 40: return "HIGH", score
    if score >= 20: return "MEDIUM", score
    if score > 0: return "LOW", score
    return "MINIMAL", score

# ==========================================
# UI FUNCTIONS
# ==========================================

def print_banner():
    print("\n" + "="*80)
    print(" " * 20 + "[*] THREAT ACTOR FINGERPRINTING TOOL [*]")
    print("="*80)
    print("\nDetecting: IOCs, Harmful Content, and Linguistic Style (Stylometry)")
    print("Type 'quit' to exit or 'examples' to see test cases.\n")

def analyze_and_print(text):
    print(f"\nEvaluating message: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
    print("-" * 80)
    
    # 1. IOCs
    iocs = extract_iocs(text)
    if iocs:
        print("\n[!] INDICATORS OF COMPROMISE (IOCs) FOUND:")
        for name, matches in iocs.items():
            print(f"   • {name}: {', '.join(matches)}")
    else:
        print("\n[+] No specific IOCs detected.")
    
    # 2. Harmful Content
    threats = detect_threats(text)
    if threats:
        print("\n[!] HARMFUL CONTENT DETECTED:")
        for cat, keywords in threats.items():
            print(f"   • {cat.upper()}: {', '.join(keywords)}")
    else:
        print("\n[+] No harmful keywords detected.")
    
    # 3. Stylometry
    style = extract_stylometry(text)
    print("\n[ ] LINGUISTIC FINGERPRINT (Stylometry):")
    if "error" not in style:
        print(f"   • Length: {style['char_count']} chars, {style['word_count']} words")
        print(f"   • Richness: {style['vocab_richness']:.2f} (Unique/Total ratio)")
        print(f"   • Tone: {style['exclamation_count']}! {style['question_count']}? {style['emoji_count']} emojis")
        if "readability" in style:
            print(f"   • Readability Score: {style['readability']:.1f}")
    else:
        print(f"   • Error extracting style: {style['error']}")
    
    # 4. Cluster Discovery (The "Fingerprinting" Part)
    if CLUSTER_DATA:
        matched_cluster, confidence = find_closest_cluster(style)
        if matched_cluster:
            print("\n[#] THREAT ACTOR DISCOVERY (Fingerprinting):")
            print(f"   • Profile Match: {matched_cluster['label']}")
            print(f"   • Match Confidence: {confidence*100:.1f}%")
            print(f"   • Logic: Style matches behavior of discovered patterns.")
    
    # 5. Risk Assessment
    risk_level, score = calculate_risk(iocs, threats)
    # Remove emoji from risk_level string if needed
    risk_text = risk_level.split(" ")[-1]
    print(f"\n[#] RISK ASSESSMENT: {risk_text} (Score: {score}/100)")
    print("-" * 80)

def main():
    print_banner()
    clusters_loaded = load_clusters()
    if not clusters_loaded:
        print("Warning: Could not load cluster data. Fingerprinting discovery will be inactive.")
        print("Required: data/processed/clustered_posts.csv\n")
    
    while True:
        try:
            user_input = input("\n>> enter the message: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                print("\nGoodbye!\n")
                break
                
            if user_input.lower() == 'examples':
                print("\nTry these:")
                print("1. 'CVE-2024-1234 payload found at 185.123.45.6' (Critical)")
                print("2. 'Join our phishing awareness session tomorrow' (Low)")
                print("3. 'Normal business email with no threats.' (Minimal)")
                continue
            
            analyze_and_print(user_input)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
