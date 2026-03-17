# src/preprocessing.py

import pandas as pd
from sklearn.preprocessing import StandardScaler
from data_loader import load_data, convert_types
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

SAVE_PATH = BASE_DIR / "data" / "processed" / "network_logs_preprocessed.csv"
SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)


def select_features(df):
    print("Selecting features...")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    columns = [
        "timestamp"
        "srcip",
        "dstip",
        "sport",
        "dsport",
        "proto",
        "dur",
        "sbytes",
        "dbytes",
        "sttl",
        "dttl",
        "label"
    ]

    df = df[columns]

    return df


def handle_missing(df):
    print("Handling missing values...")

    numeric_cols = [
        "sport",
        "dsport",
        "dur",
        "sbytes",
        "dbytes",
        "sttl",
        "dttl"
    ]

    # Fill numeric columns with median instead of dropping rows
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    # Drop rows where proto or label are missing
    df = df.dropna(subset=["proto", "label"])

    return df


def remove_duplicates(df):
    print("Removing duplicates...")

    before = df.shape[0]

    df = df.drop_duplicates()

    after = df.shape[0]

    print("Removed:", before - after)

    return df


def encode_protocol(df):
    print("Encoding protocol...")

    df = pd.get_dummies(df, columns=["proto"])

    return df


def normalize_numeric(df):
    print("Normalizing numeric features...")

    scaler = StandardScaler()

    numeric_cols = [
        "sport",
        "dsport",
        "dur",
        "sbytes",
        "dbytes",
        "sttl",
        "dttl"
    ]

    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    return df


def preprocess_data(df):

    # IMPORTANT: correct pipeline order

    df = select_features(df)

    df = handle_missing(df)

    df = remove_duplicates(df)

    df = encode_protocol(df)

    df = normalize_numeric(df)

    return df


if __name__ == "__main__":

    print("Loading data...")
    df = load_data()

    print("Converting data types...")
    df = convert_types(df)

    print("Starting preprocessing...")
    df = preprocess_data(df)

    print(df.head())
    print("Final dataset shape:", df.shape)

    print("Saving processed dataset...")
    df.to_csv(SAVE_PATH, index=False)

    print("Preprocessed dataset saved to:", SAVE_PATH)
