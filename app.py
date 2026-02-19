from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv

# Import services
from services.groq_crop_analysis import analyze_crop_with_groq
from services.weather_service import get_recent_weather
from services.market_service import get_market_prices

load_dotenv()
app = Flask(__name__)
CORS(app)

DATA_FILE = "last_scan.json"
UPLOAD_FOLDER = "stored_crops"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ========================
# 1. CROP ANALYSIS (Groq Vision AI)
# ========================
@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        
        # Save the uploaded image
        filename = f"crop_{len(os.listdir(UPLOAD_FOLDER)) + 1}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        print(f"[AgriShield] Image saved: {filepath}")

        # Analyze with Groq Vision AI
        analysis_data = analyze_crop_with_groq(filepath)

        if "error" in analysis_data:
            return jsonify({"status": "Error", "error": analysis_data["error"]}), 500

        # Save result for home page
        with open(DATA_FILE, 'w') as f:
            json.dump(analysis_data, f, indent=2)

        return jsonify({
            "status": "Success",
            "data": analysis_data,
            "confidence": analysis_data.get("confidence", 0)
        })

    except Exception as e:
        print(f"[AgriShield] Server Error: {e}")
        return jsonify({"error": str(e)}), 500


# ========================
# 2. LAST SCAN (Home Page)
# ========================
@app.route('/last-scan', methods=['GET'])
def get_last_scan():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return jsonify({"status": "Success", "data": json.load(f)})
    return jsonify({"error": "No scan found"})


# ========================
# 3. WEATHER ADVISORY (NASA POWER API)
# ========================
@app.route('/weather-advisory', methods=['GET'])
def weather_advisory():
    try:
        lat = request.args.get('lat', '22.7196')
        lon = request.args.get('lon', '75.8577')
        
        weather_data = get_recent_weather(float(lat), float(lon))
        return jsonify(weather_data)
    except Exception as e:
        print(f"[AgriShield] Weather Error: {e}")
        return jsonify({"error": str(e)}), 500


# ========================
# 4. MANDI PRICES (SerpAPI)
# ========================
@app.route('/mandi-prices', methods=['GET'])
def mandi_prices():
    try:
        prices = get_market_prices()
        return jsonify(prices)
    except Exception as e:
        print(f"[AgriShield] Market Error: {e}")
        return jsonify({"error": str(e)}), 500


# ========================
# 5. HEALTH CHECK
# ========================
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "AgriShield AI Backend Running",
        "version": "2.0",
        "endpoints": ["/predict", "/last-scan", "/weather-advisory", "/mandi-prices"]
    })


if __name__ == '__main__':
    print("=" * 50)
    print("  AgriShield AI Backend v2.0")
    print("  Powered by Groq Vision AI")
    print("=" * 50)
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 5000)),
        debug=True
    )