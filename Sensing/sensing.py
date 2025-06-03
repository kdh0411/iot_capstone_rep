from collections import deque
import sys
import os
import serial
import time
import json
import csv
import re

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from DB.db_insert import insert_sensor_data
from emer.predict_landslide_risk import LandslidePredictor
from emer.predict_landslide_risk import LandslidePredictor
from API.send_kakao_alert import send_kakao_alert 

class SensorReceiver:
    def __init__(self, port='COM3', baudrate=9600):
        self.gps_locked = False
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.prev_data = {
            'a': 0.0, 'g': 0.0, 'n': [0.0, 0.0],
            'm': 0.0, 't': 0.0, 'l': [0.0, 0.0]
        }
        self.a_history = deque(maxlen=10)
        self.g_history = deque(maxlen=10)
        self.predictor = LandslidePredictor()
        self.warning_count = 0
        self.warning_threshold = 3  
        self.warning_limit = 5
        print(f"[✅] LoRa 수신기 연결 완료: 포트={port}, 속도={baudrate}bps")

    def safe_float(self, val, key):
        try:
            f = float(val)
            if f == 0.0 and key not in ['t']:
                raise ValueError("0은 센서 오류로 간주")
            return f
        except:
            print(f"[⚠️ 보정] {key} 값 오류 또는 0 → 이전 값 사용")
            return self.prev_data.get(key, 0.0)

    def parse_sensor_data(self, raw: str) -> dict:
        try:
            raw = re.sub(r'[;/\\]', ':', raw.strip().lower())
            required_keys = ["a:", "g:", "n:", "m:", "t:", "l:"]
            missing_keys = [k for k in required_keys if k not in raw]
            if missing_keys:
                print(f"[⚠️ 보정] 누락된 키 {missing_keys} → 이전 값 사용")

            parts = raw.split(',')
            data = {}
            i = 0
            while i < len(parts):
                if ':' in parts[i]:
                    key_val = parts[i].split(':', 1)
                    if len(key_val) != 2:
                        i += 1
                        continue
                    key, val = key_val

                    if key == 'n':
                        try:
                            n1, n2 = float(val), float(parts[i + 1])
                            if n1 == 0.0 and n2 == 0.0:
                                raise ValueError
                            data['n'] = [n1, n2]
                        except:
                            print("[⚠️ 보정] n 값 오류 또는 0 → 이전 값 사용")
                            data['n'] = self.prev_data['n']
                        i += 1

                    elif key == 'l':
                        if not self.gps_locked:
                            try:
                                l1, l2 = float(val), float(parts[i + 1])
                                if not (33 <= l1 <= 39 and 124 <= l2 <= 132):
                                    raise ValueError("위도/경도 범위 벗어남")
                                if l1 == 0.0 and l2 == 0.0:
                                    raise ValueError("좌표값 0")
                                data['l'] = [round(l1, 5), round(l2, 5)]
                                self.gps_locked = True
                                gps_path = "API/device_gps.json"
                                if not os.path.exists(gps_path):
                                    os.makedirs(os.path.dirname(gps_path), exist_ok=True)
                                    with open(gps_path, "w", encoding="utf-8") as gps_file:
                                        json.dump({"l": data['l']}, gps_file, indent=2, ensure_ascii=False)
                                    print(f"📍 GPS 위치 device_gps.json에 저장 완료: {data['l']}")
                            except:
                                print("[⚠️ 보정] l 값 오류 → 이전 값 사용")
                                data['l'] = self.prev_data['l']
                        else:
                            data['l'] = self.prev_data['l']
                        i += 1

                    elif key in ['a', 'g', 'm', 't']:
                        data[key] = self.safe_float(val, key)
                i += 1

            for k in ['a', 'g', 'n', 'm', 't', 'l']:
                if k not in data:
                    data[k] = self.prev_data[k]
                    print(f"[🧩 누락 보정] {k} → 이전 값 사용")

            if all((x == 0 or x == [0.0, 0.0]) for x in data.values()):
                raise ValueError("모든 센서값이 0")

            self.prev_data = data
            return data

        except Exception as e:
            print("❌ 파싱 오류 또는 무시된 데이터:", e)
            return {}

    def append_to_csv(self, data, csv_path='log/sensor_log_rotate.csv'):
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        file_exists = os.path.isfile(csv_path)
        with open(csv_path, mode='a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['a', 'g', 'n1', 'n2', 'm', 't', 'l1', 'l2'])
            writer.writerow([
                data['a'], data['g'], data['n'][0], data['n'][1],
                data['m'], data['t'], data['l'][0], data['l'][1]
            ])

    def receive_loop(self):
        print("[🔄] 센서 데이터 수신 중... Ctrl+C로 종료")
        try:
            while True:
                if self.ser.in_waiting:
                    raw = self.ser.readline().decode(errors='ignore').strip()
                    parsed = self.parse_sensor_data(raw)
                    if parsed:
                        print("[✅ 파싱 성공]", parsed)
                        insert_sensor_data(parsed)
                        self.append_to_csv(parsed)

                        # 👉 센서 정보만 저장
                        os.makedirs("emer", exist_ok=True)
                        with open("emer/latest_data.json", "w", encoding="utf-8") as f:
                            json.dump(parsed, f, ensure_ascii=False, indent=2)
                            
                        # 👉 위험도 예측 (latest_data.json 기반)
                        label, risk = self.predictor.predict()
                        print(f"📊 보정된 라벨: {label}단계")
                        print(f"🔥 보정된 위험도: {risk * 100:.2f}% ")

                        # 👉 연속 경고 감지 로직
                        if label >= self.warning_threshold:
                            self.warning_count += 1
                            print(f"[⚠️ 누적 위험] 현재 {self.warning_count}회 연속 위험 감지")
                            if self.warning_count >= self.warning_limit:
                                msg = f"⚠️ 산사태 위험 경고 발생!\n현재 위험도: {label}단계\n({risk * 100:.2f}%)"
                                send_kakao_alert(msg)
                                print("[📤] 카카오톡 경고 전송 완료")
                                self.warning_count = 0  # 전송 후 초기화
                        else:
                            self.warning_count = 0  # 안전 상태면 카운터 초기화
                            
                        # 위험도 정보 따로 저장
                        with open("emer/risk_data.json", "w", encoding="utf-8") as f:
                            json.dump({
                                "label": int(label),           
                                "risk": float(risk)            
                            }, f, ensure_ascii=False, indent=2)

                    else:
                        print("[⚠️ 무시됨] 잘못된 데이터 또는 파싱 실패")
                time.sleep(0.05)
 
        except KeyboardInterrupt:
            print("\n[🛑] 수신 종료됨")
        finally:
            self.ser.close()


if __name__ == "__main__":
    receiver = SensorReceiver()
    receiver.receive_loop()
