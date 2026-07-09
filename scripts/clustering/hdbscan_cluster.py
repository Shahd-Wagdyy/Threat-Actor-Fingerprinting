import numpy as np
import pandas as pd
import os

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

import hdbscan
import umap

# ==========================================
# LOAD STYLOMETRIC FEATURES
# ==========================================

features_df = pd.read_csv(
    "data/processed/stylometric_features.csv"
)

print(
    f"Loaded stylometric features: "
    f"{features_df.shape}"
)

# ==========================================
# LOAD TEMPORAL FEATURES
# ==========================================

temporal_df = pd.read_csv(
    "data/processed/temporal_features.csv"
)

print(
    f"Loaded temporal features: "
    f"{temporal_df.shape}"
)

# ==========================================
# MERGE FEATURES
# ==========================================

features_df = pd.merge(
    features_df,
    temporal_df,
    on="doc_id",
    how="left"
)

print(
    f"Merged feature shape: "
    f"{features_df.shape}"
)

# ==========================================
# LOAD EMBEDDINGS
# ==========================================

embeddings = np.load(
    "data/embeddings/post_embeddings.npy"
)

print(
    f"Loaded embeddings: "
    f"{embeddings.shape}"
)

# ==========================================
# REMOVE METADATA COLUMNS
# ==========================================

metadata_columns = [
    "doc_id",
    "language",
    "channel",
    "timestamp",
    "day_name",
    "date"
]

features_cleaned = features_df.drop(
    columns=[
        col for col in metadata_columns
        if col in features_df.columns
    ],
    errors="ignore"
)

# ==========================================
# KEEP ONLY NUMERIC COLUMNS
# ==========================================

numeric_features = (
    features_cleaned
    .select_dtypes(
        include=[
            np.number
        ]
    )
)

print("\nNumeric columns used:\n")

print(
    numeric_features.columns.tolist()
)

# ==========================================
# HANDLE MISSING VALUES
# ==========================================

numeric_features = numeric_features.fillna(0)

# ==========================================
# CONVERT TO NUMPY
# ==========================================

feature_vectors = numeric_features.values

print(
    f"\nFeature vector shape: "
    f"{feature_vectors.shape}"
)

# ==========================================
# FEATURE FUSION
# ==========================================

combined_vectors = np.hstack([
    embeddings,
    feature_vectors
])

print(
    f"Combined shape: "
    f"{combined_vectors.shape}"
)

# ==========================================
# NORMALIZE FEATURES
# ==========================================

print("\nScaling features...")

scaler = StandardScaler()

scaled_vectors = scaler.fit_transform(
    combined_vectors
)

# ==========================================
# PCA DIMENSION REDUCTION
# ==========================================

print("\nRunning PCA...")

pca = PCA(
    n_components=50,
    random_state=42
)

reduced_vectors = pca.fit_transform(
    scaled_vectors
)

print(
    f"PCA output shape: "
    f"{reduced_vectors.shape}"
)

# ==========================================
# UMAP PROJECTION
# ==========================================

print("\nRunning UMAP...")

umap_model = umap.UMAP(
    n_neighbors=10,
    min_dist=0.05,
    metric="cosine",
    random_state=42
)

umap_vectors = umap_model.fit_transform(
    reduced_vectors
)

print(
    f"UMAP shape: "
    f"{umap_vectors.shape}"
)

# ==========================================
# HDBSCAN CLUSTERING
# ==========================================

print("\nRunning HDBSCAN...")

clusterer = hdbscan.HDBSCAN(
    min_cluster_size=3,
    min_samples=2,
    metric="euclidean"
)

cluster_labels = clusterer.fit_predict(
    umap_vectors
)

# ==========================================
# ATTACH CLUSTER DATA
# ==========================================

features_df["cluster"] = cluster_labels

features_df["umap_x"] = (
    umap_vectors[:, 0]
)

features_df["umap_y"] = (
    umap_vectors[:, 1]
)

# ==========================================
# CREATE OUTPUT DIRECTORIES
# ==========================================

os.makedirs(
    "data/processed",
    exist_ok=True
)

os.makedirs(
    "outputs",
    exist_ok=True
)

# ==========================================
# SAVE CLUSTERED POSTS
# ==========================================

clustered_output = (
    "data/processed/clustered_posts.csv"
)

features_df.to_csv(
    clustered_output,
    index=False
)

print("\n================================")
print(
    f"Saved clustered posts to:\n"
    f"{clustered_output}"
)
print("================================")

# ==========================================
# SAVE CLUSTERING RESULTS
# ==========================================

results_output = (
    "outputs/clustering_results.csv"
)

features_df.to_csv(
    results_output,
    index=False
)

print(
    f"Saved clustering results to:\n"
    f"{results_output}"
)

# ==========================================
# CLUSTER STATISTICS
# ==========================================

num_clusters = len(
    set(cluster_labels)
) - (
    1 if -1 in cluster_labels else 0
)

noise_points = list(
    cluster_labels
).count(-1)

print("\n================================")
print(
    f"Clusters discovered: "
    f"{num_clusters}"
)

print(
    f"Noise points: "
    f"{noise_points}"
)

print("================================")

# ==========================================
# CLUSTER DISTRIBUTION
# ==========================================

cluster_counts = (
    features_df["cluster"]
    .value_counts()
    .sort_index()
)

print("\nCluster Distribution:\n")

print(cluster_counts)

# ==========================================
# NOISE PERCENTAGE
# ==========================================

noise_ratio = (
    noise_points / len(features_df)
) * 100

print("\n================================")

print(
    f"Noise percentage: "
    f"{noise_ratio:.2f}%"
)

print("================================")

# ==========================================
# SAVE UMAP COORDINATES
# ==========================================

umap_output = (
    "outputs/umap_coordinates.csv"
)

features_df[
    [
        "doc_id",
        "cluster",
        "umap_x",
        "umap_y"
    ]
].to_csv(
    umap_output,
    index=False
)

print(
    f"Saved UMAP coordinates to:\n"
    f"{umap_output}"
)