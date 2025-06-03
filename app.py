from flask import Flask, render_template, jsonify,request
from API.get_nearest_cctv import get_nearest_cctvs
import os
import json

app = Flask(__name__, template_folder='UI')



@app.route('/')
def home():
    return render_template('monitor.html')

#------ sensor 그래프 그리기 ----------#    
@app.route('/sensor')
def get_latest_data():
    try:
        with open("emer/latest_data.json", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "No sensor data yet"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Corrupted sensor data"}), 500


#--------cctv 가져오기 -----------#
@app.route("/cctv")
def get_cctvs():
    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))
    try:
        cctvs = get_nearest_cctvs(lat, lon, top_n=5)  # ✅ 함수 호출
        return jsonify({
            "cctv_urls": [c["cctvurl"] for c in cctvs]
        })
    except Exception as e:
        return jsonify({"error": str(e)})



#--------위험도 저장-------#
@app.route("/risk")
def get_risk_data():
    try:
        with open("emer/risk_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
