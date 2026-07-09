#!/usr/bin/env python
"""
Real Pipeline Test Tool
Uses the ACTUAL project modules for preprocessing and feature extraction.
"""

import sys
import os
import json
import csv
import math

# Add project root to sys.path for internal imports
sys.path.append(os.getcwd())

from scripts.preprocessing.preprocess import clean_text, get_language
from scripts.features.stylometry import extract_features
from scripts.features.ioc_extractor import extract_from_text, IP_REGEX

# ==========================================
# CLUSTER DATA (Logic reused from previous tool)
# ==========================================

CLUSTER_DATA = {}
FEATURES_TO_MATCH = [
    'char_count', 'word_count', 'sentence_count', 
    'exclamation_count', 'question_count', 'emoji_count', 
    'uppercase_ratio', 'vocab_richness', 'readability'
]

def load_clusters():
    global CLUSTER_DATA
    csv_path = "data/processed/clustered_posts.csv"
    profiles_dir = "outputs/profiles"
    if not os.path.exists(csv_path): return False
    
    cluster_stats = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row['cluster']
            if cid == "-1": continue
            if cid not in cluster_stats:
                cluster_stats[cid] = {feat: [] for feat in FEATURES_TO_MATCH}
            for feat in FEATURES_TO_MATCH:
                try: cluster_stats[cid][feat].append(float(row[feat]))
                except: continue
                
    for cid, stats in cluster_stats.items():
        means = [sum(vals)/len(vals) if vals else 0 for vals in [stats[f] for f in FEATURES_TO_MATCH]]
        label = f"Cluster {cid}"
        json_path = os.path.join(profiles_dir, f"cluster_{cid}.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f: label = json.load(f).get("label", label)
            except: pass
        CLUSTER_DATA[cid] = {"features": means, "label": label}
    return True

def find_closest_cluster(input_vec, top_n=5):
    matches = []
    for cid, data in CLUSTER_DATA.items():
        # Weighted Euclidean distance
        dist = math.sqrt(sum([((input_vec[i] - data["features"][i])/data["features"][i])**2 if data["features"][i] != 0 else (input_vec[i])**2 for i in range(len(input_vec))]))
        confidence = max(0, 1 - (dist / 10))
        matches.append({
            "cid": cid,
            "label": data["label"],
            "confidence": confidence
        })
    
    # Sort by confidence descending
    matches.sort(key=lambda x: x["confidence"], reverse=True)
    return matches[:top_n]

# ==========================================
# MAIN INTERACTIVE TOOL
# ==========================================

def main():
    print("\n" + "="*80)
    print(" " * 20 + "[*] ACTUAL TOOL PIPELINE INTEGRATION [*]")
    print("="*80)
    print("\nUsing Project Modules: scripts.preprocessing, scripts.features")
    
    if not load_clusters():
        print("Warning: Cluster reference data not found.")

    while True:
        try:
            raw_text = input("\n>> Enter Message: ").strip()
            if not raw_text: continue
            if raw_text.lower() == 'quit': break

            # 1. ACTUAL PREPROCESSING & LANGUAGE
            print("\n[STEP 1] Preprocessing & Language...")
            lang = get_language(raw_text)
            cleaned = clean_text(raw_text)
            print(f"   • Language: {lang}")
            print(f"   • Cleaned: {cleaned[:70]}...")

            # 2. ACTUAL IOC EXTRACTION
            print("[STEP 2] Extracting IOCs & Threat Indicators...")
            ioc_data = extract_from_text(raw_text)
            
            # Map of internal keys to display labels
            ioc_labels = {
                "ips": "IP Addresses",
                "domains": "Domains",
                "urls": "URLs",
                "cves": "CVEs",
                "emails": "Emails",
                "sha256s": "Hashes (SHA256)",
                "btc_wallets": "BTC Wallets",
                "eth_wallets": "ETH Wallets",
                "files": "File Names",
                "registry": "Registry Keys",
                "mutexes": "Mutexes"
            }
            
            found_any = False
            for key, label in ioc_labels.items():
                if ioc_data.get(key):
                    print(f"   • FOUND {label}: {ioc_data[key]}")
                    found_any = True
            
            if ioc_data.get("harmful_words"):
                print(f"   • HARMFUL WORDS DETECTED: {ioc_data['harmful_words']}")
                found_any = True
                
            if not found_any:
                print("   • No IOCs or threat indicators found.")

            # 3. ACTUAL STYLOMETRY
            print("[STEP 3] Extracting Style (Actual stylometry.py logic)...")
            features = extract_features(raw_text)
            print(f"   • Stats: {features.get('word_count')} words, {features.get('vocab_richness', 0):.2f} richness")

            # 4. FINGERPRINT MATCHING
            if CLUSTER_DATA:
                input_vec = [features.get(f, 0) for f in FEATURES_TO_MATCH]
                matches = find_closest_cluster(input_vec, top_n=5)
                print(f"\n[!] TOP THREAT ACTOR MATCHES (Fingerprinting):")
                for i, match in enumerate(matches, 1):
                    prefix = "   • MOST LIKELY: " if i == 1 else f"   • Rank {i}: "
                    print(f"{prefix}{match['label']} (ID: {match['cid']}) - {match['confidence']*100:.1f}% Match")

            print("-" * 80)
            
        except KeyboardInterrupt: break
        except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    main()
