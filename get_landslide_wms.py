import requests
import folium
from folium.raster_layers import ImageOverlay
from branca.element import MacroElement
from jinja2 import Template

class HideAttribution(MacroElement):
    def __init__(self):
        super().__init__()
        self._template = Template("""
            <style>
                .leaflet-control-attribution {
                    display: none !important;
                }
            </style>
        """)

class LandslideWMSClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://www.safemap.go.kr/openApiService/wms/getLayerData.do"

    def download_image(self, bbox, width=1024, height=1024, filename="risk_map.png"):
        params = {
            "service": "WMS",
            "request": "GetMap",
            "version": "1.1.1",
            "layers": "A2SM_SANSATAI",
            "styles": "",
            "format": "image/png",
            "transparent": "true",
            "bbox": bbox,
            "width": width,
            "height": height,
            "srs": "EPSG:4326",
            "apikey": self.api_key
        }

        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"🗺️ 지도 이미지 저장 완료: {filename}")
        else:
            raise Exception(f"WMS 요청 실패: {response.status_code} - {response.text}")

    def show_on_folium(self, bbox, filename="risk_map.png", output_html="folium_risk_map.html"):
        bbox_vals = list(map(float, bbox.split(",")))
        bounds = [[bbox_vals[1], bbox_vals[0]], [bbox_vals[3], bbox_vals[2]]]
        center_lat = (bbox_vals[1] + bbox_vals[3]) / 2
        center_lon = (bbox_vals[0] + bbox_vals[2]) / 2

        m = folium.Map(location=[center_lat, center_lon], zoom_start=6)

        ImageOverlay(
            image=filename,
            bounds=bounds,
            opacity=0.6,
            interactive=True,
            cross_origin=False
        ).add_to(m)

        # Attribution 문구 제거
        m.get_root().add_child(HideAttribution())

        m.save(output_html)
        print(f"✅ folium 지도 저장 완료: {output_html}")


# 실행 예시
if __name__ == "__main__":
    api_key = "LD5IPUBU-LD5I-LD5I-LD5I-LD5IPUBU70"
    bbox = "124.5,33.0,131.0,38.5"  # 남한 전체
    client = LandslideWMSClient(api_key)
    client.download_image(bbox)
    client.show_on_folium(bbox)
