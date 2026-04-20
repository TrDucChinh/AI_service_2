# Colab Training Pipeline

Train in Google Colab (recommended), not in local service containers.

## Install (Colab)

```bash
pip install torch pandas numpy scikit-learn matplotlib
```

## Run

```bash
python train.py --dataset-path ../data/data_user500.csv --output-dir ../ml_models
```

## Quick EDA

```bash
python eda_user_behavior.py
```

This exports:
- `eda_action_distribution.png`
- `eda_events_per_user.png`
- `eda_daily_events.png`

## Trained models

- `RNN`
- `LSTM`
- `biLSTM`

## Output artifacts

- `best_model.pt`
- `label_encoder.pkl`
- `config.json`
- `training_loss.png`
- `accuracy.png`
- `confusion_matrix.png`
- `model_compare.png`

The backend reads artifacts from `ml_models/`.
