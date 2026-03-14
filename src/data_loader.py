# src/data_loader.py
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

# Paths to dataset and feature names
DATA_PATH = BASE_DIR / "data" / "raw" / "network_logs.csv"
FEATURE_PATH = BASE_DIR / "data" / "raw" / "NUSW-NB15_features.csv"


def load_data():
    print("Loading feature names...")
    # Fix encoding issue for features file
    features = pd.read_csv(FEATURE_PATH, encoding='ISO-8859-1')
    
    # Convert feature names to lowercase to avoid KeyErrors
    column_names = [str(c).lower() for c in features["Name"].tolist()]

    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH, names=column_names, low_memory=False)
    
    # Make sure target column is lowercase too
    if 'label' not in df.columns and 'Label'.lower() not in df.columns:
        df.rename(columns=lambda x: x.lower(), inplace=True)

    print("Dataset loaded.")
    print("Shape:", df.shape)

    return df


def convert_types(df):
    numeric_columns = [
        "sport",
        "dsport",
        "dur",
        "sbytes",
        "dbytes",
        "sttl",
        "dttl"
    ]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


if __name__ == "__main__":
    df = load_data()
    df = convert_types(df)
    print(df.head())
    print("Dataset loaded successfully.")
