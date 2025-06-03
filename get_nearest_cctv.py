import os
import requests
import numpy as np
from dotenv import load_dotenv

# === .env 파일 로드 ===
load_dotenv()

def get_nearest_cctvs(lat, lng, top_n=5):
    # === CCTV API 키 로드 ===
    api_key = os.getenv("CCTV_API_KEY")
    if not api_key:
        raise ValueError("❌ CCTV_API_KEY 환경변수가 설정되지 않았습니다.")

    # CCTV 탐색 범위 ±1도 (약 111km)
    minX = str(lng - 1)
    maxX = str(lng + 1)
    minY = str(lat - 1)
    maxY = str(lat + 1)

    # API 호출 URL 구성
    api_call = (
        'https://openapi.its.go.kr:9443/cctvInfo?'
        f'apiKey={api_key}'
        '&type=its'
        '&cctvType=2'
        f'&minX={minX}&maxX={maxX}&minY={minY}&maxY={maxY}'
        '&getType=json'
    )

    # API 요청
    response = requests.get(api_call)
    if response.status_code != 200:
        raise Exception(f"❌ API 요청 실패: {response.status_code} - {response.text}")
    
    w_dataset = response.json()
    cctv_data = w_dataset['response'].get('data', [])

    if not cctv_data:
        raise Exception("❌ CCTV 데이터 없음")

    # 좌표 거리 계산
    coord_list = [(float(item['coordy']), float(item['coordx'])) for item in cctv_data]
    coord_array = np.array(coord_list)
    input_coord = np.array([lat, lng])
    distances = np.linalg.norm(coord_array - input_coord, axis=1)
    top_indices = distances.argsort()[:top_n]

    # 가장 가까운 CCTV top_n개 반환
    return [cctv_data[i] for i in top_indices]

# === 실행 예시 ===
if __name__ == "__main__":
    lat, lon = 37.63696, 128.49502
    try:
        cctvs = get_nearest_cctvs(lat, lon, top_n=5)
        print("📹 가까운 CCTV 5개:")
        for i, cctv in enumerate(cctvs, 1):
            print(f"{i}. 📍 이름: {cctv['cctvname']}")
            print(f"   🔗 URL: {cctv['cctvurl']}")
    except Exception as e:
        print(str(e))

## 이거 링크를 주기적으로 받아와야 할듯 url 접근 시 30초 제한.  
## ex로 설정하면 그럴듯한데, itc로 가면, 말도안된다.  
# lat, lon = 37.641510, 128.517842 # 평창
 
   #  lat, lon = 37.58208, 127.00960

   # lat, lon = 37.63696, 128.49502 최적좌표 
    