import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    ConfusionMatrixDisplay,
)


def compute_metrics(y_true, y_pred):
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def plot_training_loss(loss_history, output_path):
    plt.figure(figsize=(8, 4))
    plt.plot(loss_history, label="Train loss")
    plt.title("Training Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_accuracy(history, output_path):
    plt.figure(figsize=(8, 4))
    plt.plot(history, label="Validation accuracy")
    plt.title("Validation Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_confusion(y_true, y_pred, labels, output_path):
    cm = confusion_matrix(y_true, y_pred, labels=np.arange(len(labels)))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    fig, ax = plt.subplots(figsize=(8, 6))
    disp.plot(ax=ax, xticks_rotation=45, colorbar=False)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close(fig)


def plot_model_compare(results, output_path):
    model_names = list(results.keys())
    f1_scores = [results[m]["metrics"]["f1"] for m in model_names]
    plt.figure(figsize=(8, 4))
    plt.bar(model_names, f1_scores)
    plt.title("Model Compare by F1")
    plt.ylabel("F1-score")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
