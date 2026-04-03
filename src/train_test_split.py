"""
Train/Test Split for Network Traffic Anomaly Detection
"""

import pandas as pd
from sklearn.model_selection import train_test_split

# Path to processed feature file
FEATURE_FILE = "../data/processed/network_features.csv"

# Load data
df = pd.read_csv(FEATURE_FILE)

# List of features to use for modeling
FEATURE_COLUMNS = [
    "packet_size",
    "rolling_mean_pkt",
    "rolling_std_pkt",
    "zscore_pkt",
    "packets_per_minute",
    "bytes_per_minute",
    "packets_per_src_ip",
    "packets_per_dst_ip",
    "unique_dst_per_src",
    "packets_per_flow",
    "bytes_per_flow",
    "dst_ip_entropy",
    "hour",
    "minute",
    "day_of_week",
    "is_weekend"
]

# -------------------------
# SUPERVISED SPLIT 
# -------------------------
if "label" in df.columns:

    X = df[FEATURE_COLUMNS]
    y = df["label"]

    # stratify to keep normal/anomaly ratio
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print("Supervised train/test split done")
    print(f"X_train: {X_train.shape}, X_test: {X_test.shape}")
    print(f"y_train distribution:\n{y_train.value_counts(normalize=True)}")
    print(f"y_test distribution:\n{y_test.value_counts(normalize=True)}")

    # Save splits
    X_train.to_csv("../data/processed/X_train.csv", index=False)
    X_test.to_csv("../data/processed/X_test.csv", index=False)
    y_train.to_csv("../data/processed/y_train.csv", index=False)
    y_test.to_csv("../data/processed/y_test.csv", index=False)

# -------------------------
# UNSUPERVISED SPLIT 
# -------------------------
else:

    # sort by timestamp for chronological split
    df = df.sort_values("timestamp")
    X = df[FEATURE_COLUMNS]

    split_idx = int(len(X) * 0.8)
    X_train = X.iloc[:split_idx]
    X_test = X.iloc[split_idx:]

    print("Unsupervised chronological train/test split done")
    print(f"X_train: {X_train.shape}, X_test: {X_test.shape}")

    # Save splits
    X_train.to_csv("../data/processed/X_train.csv", index=False)
    X_test.to_csv("../data/processed/X_test.csv", index=False)

print("Train/test CSVs saved in data/processed/")
