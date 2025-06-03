import os
import json
import requests
from dotenv import load_dotenv

# === .env 파일 로드 ===
load_dotenv()

def send_kakao_alert(message):
    access_token = os.getenv("KAKAO_ACCESS_TOKEN")
    if not access_token:
        raise ValueError("❌ KAKAO_ACCESS_TOKEN 환경변수가 설정되지 않았습니다.")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "template_object": {
            "object_type": "text",
            "text": message,
            "link": {
                "web_url": "http://127.0.0.1:5000",
                "mobile_web_url": "http://127.0.0.1:5000"
            },
            "button_title": "상세보기"
        }
    }

    res = requests.post(
        "https://kapi.kakao.com/v2/api/talk/memo/default/send",
        headers=headers,
        data={"template_object": json.dumps(data["template_object"])}
    )

    print("카카오톡 전송 결과:", res.status_code, res.text)

# 테스트 실행
if __name__ == "__main__":
    send_kakao_alert("✅ 테스트 메시지입니다. 산사태 감지 시스템에서 보낸 경고입니다.")
