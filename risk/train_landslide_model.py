# train_landslide_model.py (5단계 라벨 학습 + 위험도 점수 출력)
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import classification_report

# === [1] 데이터 로딩 ===
df = pd.read_csv("emer/landslide_data.csv")  # 5단계 라벨 데이터

# === [2] 데이터 증강 함수 정의 ===
def augment_data(df, n_copies=10, noise_level=0.07):  # ← 5배 증강
    augmented = []
    for _ in range(n_copies):
        noisy = df.copy()
        noisy[['A', 'G', 'N1', 'N2', 'M', 'T']] += np.random.normal(
            0, noise_level, size=noisy[['A', 'G', 'N1', 'N2', 'M', 'T']].shape)
        augmented.append(noisy)
    return pd.concat(augmented, ignore_index=True)

# === [3] 클래스별 증강 적용 ===
augmented_parts = []
for label in df['label'].unique():
    part = df[df['label'] == label]
    augmented = augment_data(part, n_copies=5, noise_level=0.03)
    augmented_parts.append(augmented)

df_augmented = pd.concat([df] + augmented_parts, ignore_index=True)

# === [4] 입력 피처 및 라벨 지정 ===
X = df_augmented[['A', 'G', 'N1', 'N2', 'M', 'T']]
y = df_augmented['label']

# === [5] 학습/테스트 분리 ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === [6] 모델 정의: 정규화 + XGBoost ===
pipeline = Pipeline([
    ('scaler', MinMaxScaler()),
    ('xgb', xgb.XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=4,
        use_label_encoder=False,
        objective='multi:softprob',
        num_class=5,
        eval_metric='mlogloss'
    ))
])

# === [7] 학습 ===
pipeline.fit(X_train, y_train)

# === [7-1] 스케일러 저장 ===
joblib.dump(pipeline.named_steps['scaler'], 'emer/scaler.save')
print("✅ 스케일러 저장 완료: emer/scaler.save")

# === [7-2] 과적합 여부 확인 ===
from sklearn.metrics import accuracy_score


    
# === [8] 예측 및 위험도 점수 계산 ===
y_pred = pipeline.predict(X_test)
y_proba = pipeline.predict_proba(X_test)

# 훈련 데이터 성능
y_train_pred = pipeline.predict(X_train)
train_acc = accuracy_score(y_train, y_train_pred)
print(f"\n[훈련 정확도] {train_acc * 100:.2f}%")

# 테스트 데이터 성능
test_acc = accuracy_score(y_test, y_pred)
print(f"[테스트 정확도] {test_acc * 100:.2f}%")

# 차이 확인
gap = train_acc - test_acc
print(f"[과적합 확인] 훈련-테스트 정확도 차이: {gap * 100:.2f}%")
if gap > 0.1:
    print("⚠️ 과적합 의심: 일반화 성능이 낮을 수 있음")
else:
    print("✅ 과적합 없음 또는 경미함")

# 위험도 점수 맵: label 0~4 → 0.00 ~ 1.00
# 기존
#risk_map = {0: 0.00, 1: 0.25, 2: 0.50, 3: 0.75, 4: 1.00}

# 보수적 조정 예 (100%는 실제 산사태에서만 나오도록 제한)
risk_map = {0: 0.00, 1: 0.3, 2: 0.55, 3: 0.85, 4: 0.99}

risk_scores = [sum(p[i] * risk_map[i] for i in range(5)) for p in y_proba]

# === [9] 성능 평가 출력 ===
print("\n[검증 결과 보고서]")
print(classification_report(y_test, y_pred))

# 라벨별 정확도
print("\n[클래스별 정확도]")
labels = [0, 1, 2, 3, 4]
for label in labels:
    correct = np.sum((y_test == label) & (y_pred == label))
    total = np.sum(y_test == label)
    acc = correct / total if total > 0 else 0
    print(f"라벨 {label} 정확도: {acc * 100:.2f}% ({correct}/{total})")

# === [10] 라벨별 평균 산사태 위험도 점수 출력 ===
print("\n[라벨별 평균 산사태 위험도 (%)]")
for label in labels:
    indices = np.where(y_test.values == label)[0]
    if len(indices) > 0:
        avg_risk = np.mean([risk_scores[i] for i in indices]) * 100
        print(f"라벨 {label} 평균 위험도: {avg_risk:.2f}%")
    else:
        print(f"라벨 {label} 샘플 없음")



# === [11] 피처 중요도 출력 ===
print("\n[피처별 중요도]")
feature_names = ['A', 'G', 'N1', 'N2', 'M', 'T']
importances = pipeline.named_steps['xgb'].feature_importances_
for name, score in zip(feature_names, importances):
    print(f"{name}: {score:.4f}")

# === [12] 모델 저장 ===
pipeline.named_steps['xgb'].save_model("emer/landslide_model.json")
print("\n✅ 모델 저장 완료: landslide_model.json")
