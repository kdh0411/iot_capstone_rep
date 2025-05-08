import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt

# 1. 하이퍼파라미터
SEQUENCE_LENGTH = 10
BATCH_SIZE = 32
HIDDEN_DIM = 32
EPOCHS = 20
LEARNING_RATE = 0.001
CSV_PATH = "sensor_log.csv"

# 2. 데이터 불러오기
df = pd.read_csv(CSV_PATH)
features = ['A', 'G', 'N1', 'N2', 'M', 'T']
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df[features])

# 3. 시계열 시퀀스 생성
def create_sequences(data, seq_len):
    sequences = []
    for i in range(len(data) - seq_len + 1):
        sequences.append(data[i:i+seq_len])
    return np.array(sequences)

sequences = create_sequences(scaled_data, SEQUENCE_LENGTH)
X = torch.tensor(sequences, dtype=torch.float32)
dataset = TensorDataset(X)
loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

# 4. 모델 정의
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

# 5. 학습
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = LSTMAutoencoder(input_dim=6, hidden_dim=HIDDEN_DIM).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
criterion = nn.MSELoss()

for epoch in range(EPOCHS):
    model.train()
    epoch_loss = 0
    for batch in loader:
        x_batch = batch[0].to(device)
        optimizer.zero_grad()
        output = model(x_batch)
        loss = criterion(output, x_batch)
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()
    print(f"[{epoch+1}/{EPOCHS}] Loss: {epoch_loss/len(loader):.6f}")

# 6. 위험도 예측
model.eval()
with torch.no_grad():
    x_test = X.to(device)
    x_pred = model(x_test)
    errors = torch.mean((x_pred - x_test) ** 2, dim=(1, 2)).cpu().numpy()

# 7. 위험도 정규화 (0~100%)
threshold = np.percentile(errors, 95)
risk_percent = np.clip((errors / threshold) * 100, 0, 100)

torch.save(model.state_dict(), "lstm_autoencoder.pt")
print("모델 저장 완료: lstm_autoencoder.pt")

# 8. 그래프 출력
plt.figure(figsize=(12, 5))
plt.plot(risk_percent)
plt.title("Landslide Risk Prediction (%)")
plt.ylabel("Risk (%)")
plt.xlabel("Time Step")
plt.grid()
plt.tight_layout()
plt.savefig("risk_plot.png")
plt.show()
