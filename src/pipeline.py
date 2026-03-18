
from kafka import KafkaConsumer, KafkaProducer
import pandas as pd
import json
import pickle
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

# ----------------------------
# Load trained model + scaler
# ----------------------------
model = pickle.load(open("../models/isolation_forest.pkl", "rb"))
scaler = pickle.load(open("../models/scaler.pkl", "rb"))

# ----------------------------
# Exact feature columns used during training
# ----------------------------

feature_cols = [
    'dur', 'sbytes', 'dbytes', 'sttl', 'dttl', 'sport', 'dsport',
    'proto_tcp', 'proto_udp', 'proto_icmp', 'proto_arp',
    'proto_esp', 'proto_gre', 'proto_ipcomp', 'proto_ipv6', 'proto_sctp'
]

print(f"Expecting exactly {len(feature_cols)} features: {feature_cols}")

# ----------------------------
# Kafka setup
# ----------------------------
consumer = KafkaConsumer(
    "network-logs",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True
)

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print("🚀 Streaming pipeline started... (listening on 'network-logs')")

# ----------------------------
# Streaming loop
# ----------------------------
for message in consumer:
    try:
        data = message.value

        # Convert incoming message to DataFrame
        df = pd.DataFrame([data])


        X = df[feature_cols]

        # Scale using the exact same scaler from training
        X_scaled = scaler.transform(X)

        # Predict
        pred_raw = model.predict(X_scaled)[0]           # -1 = anomaly, 1 = normal
        score = -model.decision_function(X_scaled)[0]   # higher = more anomalous

        is_anomaly = pred_raw == -1

        # Build alert message
        alert = {
            "timestamp": data.get("timestamp", "unknown"),
            "srcip": data.get("srcip", None),
            "dstip": data.get("dstip", None),
            "anomaly_score": float(score),
            "is_anomaly": bool(is_anomaly),
            "prediction_raw": int(pred_raw),
            "original_message_id": message.offset
        }

        # Send alert to downstream topic
        producer.send("anomaly-alerts", alert)
        producer.flush()  # ensure it's sent immediately

        status = "ANOMALY" if is_anomaly else "normal"
        print(f"[{message.offset}] Processed → {status} | score: {score:.4f}")

    except KeyError as ke:
        print(f"❌ Missing feature(s): {ke}")
        print("  Incoming keys:", list(data.keys()))
        print("  Expected:", feature_cols)
        # Optionally send error alert or skip
        continue

    except Exception as e:
        print(f"❌ Error processing message (offset {message.offset}): {e}")
        continue
