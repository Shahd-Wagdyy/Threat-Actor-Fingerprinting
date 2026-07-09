import pandas as pd

# Load clustered posts
df = pd.read_csv("outputs/clustering_results.csv")

# Load analyst labels
labels_df = pd.read_csv(
    "data/labeled/cluster_labels.csv"
)

# Aggregate cluster statistics
cluster_features = []

for cluster_id, group in df.groupby("cluster"):

    feature_row = {
        "cluster_id": cluster_id,

        # Writing behavior
        "avg_word_count": group["word_count"].mean(),
        "avg_sentence_length": group["avg_sentence_length"].mean(),
        "emoji_count": group["emoji_count"].mean(),
        "uppercase_ratio": group["uppercase_ratio"].mean(),
        "vocab_richness": group["vocab_richness"].mean(),
        "readability": group["readability"].mean(),

        # Activity behavior
        "avg_posts_per_day": group["posts_per_day"].mean(),

        # IOC placeholders
        "domains": 0,
        "ips": 0,
        "cves": 0,
        "hashes": 0
    }

    cluster_features.append(feature_row)

# Convert to dataframe
features_df = pd.DataFrame(cluster_features)

# Merge with labels
training_df = features_df.merge(
    labels_df,
    on="cluster_id",
    how="inner"
)

print(training_df.head())

# Save dataset
training_df.to_csv(
    "outputs/training_dataset.csv",
    index=False
)

print("saved training dataset")