import json
import glob
import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Threat Actor Fingerprinting",
    page_icon="🕵️",
    layout="wide"
)

# ==========================================
# TITLE
# ==========================================

st.title(
    "🕵️ Threat Actor Fingerprinting Dashboard"
)

st.markdown(
    """
    Interactive cyber threat intelligence dashboard
    for stylometric, semantic, and behavioral
    threat actor analysis.
    """
)

# ==========================================
# LOAD DATA
# ==========================================

df = pd.read_csv(
    "data/processed/clustered_posts.csv"
)

# ==========================================
# SIDEBAR FILTERS
# ==========================================

st.sidebar.header("Filters")

cluster_options = sorted(
    df["cluster"].unique()
)

selected_clusters = st.sidebar.multiselect(
    "Select Clusters",
    cluster_options,
    default=cluster_options
)

language_options = sorted(
    df["language"].dropna().unique()
)

selected_languages = st.sidebar.multiselect(
    "Select Languages",
    language_options,
    default=language_options
)

channel_options = sorted(
    df["channel"].dropna().unique()
)

selected_channels = st.sidebar.multiselect(
    "Select Channels",
    channel_options,
    default=channel_options
)

# ==========================================
# APPLY FILTERS
# ==========================================

filtered_df = df[
    (
        df["cluster"].isin(
            selected_clusters
        )
    )
    &
    (
        df["language"].isin(
            selected_languages
        )
    )
    &
    (
        df["channel"].isin(
            selected_channels
        )
    )
]

# ==========================================
# BASIC METRICS
# ==========================================

total_posts = len(
    filtered_df
)

num_clusters = (
    len(
        filtered_df["cluster"]
        .unique()
    )
    - (
        1
        if -1 in filtered_df[
            "cluster"
        ].unique()
        else 0
    )
)

noise_points = (
    filtered_df["cluster"] == -1
).sum()

noise_percentage = (
    noise_points / total_posts
) * 100 if total_posts > 0 else 0

# ==========================================
# METRIC CARDS
# ==========================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Posts",
    total_posts
)

col2.metric(
    "Clusters",
    num_clusters
)

col3.metric(
    "Noise Points",
    noise_points
)

col4.metric(
    "Noise %",
    f"{noise_percentage:.2f}%"
)

st.markdown("---")

# ==========================================
# CLUSTER DISTRIBUTION
# ==========================================

st.header(
    "📊 Cluster Distribution"
)

cluster_counts = (
    filtered_df[filtered_df["cluster"] != -1]["cluster"]
    .value_counts()
    .nlargest(30)
    .reset_index()
)

cluster_counts.columns = [
    "cluster",
    "count"
]

# Convert cluster column to string so Plotly treats it natively as categorical/discrete,
# otherwise it tries to render a continuous axis for 4000+ IDs
cluster_counts["cluster"] = cluster_counts["cluster"].astype(str)

fig_clusters = px.bar(
    cluster_counts,
    x="cluster",
    y="count",
    color="cluster",
    title="Posts per Cluster"
)

st.plotly_chart(
    fig_clusters,
    use_container_width=True
)

# ==========================================
# LANGUAGE DISTRIBUTION
# ==========================================

st.header(
    "🌍 Language Distribution"
)

language_counts = (
    filtered_df["language"]
    .value_counts()
    .reset_index()
)

language_counts.columns = [
    "language",
    "count"
]

fig_lang = px.pie(
    language_counts,
    names="language",
    values="count",
    title="Language Breakdown"
)

st.plotly_chart(
    fig_lang,
    use_container_width=True
)

# ==========================================
# UMAP VISUALIZATION
# ==========================================

st.header(
    "🧠 UMAP Cluster Visualization"
)

if (
    "umap_x" in filtered_df.columns
    and "umap_y" in filtered_df.columns
):

    fig_umap = px.scatter(
        filtered_df,
        x="umap_x",
        y="umap_y",
        color=filtered_df[
            "cluster"
        ].astype(str),
        hover_data=[
            "language",
            "channel",
            "word_count",
            "hour",
            "day_name"
        ],
        title="Threat Actor Clusters"
    )

    st.plotly_chart(
        fig_umap,
        use_container_width=True
    )

else:

    st.warning(
        "UMAP coordinates not found."
    )

# ==========================================
# POSTING HOUR DISTRIBUTION
# ==========================================

st.header(
    "⏰ Posting Hour Distribution"
)

hour_counts = (
    filtered_df["hour"]
    .value_counts()
    .sort_index()
    .reset_index()
)

hour_counts.columns = [
    "hour",
    "count"
]

fig_hours = px.bar(
    hour_counts,
    x="hour",
    y="count",
    title="Posts by Hour"
)

