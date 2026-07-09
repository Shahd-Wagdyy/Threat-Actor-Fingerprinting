import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

# Load training dataset
df = pd.read_csv("outputs/training_dataset.csv")

# Features
X = df[
    [
        "avg_word_count",
        "avg_posts_per_day",
        "avg_sentence_length",
        "emoji_count",
        "uppercase_ratio",
        "vocab_richness",
        "readability",
        "domains",
        "ips",
        "cves",
        "hashes"
    ]
]

# Labels
y = df["label"]

# Encode labels
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.3,
    random_state=42
)

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Predictions
predictions = model.predict(X_test)

# Evaluation
print(
    classification_report(
        y_test,
        predictions
    )
)

print("training complete")