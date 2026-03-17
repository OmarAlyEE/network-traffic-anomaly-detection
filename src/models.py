import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import os

# ----------------------------
# Isolation Forest helpers
# ----------------------------
def train_isolation_forest(X_train, n_estimators=100, contamination=0.01, random_state=42):
    model = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1,
        verbose=1
    )
    model.fit(X_train)
    return model


def predict_isolation_forest(model, X):
    scores = -model.decision_function(X)   # higher = more anomalous
    preds  = model.predict(X)               # -1 = anomaly, 1 = normal
    flags  = preds == -1
    return scores, flags


# ----------------------------
# Model save/load
# ----------------------------
def save_model(model, path):
    with open(path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved → {path}")

def save_scaler(scaler, path):
    with open(path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"Scaler saved → {path}")


# ----------------------------
# Feature selection — tuned to YOUR dataset
# ----------------------------
def generate_features(df):
    print("Selecting features for anomaly detection...")

    # Core numerical flow/packet features (most important for traffic anomalies)
    core_features = [
        'dur',          # flow duration
        'sbytes',       # source bytes
        'dbytes',       # destination bytes
        'sttl',         # source TTL
        'dttl',         # destination TTL
        'sport',        # source port
        'dsport',       # destination port
    ]

    # Selected protocol one-hots (only common/dangerous ones — add more if needed)
    # These help detect protocol anomalies without exploding dimensionality
    proto_features = [
        'proto_tcp',
        'proto_udp',
        'proto_icmp',
        'proto_arp',
        'proto_esp',
        'proto_gre',
        'proto_ipcomp',
        'proto_ipv6',
        'proto_sctp',
    ]

    # Combine
    candidate_cols = core_features + [p for p in proto_features if p in df.columns]

    # Keep only columns that actually exist
    selected_cols = [col for col in candidate_cols if col in df.columns]

    if not selected_cols:
        print("\nERROR: None of the expected numerical features were found!")
        print("Available columns:", df.columns.tolist()[:30], "...")
        raise ValueError("No usable features → check column names or preprocessing")

    print(f"Selected {len(selected_cols)} features:")
    print("  " + ", ".join(selected_cols))

    # Return only these columns as X
    X = df[selected_cols].copy()

    # Quick sanity check
    if X.isna().any().any():
        print("Warning: NaN values found → filling with 0 (adjust if needed)")
        X = X.fillna(0)

    return X, selected_cols


if __name__ == "__main__":

    print("Loading processed dataset...")

    data_path = "../data/processed/network_logs_preprocessed.csv"

    if not os.path.exists(data_path):
        print(f"ERROR: File not found → {data_path}")
        print("Check path or run preprocessing first.")
        exit(1)

    df = pd.read_csv(data_path)
    print(f"Dataset shape: {df.shape}")
    print(f"Columns count: {len(df.columns)}")

    # Generate features
    try:
        X, used_features = generate_features(df)
    except Exception as e:
        print("Feature generation failed:", str(e))
        exit(1)

    if X.empty or X.shape[1] == 0:
        print("No features after selection. Exiting.")
        exit(1)

    print(f"Feature matrix shape: {X.shape}")

    print("\nScaling features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("Training Isolation Forest...")
    if_model = train_isolation_forest(X_scaled, contamination=0.005)  # adjust contamination as needed

    print("Predicting anomalies...")
    scores, flags = predict_isolation_forest(if_model, X_scaled)

    df['anomaly_score'] = scores
    df['anomaly_flag']  = flags

    anomaly_count = flags.sum()
    print(f"\nAnomalies detected: {anomaly_count} / {len(df):,}  ({anomaly_count/len(df):.4f} or {anomaly_count/len(df)*100:.2f}%)")

    # Save model
    os.makedirs("../models", exist_ok=True)
    model_path = "../models/isolation_forest.pkl"
    save_model(if_model, model_path)
    scaler_path = "../models/scaler.pkl"
    save_scaler(scaler, scaler_path)
    # Optional: save results (useful for inspection / evaluation)
    output_path = "../data/processed/network_logs_with_anomalies.csv"
    df.to_csv(output_path, index=False)
    print(f"Results saved → {output_path}")

    # Show sample
    print("\nSample of anomaly scores/flags:")
    print(df[['anomaly_score', 'anomaly_flag']].sort_values('anomaly_score', ascending=False).head(10))
