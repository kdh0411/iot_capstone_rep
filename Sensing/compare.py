import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import joblib

# ---------------- 설정 ----------------
CSV_PATH = "sensor_log_test.csv"
MODEL_PATH = "lstm_autoencoder.pt"
SCALER_PATH = "scaler.save"  # scaler 저장해놨다면
SEQUENCE_INDEX = 71
SEQUENCE_LENGTH = 10
FEATURES = ['A', 'G', 'N1', 'N2', 'M', 'T']

# ---------------- 모델 정의 ----------------
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

# ---------------- 데이터 로딩 ----------------
df = pd.read_csv(CSV_PATH)

# 스케일러 불러오기 (train_model.py에서 저장했을 경우)
# scaler = joblib.load(SCALER_PATH)

# 혹은 다시 fit() 하기 (주의: 이건 테스트용)
scaler = MinMaxScaler()
scaled = scaler.fit_transform(df[FEATURES])

def create_sequences(data, seq_len):
    return np.array([data[i:i+seq_len] for i in range(len(data) - seq_len + 1)])

sequences = create_sequences(scaled, SEQUENCE_LENGTH)
X = torch.tensor(sequences, dtype=torch.float32)

# ---------------- 모델 로드 및 복원 ----------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = LSTMAutoencoder(input_dim=6, hidden_dim=32).to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

with torch.no_grad():
    x_input = X[SEQUENCE_INDEX:SEQUENCE_INDEX+1].to(device)
    x_recon = model(x_input)

# ---------------- 비교 ----------------
actual = x_input.cpu().numpy().squeeze()
recon = x_recon.cpu().numpy().squeeze()

compare_df = pd.DataFrame()
for i, col in enumerate(FEATURES):
    compare_df[f'Actual_{col}'] = actual[:, i]
    compare_df[f'Ideal_{col}'] = recon[:, i]

# ---------------- 출력 ----------------
print(compare_df.round(4))
compare_df.to_csv("sequence71_compare.csv", index=False)
print("\n✅ 저장 완료: sequence71_compare.csv")
