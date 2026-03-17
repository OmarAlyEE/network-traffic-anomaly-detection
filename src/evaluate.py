
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    roc_curve
)

# ----------------------------
# Classification Metrics
# ----------------------------

def evaluate_classification(y_true, y_pred, y_scores=None):
    """
    Compute evaluation metrics for anomaly detection.
    """

    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    results = {
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    }

    if y_scores is not None:
        roc_auc = roc_auc_score(y_true, y_scores)
        results["ROC-AUC"] = roc_auc

    return results


# ----------------------------
# Confusion Matrix Plot
# ----------------------------

def plot_confusion_matrix(y_true, y_pred, save_path=None):

    cm = confusion_matrix(y_true, y_pred)

    plt.figure(figsize=(6,5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Normal", "Anomaly"],
        yticklabels=["Normal", "Anomaly"]
    )

    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")

    if save_path:
        plt.savefig(save_path)

    plt.show()


# ----------------------------
# ROC Curve
# ----------------------------

def plot_roc_curve(y_true, y_scores, save_path=None):

    fpr, tpr, _ = roc_curve(y_true, y_scores)

    plt.figure(figsize=(6,5))
    plt.plot(fpr, tpr)
    plt.plot([0,1], [0,1], linestyle="--")

    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")

    if save_path:
        plt.savefig(save_path)

    plt.show()


# ----------------------------
# Anomaly Score Distribution
# ----------------------------

def plot_anomaly_scores(scores, labels=None, save_path=None):

    plt.figure(figsize=(8,5))

    if labels is None:
        sns.histplot(scores, bins=50)
    else:
        sns.histplot(scores[labels==0], color="blue", label="Normal", bins=50)
        sns.histplot(scores[labels==1], color="red", label="Anomaly", bins=50)
        plt.legend()

    plt.title("Anomaly Score Distribution")
    plt.xlabel("Score")
    plt.ylabel("Count")

    if save_path:
        plt.savefig(save_path)

    plt.show()


# ----------------------------
# Compare Multiple Models
# ----------------------------

def compare_models(results_dict):

    df = pd.DataFrame(results_dict).T

    print("\nModel Comparison\n")
    print(df)

    return df
