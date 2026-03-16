# Network Traffic Anomaly Detection Platform

## Project Overview

This project builds a **machine learning pipeline for detecting anomalous network traffic patterns** using large-scale network flow data. The goal is to identify unusual behaviors such as abnormal packet flows, suspicious protocol activity, or unexpected traffic volumes that may indicate **network attacks, failures, or misconfigurations**.

The system processes raw network logs, performs preprocessing and feature engineering, and applies **unsupervised anomaly detection using Isolation Forest** to detect unusual traffic flows.

The project demonstrates a full applied machine learning workflow including:

* Large-scale data preprocessing
* Feature engineering for network traffic
* Unsupervised anomaly detection
* Model training and scoring
* Results persistence and inspection

The pipeline was tested on **~2 million network flows**, making it suitable for realistic operational environments.

---

# Dataset

The project uses the **UNSW-NB15 dataset**, a widely used dataset for network intrusion detection research.

**Dataset:** UNSW-NB15
**Source:** Australian Centre for Cyber Security
**Download link:**
[https://research.unsw.edu.au/projects/unsw-nb15-dataset](https://www.kaggle.com/datasets/mrwellsdavid/unsw-nb15)

The dataset was generated using the **IXIA PerfectStorm tool** to simulate modern network traffic including both normal activity and malicious attacks.

It contains **realistic network flow features** and labeled attack types.

---

## Dataset Characteristics

Typical columns include:

| Feature   | Description                 |
| --------- | --------------------------- |
| timestamp | Time of the network flow    |
| srcip     | Source IP address           |
| dstip     | Destination IP address      |
| sport     | Source port                 |
| dsport    | Destination port            |
| proto     | Network protocol            |
| dur       | Duration of connection      |
| sbytes    | Bytes sent from source      |
| dbytes    | Bytes sent from destination |
| sttl      | Source time-to-live         |
| dttl      | Destination time-to-live    |
| label     | Normal or attack            |

The full dataset contains **49 original features**, but preprocessing and encoding expand the total number of columns.

After preprocessing in this project:

```
~1,980,000 network flows
145 processed columns
```

---

# Project Structure

```
network-traffic-anomaly-detection
│
├── data
│   ├── raw
│   └── processed
│
├── src
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   └── models.py
│
├── models
│
├── notebooks
│
├── reports
│   ├── figures
├── requirements.txt
└── README.md
```

---

# Data Pipeline

The project follows a modular pipeline:

```
Raw Network Logs
      │
      ▼
Data Loading
      │
      ▼
Preprocessing
      │
      ▼
Feature Engineering
      │
      ▼
Anomaly Detection Model
      │
      ▼
Anomaly Scores + Flags
```

---

# Data Loading

Raw data is loaded from CSV files and converted to pandas DataFrames.

Key tasks include:

* Parsing timestamps
* Ensuring correct data types
* Sorting flows chronologically

Example:

```python
df = pd.read_csv("network_logs.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])
```

---

# Data Preprocessing

The preprocessing pipeline performs several cleaning and transformation steps.

### 1. Feature Selection

The following core network features are retained:

```
srcip
dstip
sport
dsport
proto
dur
sbytes
dbytes
sttl
dttl
label
```

These features represent **flow-level statistics commonly used in intrusion detection systems**.

---

### 2. Missing Value Handling

Numeric features are filled using the **median value**:

```
sport
dsport
dur
sbytes
dbytes
sttl
dttl
```

Rows missing critical categorical values such as `proto` or `label` are removed.

---

### 3. Duplicate Removal

Duplicate network flows are removed to avoid biasing the model.

---

### 4. Protocol Encoding

The `proto` column is converted into **one-hot encoded protocol features**.

Examples:

```
proto_tcp
proto_udp
proto_icmp
proto_arp
proto_esp
proto_gre
proto_ipv6
proto_sctp
```

---

### 5. Feature Normalization

Numeric network metrics are standardized using **StandardScaler**:

```
sport
dsport
dur
sbytes
dbytes
sttl
dttl
```

Standardization ensures features have comparable scales for machine learning models.

---

# Feature Engineering

For anomaly detection, a subset of **high-signal traffic features** is used.

Selected features include:

### Flow statistics

```
dur
sbytes
dbytes
sttl
dttl
sport
dsport
```

These describe connection behavior and packet flow characteristics.

---

### Protocol indicators

Selected one-hot protocol features:

```
proto_tcp
proto_udp
proto_icmp
proto_arp
proto_esp
proto_gre
proto_ipcomp
proto_ipv6
proto_sctp
```

These help identify unusual protocol usage patterns.

---

# Machine Learning Model

The project uses the **Isolation Forest algorithm** for unsupervised anomaly detection.

Isolation Forest works by randomly partitioning data and identifying points that require fewer splits to isolate.

Anomalies tend to be **isolated quickly**, producing higher anomaly scores.

Algorithm reference:
Liu, Ting, Zhou (2008) — Isolation Forest

---

## Model Configuration

```
Algorithm: Isolation Forest
Trees: 100
Contamination: 0.005
Parallel training enabled
```

The contamination parameter represents the **expected anomaly ratio in the dataset**.

---

# Model Training

Features are scaled using **StandardScaler** before training.

```
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

The model is trained on the full dataset:

```
model.fit(X_scaled)
```

---

# Anomaly Scoring

The model produces two outputs:

### Anomaly Score

```
scores = -model.decision_function(X)
```

Higher scores indicate more anomalous traffic.

---

### Binary Anomaly Flag

```
preds = model.predict(X)
flags = preds == -1
```

```
True  → anomaly
False → normal traffic
```

---

# Results

Dataset size:

```
1,980,433 network flows
16 selected anomaly detection features
```

Detected anomalies:

```
9,902 flows flagged as anomalous
≈ 0.50% of total traffic
```

Example high anomaly scores:

| anomaly_score | anomaly_flag |
| ------------- | ------------ |
| 0.089         | True         |
| 0.088         | True         |
| 0.087         | True         |

---

# Output Artifacts

The pipeline produces:

### Trained model

```
models/isolation_forest.pkl
```

---

### Annotated dataset

```
data/processed/network_logs_with_anomalies.csv
```

New columns added:

```
anomaly_score
anomaly_flag
```

These allow further inspection and visualization.

---

# Performance

Training was performed on approximately **2 million network flows** with **16 numerical features**.

Isolation Forest training time:

```
~25 seconds
```

Parallel processing was enabled to speed up model training.

---

# Example Workflow

Run preprocessing:

```
python src/preprocessing.py
```

Train the anomaly detection model:

```
python src/models.py
```

Results will be saved automatically.

---

# Future Improvements

Potential extensions to the project include:

* Statistical anomaly detection baselines (Z-score, EWMA)
* Additional feature engineering for network flows
* Model evaluation using labeled attacks
* Explainable anomaly detection using SHAP
* Real-time streaming detection using Kafka
* Interactive anomaly visualization dashboards

---

# Key Technologies

* Python
* pandas
* numpy
* scikit-learn
* Isolation Forest
* network traffic analysis

---

# References

UNSW-NB15 Dataset
https://research.unsw.edu.au/projects/unsw-nb15-dataset

Isolation Forest Paper
https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf

Scikit-learn IsolationForest Documentation
https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html
