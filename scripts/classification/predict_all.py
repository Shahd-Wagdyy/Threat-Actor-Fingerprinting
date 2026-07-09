import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import numpy as np

# 1. Load Data
df = pd.read_csv("outputs/clustering_results.csv")
labels_df = pd.read_csv("data/labeled/cluster_labels.csv")

# 2. Extract features for ALL clusters
cluster_features = []
for cluster_id, group in df.groupby("cluster"):
    if cluster_id == -1: continue # Skip noise
    feature_row = {
        "cluster_id": cluster_id,
        "avg_word_count": group["word_count"].mean(),
        "avg_sentence_length": group["avg_sentence_length"].mean(),
        "emoji_count": group["emoji_count"].mean(),
        "uppercase_ratio": group["uppercase_ratio"].mean(),
        "vocab_richness": group["vocab_richness"].mean(),
        "readability": group["readability"].mean(),
        "avg_posts_per_day": group["posts_per_day"].mean(),
        "domains": 0, "ips": 0, "cves": 0, "hashes": 0
    }
    cluster_features.append(feature_row)

features_df = pd.DataFrame(cluster_features)

# 3. Separate Labeled vs Unlabeled
labeled_features = features_df[features_df["cluster_id"].isin(labels_df["cluster_id"])]
unlabeled_features = features_df[~features_df["cluster_id"].isin(labels_df["cluster_id"])].copy()

training_data = pd.merge(labeled_features, labels_df, on="cluster_id", how="inner")

# 4. Prepare model
feature_cols = [
    "avg_word_count", "avg_posts_per_day", "avg_sentence_length",
    "emoji_count", "uppercase_ratio", "vocab_richness", "readability",
    "domains", "ips", "cves", "hashes"
]

X_train = training_data[feature_cols]
y_train = training_data["label"]

encoder = LabelEncoder()
y_train_encoded = encoder.fit_transform(y_train)

# We also need a mapping from 'label' to 'category', 'motivation', 'notes'
metadata_map = training_data[["label", "category", "motivation", "notes"]].drop_duplicates().set_index("label")

# Train
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train_encoded)

# Predict
X_test = unlabeled_features[feature_cols]
y_pred_encoded = model.predict(X_test)
y_pred_probs = model.predict_proba(X_test)

y_pred = encoder.inverse_transform(y_pred_encoded)
confidences = np.max(y_pred_probs, axis=1)

# Format predictions
unlabeled_features["label"] = y_pred
unlabeled_features["confidence"] = np.round(confidences, 2)
unlabeled_features = unlabeled_features.merge(metadata_map, on="label", how="left")

# Only keep necessary columns matching cluster_labels.csv
final_cols = ["cluster_id", "label", "category", "motivation", "confidence", "notes"]
new_labels_df = unlabeled_features[final_cols]
existing_labels_df = labels_df[final_cols]

# Combine
updated_labels_df = pd.concat([existing_labels_df, new_labels_df], ignore_index=True)
updated_labels_df = updated_labels_df.sort_values("cluster_id")

# Save
updated_labels_df.to_csv("data/labeled/cluster_labels.csv", index=False)
print(f"Updated cluster_labels.csv. Total clusters labeled: {len(updated_labels_df)}")
