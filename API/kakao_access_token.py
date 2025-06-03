import os
import requests
from dotenv import load_dotenv

# === .env 파일 로드 ===
load_dotenv()

# === 환경변수에서 값 불러오기 ===
REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")
AUTH_CODE = os.getenv("KAKAO_AUTH_CODE")

# === 유효성 검사 ===
if not all([REST_API_KEY, REDIRECT_URI, AUTH_CODE]):
    raise ValueError("❌ KAKAO 관련 환경변수가 누락되었습니다.")

# === 토큰 요청 ===
url = 'https://kauth.kakao.com/oauth/token'
data = {
    'grant_type': 'authorization_code',
    'client_id': REST_API_KEY,
    'redirect_uri': REDIRECT_URI,
    'code': AUTH_CODE,
}

response = requests.post(url, data=data)
tokens = response.json()
print("🔐 발급된 토큰 정보:", tokens)