st.plotly_chart(
    fig_hours,
    use_container_width=True
)

# ==========================================
# WEEKDAY DISTRIBUTION
# ==========================================

st.header(
    "📅 Weekday Activity"
)

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

weekday_counts = (
    filtered_df["day_name"]
    .value_counts()
    .reindex(weekday_order)
    .fillna(0)
    .reset_index()
)

weekday_counts.columns = [
    "weekday",
    "count"
]

fig_weekdays = px.bar(
    weekday_counts,
    x="weekday",
    y="count",
    title="Posts by Weekday"
)

st.plotly_chart(
    fig_weekdays,
    use_container_width=True
)

# ==========================================
# TEMPORAL HEATMAP
# ==========================================

st.header(
    "🔥 Temporal Activity Heatmap"
)

heatmap_df = (
    filtered_df.groupby(
        [
            "day_name",
            "hour"
        ]
    )
    .size()
    .reset_index(name="count")
)

heatmap_df["day_name"] = pd.Categorical(
    heatmap_df["day_name"],
    categories=weekday_order,
    ordered=True
)

heatmap_df = heatmap_df.sort_values(
    [
        "day_name",
        "hour"
    ]
)

fig_heatmap = px.density_heatmap(
    heatmap_df,
    x="hour",
    y="day_name",
    z="count",
    title="Posting Activity Heatmap"
)

st.plotly_chart(
    fig_heatmap,
    use_container_width=True
)

# ==========================================
# TOP CHANNELS
# ==========================================

st.header(
    "📡 Top Channels"
)

channel_counts = (
    filtered_df["channel"]
    .value_counts()
    .reset_index()
)

channel_counts.columns = [
    "channel",
    "count"
]

fig_channels = px.bar(
    channel_counts,
    x="channel",
    y="count",
    color="channel",
    title="Posts per Channel"
)

st.plotly_chart(
    fig_channels,
    use_container_width=True
)

# ==========================================
# LOAD PROFILES
# ==========================================

profile_files = glob.glob(
    "outputs/profiles/*.json"
)

profiles = []

for file in profile_files:

    with open(
        file,
        "r",
        encoding="utf-8"
    ) as f:

        profiles.append(
            json.load(f)
        )

# ==========================================
# PROFILE VIEWER
# ==========================================

st.header(
    "🧾 Threat Actor Profiles"
)

cluster_ids = sorted([
    p["cluster_id"]
    for p in profiles
])

selected_cluster = st.selectbox(
    "Select Cluster Profile",
    cluster_ids
)

selected_profile = next(
    p for p in profiles
    if p["cluster_id"]
    == selected_cluster
)

# ==========================================
# PROFILE METRICS
# ==========================================

col1, col2 = st.columns(2)

with col1:

    st.subheader(
        f"Cluster {selected_cluster}"
    )

    st.metric(
        "Total Posts",
        selected_profile[
            "total_posts"
        ]
    )

    st.metric(
        "Average Word Count",
        round(
            selected_profile[
                "average_word_count"
            ],
            2
        )
    )

with col2:

    st.subheader(
        "IOC Summary"
    )

    st.json(
        selected_profile[
            "ioc_summary"
        ]
    )

# ==========================================
# TEMPORAL PROFILE DATA
# ==========================================

st.subheader(
    "⏱ Behavioral Intelligence"
)

col1, col2 = st.columns(2)

with col1:

    st.write(
        "Active Hours"
    )

    st.json(
        selected_profile[
            "active_hours"
        ]
    )

    st.write(
        "Weekend Activity Ratio"
    )

    st.write(
        selected_profile[
            "weekend_activity_ratio"
        ]
    )

with col2:

    st.write(
        "Active Weekdays"
    )

    st.json(
        selected_profile[
            "active_weekdays"
        ]
    )

    st.write(
        "Average Posts Per Day"
    )

    st.write(
        selected_profile[
            "avg_posts_per_day"
        ]
    )

# ==========================================
# LANGUAGES & CHANNELS
# ==========================================

col1, col2 = st.columns(2)

with col1:

    st.subheader(
        "Languages"
    )

    st.json(
        selected_profile[
            "languages"
        ]
    )

with col2:

    st.subheader(
        "Channels"
    )

    st.json(
        selected_profile[
            "channels"
        ]
    )

# ==========================================
# REPRESENTATIVE POSTS
# ==========================================

st.subheader(
    "📝 Representative Posts"
)

for i, post in enumerate(
    selected_profile[
        "sample_posts"
    ],
    start=1
):

    with st.expander(
        f"Post {i}"
    ):

        st.write(post)

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.caption(
    "Threat Actor Fingerprinting Research Dashboard"
)