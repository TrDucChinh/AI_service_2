import torch.nn as nn


class BiLSTMNextAction(nn.Module):
    def __init__(self, num_classes, embed_dim=16, hidden_dim=64):
        super().__init__()
        self.embedding = nn.Embedding(num_classes, embed_dim)
        self.bilstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, num_classes)

    def forward(self, x):
        x = self.embedding(x)
        out, _ = self.bilstm(x)
        return self.fc(out[:, -1, :])
