import torch.nn as nn


class RNNNextAction(nn.Module):
    def __init__(self, num_classes, embed_dim=16, hidden_dim=64):
        super().__init__()
        self.embedding = nn.Embedding(num_classes, embed_dim)
        self.rnn = nn.RNN(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        x = self.embedding(x)
        out, _ = self.rnn(x)
        return self.fc(out[:, -1, :])
