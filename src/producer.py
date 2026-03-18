from kafka import KafkaProducer
import pandas as pd
import json
import time

# Load the data
df = pd.read_csv("../data/processed/network_logs_preprocessed.csv")

# ────────────────────────────────────────────────
# Define EXACTLY the same 16 features used in training
# ────────────────────────────────────────────────
core_features = ['dur', 'sbytes', 'dbytes', 'sttl', 'dttl', 'sport', 'dsport']
proto_features = [
    'proto_tcp', 'proto_udp', 'proto_icmp', 'proto_arp',
    'proto_esp', 'proto_gre', 'proto_ipcomp', 'proto_ipv6', 'proto_sctp'
]

feature_cols = [c for c in core_features + proto_features if c in df.columns]

print(f"Sending only {len(feature_cols)} features: {feature_cols}")


producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print("🚀 Starting producer...")

for i, row in df.iterrows():
    # Only take the 16 columns the model knows
    message = row[feature_cols].to_dict()



    producer.send("network-logs", message)

    time.sleep(0.01)  # simulate real-time streaming

producer.flush()
print("✅ Streaming finished")
