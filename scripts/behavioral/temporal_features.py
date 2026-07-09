import pandas as pd
import numpy as np
import os

# ==========================================
# LOAD DATA
# ==========================================

df = pd.read_json(
    "data/processed/processed_posts.json"
)

print(f"Loaded posts: {len(df)}")

# ==========================================
# CHECK TIMESTAMP COLUMN
# ==========================================

if "timestamp" not in df.columns:

    raise ValueError(
        "timestamp column not found "
        "in processed_posts.json"
    )

# ==========================================
# CONVERT TO DATETIME
# ==========================================

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)

# ==========================================
# EXTRACT TEMPORAL FEATURES
# ==========================================

df["hour"] = (
    df["timestamp"]
    .dt.hour
)

df["weekday"] = (
    df["timestamp"]
    .dt.weekday
)

df["day_name"] = (
    df["timestamp"]
    .dt.day_name()
)

df["month"] = (
    df["timestamp"]
    .dt.month
)

df["is_weekend"] = (
    df["weekday"] >= 5
).astype(int)

# ==========================================
# POSTS PER DAY
# ==========================================

df["date"] = (
    df["timestamp"]
    .dt.date
)

posts_per_day = (
    df.groupby("date")
    .size()
    .rename("posts_per_day")
)

df = df.merge(
    posts_per_day,
    on="date",
    how="left"
)

# ==========================================
# SORT FOR TIME DIFFERENCES
# ==========================================

df = df.sort_values(
    by="timestamp"
)

# ==========================================
# TIME DELTA BETWEEN POSTS
# ==========================================

df["time_diff_minutes"] = (
    df["timestamp"]
    .diff()
    .dt.total_seconds()
    / 60
)

# ==========================================
# FILL FIRST NULL
# ==========================================

df["time_diff_minutes"] = (
    df["time_diff_minutes"]
    .fillna(0)
)

# ==========================================
# BURST DETECTION
# ==========================================

df["is_burst"] = (
    df["time_diff_minutes"] < 10
).astype(int)

# ==========================================
# SELECT OUTPUT COLUMNS
# ==========================================

temporal_df = df[[
    "doc_id",
    "timestamp",
    "hour",
    "weekday",
    "day_name",
    "month",
    "is_weekend",
    "posts_per_day",
    "time_diff_minutes",
    "is_burst"
]]

# ==========================================
# CREATE OUTPUT DIRECTORY
# ==========================================

os.makedirs(
    "data/processed",
    exist_ok=True
)

# ==========================================
# SAVE FEATURES
# ==========================================

output_path = (
    "data/processed/temporal_features.csv"
)

temporal_df.to_csv(
    output_path,
    index=False
)

# ==========================================
# STATS
# ==========================================

print("\n================================")
print(
    f"Saved temporal features to:\n"
    f"{output_path}"
)
print("================================")

print("\nTemporal Feature Summary:\n")

print(
    temporal_df[
        [
            "hour",
            "weekday",
            "posts_per_day",
            "time_diff_minutes"
        ]
    ].describe()
)