import pickle
from pathlib import Path

import numpy as np
from sklearn.preprocessing import LabelEncoder


def encode_actions(df):
    encoder = LabelEncoder()
    df = df.copy()
    df["action_encoded"] = encoder.fit_transform(df["action"].astype(str))
    return df, encoder


def build_action_sequences(df, window_size=5):
    X, y = [], []
    for _, user_df in df.groupby("user_id", sort=False):
        actions = user_df["action_encoded"].tolist()
        if len(actions) <= window_size:
            continue
        for i in range(len(actions) - window_size):
            X.append(actions[i : i + window_size])
            y.append(actions[i + window_size])
    return np.array(X), np.array(y)


def save_encoder(encoder, output_path: str):
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as f:
        pickle.dump(encoder, f)
