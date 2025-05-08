import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# --------------------------
# 1. 모델 정의
# --------------------------
class LSTMAutoencoder(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super().__init__()
        self.encoder = nn.LSTM(input_dim, hidden_dim, batch_first=True)
        self.decoder = nn.LSTM(hidden_dim, input_dim, batch_first=True)

    def forward(self, x):
        _, (h, _) = self.encoder(x)
        dec_input = h.repeat(x.size(1), 1, 1).permute(1, 0, 2)
        out, _ = self.decoder(dec_input)
        return out

# --------------------------
# 2. 설정
# --------------------------
SEQUENCE_LENGTH = 10
CSV_PATH = "sensor_log_test.csv"
MODEL_PATH = "lstm_autoencoder.pt"
FEATURES = ['A', 'G', 'N1', 'N2', 'M', 'T']

# --------------------------
# 3. 데이터 불러오기 및 전처리
# --------------------------
df = pd.read_csv(CSV_PATH)
scaler = MinMaxScaler()
scaled = scaler.fit_transform(df[FEATURES])

# 시퀀스 분할
def create_sequences(data, seq_len):
    return np.array([data[i:i+seq_len] for i in range(len(data) - seq_len + 1)])

sequences = create_sequences(scaled, SEQUENCE_LENGTH)
X = torch.tensor(sequences, dtype=torch.float32)

# --------------------------
# 4. 모델 로드 및 예측
# --------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = LSTMAutoencoder(input_dim=6, hidden_dim=32).to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

with torch.no_grad():
    x_input = X.to(device)
    x_output = model(x_input)
    errors = torch.mean((x_output - x_input) ** 2, dim=(1, 2)).cpu().numpy()

# --------------------------
# 5. 위험도 계산 및 출력
# --------------------------
threshold = np.percentile(errors, 99)
risks = np.clip((errors / threshold) * 100, 0, 100)

for i, risk in enumerate(risks):
    alert = "⚠️ 위험" if risk > 80 else "✅ 정상"
    print(f"[{i:03}] 위험도: {risk:.1f}% {alert}")
