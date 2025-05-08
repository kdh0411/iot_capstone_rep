import sys
import os
import serial
import time
import json
import csv
import numpy as np

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from DB.db_insert import insert_sensor_data
from predict_risk_denseae import compute_risk_dense

class SensorReceiver:
    def __init__(self, port='COM4', baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.prev_data = {'A': 0.0, 'G': 0.0, 'N': [0.0, 0.0], 'M': 0.0, 'T': 0.0, 'L': [0.0, 0.0]}
        print(f"[✅] LoRa 수신기 연결 완료: 포트={port}, 속도={baudrate}bps")

    def safe_float(self, val, key):
        try:
            f = float(val)
            if f == 0.0 and key not in ['T']:  # 지온은 0도 허용
                raise ValueError("0은 센서 오류로 간주")
            return f
        except:
            print(f"[⚠️ 보정] {key} 값 오류 또는 0 → 이전 값 사용")
            return self.prev_data.get(key, 0.0)

    def parse_sensor_data(self, raw: str) -> dict:
        try:
            if not all(k in raw for k in ["A:", "G:", "N:", "M:", "T:", "L:"]):
                raise ValueError("필수 키 누락")

            parts = raw.strip().split(',')
            data = {}
            i = 0
            while i < len(parts):
                if ':' in parts[i]:
                    key_val = parts[i].split(':', 1)
                    if len(key_val) != 2:
                        i += 1
                        continue
                    key, val = key_val

                    if key == 'N':
                        try:
                            n1, n2 = float(val), float(parts[i + 1])
                            if n1 == 0.0 and n2 == 0.0:
                                raise ValueError
                            data['N'] = [n1, n2]
                        except:
                            print("[⚠️ 보정] N 값 오류 또는 0 → 이전 값 사용")
                            data['N'] = self.prev_data['N']
                        i += 1

                    elif key == 'L':
                        try:
                            l1, l2 = float(val), float(parts[i + 1])
                            if l1 == 0.0 and l2 == 0.0:
                                raise ValueError
                            data['L'] = [l1, l2]
                        except:
                            print("[⚠️ 보정] L 값 오류 또는 0 → 이전 값 사용")
                            data['L'] = self.prev_data['L']
                        i += 1

                    elif key in ['A', 'G', 'M', 'T']:
                        data[key] = self.safe_float(val, key)
                i += 1

            if not all(k in data for k in ['A', 'G', 'N', 'M', 'T', 'L']):
                raise ValueError("최종 누락 필드 있음")

            if all((x == 0 or x == [0.0, 0.0]) for x in data.values()):
                raise ValueError("모든 센서값이 0")

            self.prev_data = data
            return data

        except Exception as e:
            print("❌ 파싱 오류 또는 무시된 데이터:", e)
            return {}

    def append_to_csv(self, data, csv_path='log/sensor_log.csv'):
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        file_exists = os.path.isfile(csv_path)
        with open(csv_path, mode='a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['A', 'G', 'N1', 'N2', 'M', 'T'])
            writer.writerow([
                data['A'], data['G'], data['N'][0], data['N'][1], data['M'], data['T']
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

                        with open("latest_data.json", "w") as f:
                            json.dump(parsed, f, ensure_ascii=False, indent=2)

                        input_1x6 = [parsed['A'], parsed['G'], parsed['N'][0], parsed['N'][1], parsed['M'], parsed['T']]
                        risk = compute_risk_dense(input_1x6)
                        #print(f"⚠️ 실시간 위험도 (Dense AE): {risk}%")
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
