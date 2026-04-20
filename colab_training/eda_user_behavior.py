from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def run_eda(dataset_path="../data/data_user500.csv", output_dir="../ml_models"):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(dataset_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    print("Rows:", len(df))
    print("Users:", df["user_id"].nunique())
    print("Actions:", sorted(df["action"].dropna().unique().tolist()))
    print(df.head())

    action_counts = df["action"].value_counts().sort_values(ascending=False)
    plt.figure(figsize=(8, 4))
    action_counts.plot(kind="bar")
    plt.title("Action Distribution")
    plt.tight_layout()
    plt.savefig(output / "eda_action_distribution.png")
    plt.close()

    events_per_user = df.groupby("user_id").size()
    plt.figure(figsize=(8, 4))
    events_per_user.hist(bins=20)
    plt.title("Events Per User")
    plt.xlabel("Events")
    plt.ylabel("Users")
    plt.tight_layout()
    plt.savefig(output / "eda_events_per_user.png")
    plt.close()

    daily_events = df.set_index("timestamp").resample("D").size()
    plt.figure(figsize=(10, 4))
    daily_events.plot()
    plt.title("Daily Events")
    plt.tight_layout()
    plt.savefig(output / "eda_daily_events.png")
    plt.close()

    print("EDA plots saved to", output)


if __name__ == "__main__":
    run_eda()
