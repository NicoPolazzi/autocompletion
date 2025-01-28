import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
import torch


class AutocompleteModel(nn.Module):
    def __init__(
        self, input_size: int, hidden_size: int, output_size: int, num_layers: int = 2, dropout: float = 0.2
    ) -> None:
        super(AutocompleteModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size,
            hidden_size,
            num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
        )
        self.layer_norm = nn.LayerNorm(hidden_size)
        self.attention = _AttentionLayer(hidden_size)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x: Tensor) -> Tensor:
        batch_size = x.size(0)
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(x.device)

        lstm_out, _ = self.lstm(x, (h0, c0))
        normalized = self.layer_norm(lstm_out)
        attended = self.attention(normalized)
        out = self.fc(attended)

        return out


class _AttentionLayer(nn.Module):
    def __init__(self, hidden_size: int) -> None:
        super().__init__()
        self.attention = nn.Linear(hidden_size, 1)

    def forward(self, x: Tensor) -> Tensor:
        attention_weights = F.softmax(self.attention(x), dim=1)
        return torch.sum(attention_weights * x, dim=1)
