
"""
Feature Engineering Module for Network Traffic Anomaly Detection
Works with UNSW-NB15 style datasets even if column counts differ.
"""

import pandas as pd
import numpy as np
from scipy.stats import entropy


# -----------------------------------------------------
# DATA LOADING
# -----------------------------------------------------

def load_network_data(path):

    df = pd.read_csv(
        path,
        header=None,
        low_memory=False
    )

    # keep only first columns we actually need
    df = df.iloc[:, :6]

    df.columns = [
        "src_ip",
        "src_port",
        "dst_ip",
        "dst_port",
        "protocol",
        "state"
    ]

    # synthetic packet size (dataset rows represent flows)
    df["packet_size"] = np.random.randint(60, 1500, size=len(df))

    # synthetic timestamp for time-series features
    df["timestamp"] = pd.date_range(
        start="2024-01-01",
        periods=len(df),
        freq="s"
    )

    return df


# -----------------------------------------------------
# TIME FEATURES
# -----------------------------------------------------

def add_time_features(df):

    df["hour"] = df["timestamp"].dt.hour
    df["minute"] = df["timestamp"].dt.minute
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5,6]).astype(int)

    return df


# -----------------------------------------------------
# PACKET STATISTICS
# -----------------------------------------------------

def add_packet_statistics(df, window=20):

    df = df.sort_values("timestamp")

    df["rolling_mean_pkt"] = df["packet_size"].rolling(
        window, min_periods=1
    ).mean()

    df["rolling_std_pkt"] = df["packet_size"].rolling(
        window, min_periods=1
    ).std()

    mean_pkt = df["packet_size"].mean()
    std_pkt = df["packet_size"].std()

    df["zscore_pkt"] = (df["packet_size"] - mean_pkt) / std_pkt

    return df


# -----------------------------------------------------
# TRAFFIC VOLUME FEATURES
# -----------------------------------------------------

def add_traffic_volume_features(df):

    df["minute_bucket"] = df["timestamp"].dt.floor("min")

    packets_per_minute = (
        df.groupby("minute_bucket")
        .size()
        .rename("packets_per_minute")
        .reset_index()
    )

    bytes_per_minute = (
        df.groupby("minute_bucket")["packet_size"]
        .sum()
        .rename("bytes_per_minute")
        .reset_index()
    )

    df = df.merge(packets_per_minute, on="minute_bucket", how="left")
    df = df.merge(bytes_per_minute, on="minute_bucket", how="left")

    return df


# -----------------------------------------------------
# IP FEATURES
# -----------------------------------------------------

def add_ip_features(df):

    src_counts = (
        df.groupby("src_ip")
        .size()
        .rename("packets_per_src_ip")
        .reset_index()
    )

    dst_counts = (
        df.groupby("dst_ip")
        .size()
        .rename("packets_per_dst_ip")
        .reset_index()
    )

    unique_dst = (
        df.groupby("src_ip")["dst_ip"]
        .nunique()
        .rename("unique_dst_per_src")
        .reset_index()
    )

    df = df.merge(src_counts, on="src_ip", how="left")
    df = df.merge(dst_counts, on="dst_ip", how="left")
    df = df.merge(unique_dst, on="src_ip", how="left")

    return df


# -----------------------------------------------------
# FLOW FEATURES
# -----------------------------------------------------

def add_flow_features(df):

    flow_cols = ["src_ip","dst_ip","src_port","dst_port","protocol"]

    flow_stats = (
        df.groupby(flow_cols)
        .agg(
            packets_per_flow=("packet_size","count"),
            bytes_per_flow=("packet_size","sum")
        )
        .reset_index()
    )

    df = df.merge(flow_stats, on=flow_cols, how="left")

    return df


# -----------------------------------------------------
# ENTROPY FEATURES
# -----------------------------------------------------

def compute_entropy(series):

    probs = series.value_counts(normalize=True)
    return entropy(probs)


def add_entropy_features(df):

    df["minute_bucket"] = df["timestamp"].dt.floor("min")

    entropy_vals = (
        df.groupby("minute_bucket")["dst_ip"]
        .apply(compute_entropy)
        .rename("dst_ip_entropy")
        .reset_index()
    )

    df = df.merge(entropy_vals, on="minute_bucket", how="left")

    return df


# -----------------------------------------------------
# PIPELINE
# -----------------------------------------------------

def generate_features(df):

    df = add_time_features(df)
    df = add_packet_statistics(df)
    df = add_traffic_volume_features(df)
    df = add_ip_features(df)
    df = add_flow_features(df)
    df = add_entropy_features(df)

    df = df.fillna(0)

    return df


# -----------------------------------------------------
# FEATURES USED BY MODELS
# -----------------------------------------------------

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


# -----------------------------------------------------
# RUN
# -----------------------------------------------------

if __name__ == "__main__":

    df = load_network_data("../data/raw/network_logs.csv")

    df = generate_features(df)

    print(df[FEATURE_COLUMNS].head())

    df.to_csv("../data/processed/network_features.csv", index=False)

    print("Saved: data/processed/network_features.csv")
