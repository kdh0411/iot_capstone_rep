from flask import Flask, render_template, jsonify,request
from API.get_nearest_cctv import NearestCCTVClient
import os
import json

app = Flask(__name__, template_folder='UI')

cctv_client = NearestCCTVClient(api_key="b8d6f8a5aea94ae695efbb35fc540965")

@app.route('/')
def home():
    return render_template('monitor.html')

#------ sensor 그래프 그리기 ----------#    
@app.route('/sensor')
def get_latest_data():
    try:
        with open("latest_data.json", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "No sensor data yet"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Corrupted sensor data"}), 500

#--------cctv 가져오기 -----------#
@app.route("/cctv")
def get_cctv():
    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))
    try:
        data = cctv_client.get_nearest_cctv(lat, lon)
        return jsonify({
            "cctv_name": data['cctvname'],
            "cctv_url": data['cctvurl']
        })
    except Exception as e:
        return jsonify({"error": str(e)})
    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
