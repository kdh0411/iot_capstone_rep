import os
import requests
from dotenv import load_dotenv

# === .env 파일 로드 ===
load_dotenv()

# === 환경변수에서 값 불러오기 ===
REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
REFRESH_TOKEN = os.getenv("KAKAO_REFRESH_TOKEN")

# === 유효성 검사 ===
if not all([REST_API_KEY, REFRESH_TOKEN]):
    raise ValueError("❌ KAKAO_REFRESH 관련 환경변수가 누락되었습니다.")

# === 토큰 갱신 요청 ===
url = 'https://kauth.kakao.com/oauth/token'
data = {
    'grant_type': 'refresh_token',
    'client_id': REST_API_KEY,
    'refresh_token': REFRESH_TOKEN
}

response = requests.post(url, data=data)
tokens = response.json()
print("🔄 갱신된 토큰 정보:", tokens)
