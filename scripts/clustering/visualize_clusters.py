import matplotlib
matplotlib.use("Agg")

import os
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

import umap

# ==========================================
# LOAD CLUSTERING RESULTS
# ==========================================

df = pd.read_csv(
    "outputs/clustering_results.csv"
)

print(f"Loaded clustering results: {df.shape}")

# ==========================================
# KEEP ONLY NUMERIC FEATURES
# ==========================================

numeric_df = df.select_dtypes(
    include=["number"]
)

# Remove target column from features
X = numeric_df.drop(
    columns=["cluster"],
    errors="ignore"
)

# Cluster labels
clusters = df["cluster"].values

print("\n================================")
print("Numeric columns used:")
print("================================")
print(X.columns.tolist())

# ==========================================
# NORMALIZE FEATURES
# ==========================================

print("\nScaling features...")

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

# ==========================================
# PCA DIMENSIONALITY REDUCTION
# ==========================================

print("\nRunning PCA...")

pca = PCA(
    n_components=5,
    random_state=42
)

X_pca = pca.fit_transform(X_scaled)

print(f"PCA output shape: {X_pca.shape}")

# ==========================================
# UMAP VISUALIZATION
# ==========================================

print("\nRunning UMAP...")

umap_model = umap.UMAP(
    n_neighbors=15,
    min_dist=0.1,
    metric="cosine",
    random_state=42
)

embedding_2d = umap_model.fit_transform(
    X_pca
)

print(f"UMAP output shape: {embedding_2d.shape}")

# ==========================================
# CREATE OUTPUT DIRECTORY
# ==========================================

os.makedirs(
    "outputs/figures",
    exist_ok=True
)

# ==========================================
# CREATE VISUALIZATION
# ==========================================

plt.figure(figsize=(14, 10))

scatter = plt.scatter(
    embedding_2d[:, 0],
    embedding_2d[:, 1],
    c=clusters,
    cmap="tab20",
    s=10,
    alpha=0.7
)

plt.title(
    "Threat Actor Cluster Visualization",
    fontsize=16
)

plt.xlabel("UMAP Dimension 1")
plt.ylabel("UMAP Dimension 2")

plt.colorbar(
    scatter,
    label="Cluster ID"
)

# ==========================================
# SAVE FIGURE
# ==========================================

output_path = (
    "outputs/figures/cluster_visualization.png"
)

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

print("\n================================")
print(f"Saved figure to:\n{output_path}")
print("================================")

# ==========================================
# OPTIONAL DISPLAY
# ==========================================

# plt.show()