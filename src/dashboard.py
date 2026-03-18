import streamlit as st
from kafka import KafkaConsumer
import json

st.title("🚨 Real-Time Network Anomaly Detection")

consumer = KafkaConsumer(
    "anomaly-alerts",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

placeholder = st.empty()

for message in consumer:
    data = message.value

    with placeholder.container():
        if data["is_anomaly"]:
            st.error(f"🚨 Anomaly | Score: {data['anomaly_score']:.2f}")
        else:
            st.success(f"Normal | Score: {data['anomaly_score']:.2f}")
