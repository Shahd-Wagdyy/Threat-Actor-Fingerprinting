import pandas as pd
import json
import os

# ==========================================
# LOAD DATA
# ==========================================

clusters_df = pd.read_csv(
    "data/processed/clustered_posts.csv"
)

ioc_df = pd.read_csv(
    "data/processed/ioc_features.csv"
)

processed_df = pd.read_json(
    "data/processed/processed_posts.json"
)

# ==========================================
# MERGE DATASETS
# ==========================================

df = pd.merge(
    clusters_df,
    ioc_df,
    on="doc_id",
    how="left"
)

df = pd.merge(
    df,
    processed_df[
        [
            "doc_id",
            "text"
        ]
    ],
    on="doc_id",
    how="left"
)

# Load labels
if os.path.exists("data/labeled/cluster_labels.csv"):
    labels_df = pd.read_csv("data/labeled/cluster_labels.csv")
    df = pd.merge(
        df,
        labels_df[["cluster_id", "label"]].rename(columns={"cluster_id": "cluster"}),
        on="cluster",
        how="left"
    )
    df["label"] = df["label"].fillna("Unlabeled Cluster")
else:
    df["label"] = "Unlabeled Cluster"

# ==========================================
# FIX DUPLICATE COLUMN NAMES
# ==========================================

if "language_x" in df.columns:
    df["language"] = df["language_x"]

if "channel_x" in df.columns:
    df["channel"] = df["channel_x"]

# ==========================================
# OUTPUT DIRECTORY
# ==========================================

os.makedirs(
    "outputs/profiles",
    exist_ok=True
)

# ==========================================
# BUILD CLUSTER PROFILES
# ==========================================

clusters = sorted(
    df["cluster"].unique()
)

for cluster_id in clusters:

    # Skip noise cluster
    if cluster_id == -1:
        continue

    cluster_posts = df[
        df["cluster"] == cluster_id
    ]

    # ======================================
    # BASIC STATS
    # ======================================

    total_posts = len(
        cluster_posts
    )

    languages = (
        cluster_posts["language"]
        .value_counts()
        .to_dict()
    )

    channels = (
        cluster_posts["channel"]
        .value_counts()
        .to_dict()
    )

    avg_words = (
        cluster_posts["word_count"]
        .mean()
    )

    # ======================================
    # TEMPORAL FEATURES
    # ======================================

    active_hours = (
        cluster_posts["hour"]
        .value_counts()
        .head(5)
        .to_dict()
    )

    active_weekdays = (
        cluster_posts["day_name"]
        .value_counts()
        .to_dict()
    )

    weekend_activity_ratio = float(
        cluster_posts["is_weekend"]
        .mean()
    )

    avg_posts_per_day = float(
        cluster_posts["posts_per_day"]
        .mean()
    )

    # ======================================
    # IOC SUMMARY
    # ======================================

    total_domains = (
        cluster_posts["domain_count"]
        .sum()
    )

    total_ips = (
        cluster_posts["ip_count"]
        .sum()
    )

    total_cves = (
        cluster_posts["cve_count"]
        .sum()
    )

    total_hashes = (
        cluster_posts["sha256_count"]
        .sum()
    )

    # ======================================
    # SAMPLE POSTS
    # ======================================

    sample_posts = (
        cluster_posts["text"]
        .dropna()
        .head(5)
        .tolist()
    )

    # ======================================
    # PROFILE OBJECT
    # ======================================
    
    cluster_label = "Unlabeled Cluster"
    if "label" in cluster_posts.columns:
        cluster_label = cluster_posts["label"].iloc[0]

    profile = {

        "cluster_id": int(cluster_id),
        "label": str(cluster_label),

        "total_posts": int(total_posts),

        "languages": languages,

        "channels": channels,

        "average_word_count": round(
            float(avg_words),
            2
        ),

        # ==================================
        # TEMPORAL INTELLIGENCE
        # ==================================

        "active_hours": active_hours,

        "active_weekdays": active_weekdays,

        "weekend_activity_ratio": round(
            weekend_activity_ratio,
            3
        ),

        "avg_posts_per_day": round(
            avg_posts_per_day,
            2
        ),

        # ==================================
        # IOC SUMMARY
        # ==================================

        "ioc_summary": {

            "domains": int(total_domains),

            "ips": int(total_ips),

            "cves": int(total_cves),

            "sha256_hashes": int(total_hashes)
        },

        # ==================================
        # REPRESENTATIVE POSTS
        # ==================================

        "sample_posts": sample_posts
    }

    # ======================================
    # SAVE PROFILE
    # ======================================

    output_path = (
        f"outputs/profiles/"
        f"cluster_{cluster_id}.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            profile,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"Saved profile: "
        f"{output_path}"
    )

# ==========================================
# FINISHED
# ==========================================

print("\n================================")
print("Threat actor profiles generated")
print("================================")