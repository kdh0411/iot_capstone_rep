# 🌍 IoT 기반 산사태 감지 시스템

**2025 캡스톤디자인 프로젝트 - 사물인터넷트랙**  
IoT 센서를 활용하여 산사태 위험을 실시간으로 감지하고, 웹 기반으로 시각화하는 시스템입니다.

---

## 📦 프로젝트 개요

이 프로젝트는 다양한 환경 센서를 활용하여 산사태 징후를 조기에 감지하고,  
LoRa 통신을 통해 원거리에서 수집한 데이터를 서버로 전송하여 시각화 및 저장하는 IoT 기반 시스템입니다.

---

## 🧩 시스템 구성도

- **센서 노드 (Arduino nano)**
  - 기울기 센서: `MPU6050`
  - 진동 센서: `Grove - Piezo Vibration Sensor`
  - 토양 수분 센서: `Grove - Capacitive Soil Moisture Sensor`
  - 지온 센서: `Grove - DS18B20`
  - GPS 모듈: `GPS GY-NEO6MV2`
  - 통신: `LoRa (REYAX RYLR998)`

- **수신 랩탑 (P2P)**
  - Flask 기반 웹 서버
  - SQLite3 DB 저장
  - 실시간 지도 시각화 (HTML + JS)

---
### 🖼️ 디바이스 구성도

![디바이스 구성도](https://private-user-images.githubusercontent.com/138554661/450804851-ac6a0688-be6d-4f27-ae64-e7569bbd490e.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDg5NTYzMDMsIm5iZiI6MTc0ODk1NjAwMywicGF0aCI6Ii8xMzg1NTQ2NjEvNDUwODA0ODUxLWFjNmEwNjg4LWJlNmQtNGYyNy1hZTY0LWU3NTY5YmJkNDkwZS5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNjAzJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDYwM1QxMzA2NDNaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1kMzhjNDhjMTZhMjQ1MTc1M2ViODZjMGU0M2QzZDVjZTgxOWVjY2I3ZGNiYzhhYjg4NWU4MDA1ZmM3MDZiZWQ0JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.qS7ZSr3Ng0nOaDmHkNUl39ENw3kez9X09KB5WIj1PS4)
---

## 📁 디렉토리 구조
- **git 코드 참고**


---

## 🧠 주요 기능

- 🌐 **LoRa 기반 원거리 통신**
- 📉 **센서 데이터 실시간 수신**
- 🌡️ **환경 정보 시각화 (지도 기반)**
- 🧠 **센서 데이터 기반 위험도 판단**

---

