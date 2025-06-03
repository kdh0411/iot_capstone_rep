# emer/predict_landslide_risk.py

import json
import numpy as np
import xgboost as xgb
import joblib
import pandas as pd  
class LandslidePredictor:
    def __init__(self, model_path="emer/landslide_model.json", scaler_path="emer/scaler.save"):
        self.model = xgb.XGBClassifier()
        self.model.load_model(model_path)

        self.scaler = joblib.load(scaler_path)
        self.risk_map = {0: 0.00, 1: 0.28, 2: 0.65, 3: 0.85, 4: 0.99}

    def load_input_data(self, json_path="emer/latest_data.json"):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return np.array([[data["a"], data["g"], data["n"][0], data["n"][1], data["m"], data["t"]]])



    def predict(self):
        input_data = self.load_input_data()
        df = pd.DataFrame(input_data, columns=["A", "G", "N1", "N2", "M", "T"])  # ✨ feature 이름 추가
        scaled = self.scaler.transform(df)
        proba = self.model.predict_proba(scaled)[0]
        label = np.argmax(proba)
        risk_score = sum(p * self.risk_map[i] for i, p in enumerate(proba))

        m_value = df["M"].iloc[0]
        if m_value < 240 and risk_score < 0.28:
            risk_score = 0.2853

        return label, risk_score


# =========================
# ✅ 테스트 실행 코드
# =========================
if __name__ == "__main__":
    import pandas as pd

    predictor = LandslidePredictor()

    csv_path = "log/sensor_log.csv"  # 너가 말한 파일 위치
    df = pd.read_csv(csv_path, header=None)  # 헤더 없음 주의
    df.columns = ["a", "g", "n1", "n2", "m", "t", "l1", "l2"]  # 컬럼 수동 지정

    print("\n[🚨 테스트 데이터 위험도 예측 결과]\n")
    for i, row in df.iterrows():
        input_array = np.array([[row["a"], row["g"], row["n1"], row["n2"], row["m"], row["t"]]])
        try:
            input_df = pd.DataFrame(input_array, columns=["A", "G", "N1", "N2", "M", "T"])
            scaled = predictor.scaler.transform(input_df)
            proba = predictor.model.predict_proba(scaled)[0]
            label = np.argmax(proba)
            risk_score = sum(p * predictor.risk_map[i] for i, p in enumerate(proba))
            print(f"[{i}] 📌 라벨: {label}, 🔥 위험도: {risk_score * 100:.2f}%")
        except Exception as e:
            print(f"[{i}] ❌ 예측 실패: {e}")

