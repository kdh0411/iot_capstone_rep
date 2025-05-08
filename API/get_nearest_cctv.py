import requests
import numpy as np

class NearestCCTVClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://openapi.its.go.kr:9443/cctvInfo"

    def get_nearest_cctv(self, lat, lon, delta=1.0):
        minX = lon - delta
        maxX = lon + delta
        minY = lat - delta
        maxY = lat + delta

        params = {
            "apiKey": self.api_key,
            "type": "ex",
            "cctvType": "2",
            "minX": str(minX),
            "maxX": str(maxX),
            "minY": str(minY),
            "maxY": str(maxY),
            "getType": "json"
        }

        response = requests.get(self.base_url, params=params)
        data = response.json()

        try:
            cctv_data = data['response']['data']
        except (KeyError, TypeError):
            raise Exception("❌ CCTV 데이터 응답 형식 이상 or CCTV 없음")

        if not cctv_data:
            raise Exception("❌ 해당 범위 내 CCTV 없음")

        coords = np.array([(float(item['coordy']), float(item['coordx'])) for item in cctv_data])
        input_coord = np.array([lat, lon])
        distances = np.linalg.norm(coords - input_coord, axis=1)
        nearest_idx = np.argmin(distances)
        return cctv_data[nearest_idx]

# 실행 예시
if __name__ == "__main__":
    api_key = "b8d6f8a5aea94ae695efbb35fc540965"  # 너 인증키
    lat, lon =  37.58284829999999, 127.0105811  # 테스트 좌표

    client = NearestCCTVClient(api_key)
    nearest_cctv = client.get_nearest_cctv(lat, lon)

    print("📹 가장 가까운 CCTV명:", nearest_cctv['cctvname'])
    print("🔗 영상 URL:", nearest_cctv['cctvurl'])
