import argparse
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader

from dataset_loader import BehaviorDataset, load_csv
from preprocessing import encode_actions, build_action_sequences, save_encoder
from rnn_model import RNNNextAction
from lstm_model import LSTMNextAction
from bilstm_model import BiLSTMNextAction
from evaluate import (
    compute_metrics,
    plot_training_loss,
    plot_accuracy,
    plot_confusion,
    plot_model_compare,
)


def train_model(model, train_loader, val_loader, device, epochs=10, lr=1e-3):
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    model.to(device)

    train_losses = []
    val_accuracies = []
    best_state = None
    best_accuracy = -1.0

    for _ in range(epochs):
        model.train()
        running_loss = 0.0
        for X_batch, y_batch in train_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)

            optimizer.zero_grad()
            logits = model(X_batch)
            loss = criterion(logits, y_batch)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        epoch_loss = running_loss / max(len(train_loader), 1)
        train_losses.append(epoch_loss)

        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch = X_batch.to(device)
                y_batch = y_batch.to(device)
                preds = model(X_batch).argmax(dim=1)
                correct += (preds == y_batch).sum().item()
                total += y_batch.size(0)

        val_acc = correct / max(total, 1)
        val_accuracies.append(val_acc)
        if val_acc > best_accuracy:
            best_accuracy = val_acc
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    if best_state is not None:
        model.load_state_dict(best_state)

    return model, train_losses, val_accuracies


def predict(model, data_loader, device):
    model.eval()
    y_true = []
    y_pred = []
    with torch.no_grad():
        for X_batch, y_batch in data_loader:
            logits = model(X_batch.to(device))
            preds = logits.argmax(dim=1).cpu().numpy().tolist()
            y_pred.extend(preds)
            y_true.extend(y_batch.numpy().tolist())
    return np.array(y_true), np.array(y_pred)


def main(args):
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_csv(args.dataset_path)
    df, encoder = encode_actions(df)
    X, y = build_action_sequences(df, window_size=args.window_size)

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
    )

    train_loader = DataLoader(BehaviorDataset(X_train, y_train), batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(BehaviorDataset(X_val, y_val), batch_size=args.batch_size, shuffle=False)
    test_loader = DataLoader(BehaviorDataset(X_test, y_test), batch_size=args.batch_size, shuffle=False)

    num_classes = len(encoder.classes_)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    models = {
        "rnn": RNNNextAction(num_classes, hidden_dim=args.hidden_dim),
        "lstm": LSTMNextAction(num_classes, hidden_dim=args.hidden_dim),
        "bilstm": BiLSTMNextAction(num_classes, hidden_dim=args.hidden_dim),
    }

    results = {}
    for name, model in models.items():
        trained, loss_history, val_history = train_model(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            device=device,
            epochs=args.epochs,
            lr=args.lr,
        )
        y_true, y_pred = predict(trained.to(device), test_loader, device)
        metrics = compute_metrics(y_true, y_pred)
        results[name] = {
            "model": trained,
            "metrics": metrics,
            "loss_history": loss_history,
            "val_accuracy_history": val_history,
            "y_true": y_true,
            "y_pred": y_pred,
        }

    best_name = max(results, key=lambda n: results[n]["metrics"]["f1"])
    best = results[best_name]

    torch.save(best["model"].state_dict(), output_dir / "best_model.pt")
    save_encoder(encoder, str(output_dir / "label_encoder.pkl"))

    config = {
        "model_type": best_name,
        "window_size": args.window_size,
        "num_classes": num_classes,
        "hidden_dim": args.hidden_dim,
        "classes": encoder.classes_.tolist(),
    }
    (output_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    plot_training_loss(best["loss_history"], output_dir / "training_loss.png")
    plot_accuracy(best["val_accuracy_history"], output_dir / "accuracy.png")
    plot_confusion(best["y_true"], best["y_pred"], encoder.classes_, output_dir / "confusion_matrix.png")
    plot_model_compare(results, output_dir / "model_compare.png")

    print("Best model:", best_name)
    for name, item in results.items():
        print(name, item["metrics"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-path", default="../data/data_user500.csv")
    parser.add_argument("--output-dir", default="../ml_models")
    parser.add_argument("--window-size", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--hidden-dim", type=int, default=64)
    parser.add_argument("--lr", type=float, default=1e-3)
    main(parser.parse_args())
