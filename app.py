from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv

# Import services
from services.groq_crop_analysis import analyze_crop_with_groq
from services.weather_service import get_recent_weather
from services.market_service import get_market_prices
from services.govt_schemes_service import get_government_schemes
from services.groq_soil_analysis import analyze_soil_image, get_plant_recommendations, get_crop_recommendations

# Import Twilio services
from services.smart_alerts import (
    check_and_trigger_crop_alerts,
    check_and_trigger_soil_alerts,
    check_and_trigger_weather_alerts,
    send_manual_alert,
    get_alert_history,
)
# ⚠️ COMMENTED OUT — Twilio disabled
# from services.twilio_voice_handler import (
#     generate_welcome_twiml,
#     handle_voice_input,
#     generate_alert_call_twiml,
# )

load_dotenv()
app = Flask(__name__)
CORS(app)

DATA_FILE = "last_scan.json"
UPLOAD_FOLDER = "stored_crops"
SOIL_UPLOAD_FOLDER = "stored_soil"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SOIL_UPLOAD_FOLDER, exist_ok=True)


# ========================
# 1. CROP ANALYSIS (Groq Vision AI) + Auto Twilio Alert
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

        # 🔔 AUTO SMART ALERT — Twilio triggers automatically
        alert_result = {"skipped": True}
        try:
            alert_result = check_and_trigger_crop_alerts(analysis_data)
            print(f"[AgriShield] 🔔 Alert triggered: {alert_result.get('alert_level', 'NONE')}")
        except Exception as alert_err:
            print(f"[AgriShield] ⚠️ Alert error (non-blocking): {alert_err}")

        return jsonify({
            "status": "Success",
            "data": analysis_data,
            "confidence": analysis_data.get("confidence", 0),
            "alert": alert_result,
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
        
        # 🔔 AUTO SMART ALERT for weather
        weather_alert = {"skipped": True}
        try:
            weather_alert = check_and_trigger_weather_alerts(weather_data)
            print(f"[AgriShield] 🌦️ Weather alert: {weather_alert.get('alert_level', 'NONE')}")
        except Exception as alert_err:
            print(f"[AgriShield] ⚠️ Weather alert error (non-blocking): {alert_err}")
        
        weather_data["alert"] = weather_alert
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
# 4B. GOVERNMENT SCHEMES (SerpAPI)
# ========================
@app.route('/govt-schemes', methods=['GET'])
def govt_schemes():
    try:
        schemes = get_government_schemes()
        return jsonify({"status": "Success", "data": schemes})
    except Exception as e:
        print(f"[AgriShield] Govt Schemes Error: {e}")
        return jsonify({"error": str(e)}), 500


# ========================
# 5. SOIL ANALYSIS + Auto Twilio Alert
# ========================
@app.route('/analyze-soil', methods=['POST'])
def analyze_soil():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        file = request.files['file']
        filename = f"soil_{len(os.listdir(SOIL_UPLOAD_FOLDER)) + 1}.jpg"
        filepath = os.path.join(SOIL_UPLOAD_FOLDER, filename)
        file.save(filepath)
        print(f"[AgriShield] Soil image saved: {filepath}")
        result = analyze_soil_image(filepath)
        if "error" in result:
            return jsonify({"status": "Error", "error": result["error"]}), 500
        
        # 🔔 AUTO SMART ALERT for soil
        alert_result = {"skipped": True}
        try:
            alert_result = check_and_trigger_soil_alerts(result)
            print(f"[AgriShield] 🔔 Soil alert sent")
        except Exception as alert_err:
            print(f"[AgriShield] ⚠️ Soil alert error (non-blocking): {alert_err}")
        
        return jsonify({"status": "Success", "data": result, "alert": alert_result})
    except Exception as e:
        print(f"[AgriShield] Soil Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/soil-plant-recommendations', methods=['POST'])
def soil_plant_recs():
    try:
        soil_data = request.get_json()
        result = get_plant_recommendations(soil_data)
        if "error" in result:
            return jsonify({"status": "Error", "error": result["error"]}), 500
        return jsonify({"status": "Success", "data": result["plants"]})
    except Exception as e:
        print(f"[AgriShield] Plant Rec Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/soil-crop-recommendations', methods=['POST'])
def soil_crop_recs():
    try:
        import json as jlib
        soil_data = jlib.loads(request.form.get('soil_data', '{}'))
        season = request.form.get('season', None)  # winter / summer / rainy
        field_files = request.files.getlist('field_images')
        if len(field_files) < 3:
            return jsonify({"error": "Minimum 3 field photos required"}), 400
        saved_paths = []
        for i, f in enumerate(field_files):
            fp = os.path.join(SOIL_UPLOAD_FOLDER, f"field_{i+1}.jpg")
            f.save(fp)
            saved_paths.append(fp)
        result = get_crop_recommendations(soil_data, saved_paths, season=season)
        if "error" in result:
            return jsonify({"status": "Error", "error": result["error"]}), 500
        return jsonify({"status": "Success", "data": result["crops"]})
    except Exception as e:
        print(f"[AgriShield] Crop Rec Error: {e}")
        return jsonify({"error": str(e)}), 500


# ========================
# 6. TWILIO SMART ALERTS
# ========================
@app.route('/send-alert', methods=['POST'])
def send_alert():
    """Manually trigger a Twilio alert (for testing)."""
    try:
        data = request.get_json() or {}
        message = data.get("message", "🌾 AgriShield AI Test Alert - System working!")
        level = data.get("level", "INFO")
        
        result = send_manual_alert(message, level)
        return jsonify({"status": "Success", "alert": result})
    except Exception as e:
        print(f"[AgriShield] Alert Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/alert-history', methods=['GET'])
def alert_history():
    """Get recent alert history."""
    try:
        limit = int(request.args.get('limit', 50))
        history = get_alert_history(limit)
        return jsonify({"status": "Success", "data": history, "count": len(history)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========================
# 7. TWILIO VOICE WEBHOOKS — ⚠️ DISABLED
# ========================
# @app.route('/voice-webhook', methods=['POST', 'GET'])
# def voice_webhook():
#     """Handle incoming Twilio voice calls — agriculture AI assistant."""
#     twiml = generate_welcome_twiml()
#     return Response(twiml, mimetype='text/xml')


# @app.route('/voice-respond', methods=['POST'])
# def voice_respond():
#     """Handle voice input from farmer and respond with AI."""
#     speech_text = request.form.get('SpeechResult', '')
#     print(f"[AgriShield] 🎤 Farmer said: {speech_text}")
#     
#     if not speech_text:
#         from twilio.twiml.voice_response import VoiceResponse
#         response = VoiceResponse()
#         response.say(
#             "Sorry, we could not hear you. Please speak again.",
#             language="en-IN",
#             voice="Polly.Aditi",
#         )
#         response.redirect("/voice-webhook")
#         return Response(str(response), mimetype='text/xml')
#     
#     twiml = handle_voice_input(speech_text)
#     return Response(twiml, mimetype='text/xml')


# ========================
# 8. REPORTS API
# ========================
@app.route('/reports', methods=['GET'])
def get_reports():
    """Get aggregated report data."""
    try:
        report = {
            "last_scan": None,
            "alert_history": get_alert_history(20),
            "total_alerts": len(get_alert_history(100)),
        }
        
        # Load last scan
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                report["last_scan"] = json.load(f)
        
        return jsonify({"status": "Success", "data": report})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========================
# 9. HEALTH CHECK
# ========================
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "AgriShield AI Backend Running",
        "version": "4.0 — Twilio Smart Alerts",
        "endpoints": [
            "/predict", "/last-scan", "/weather-advisory", "/mandi-prices",
            "/analyze-soil", "/soil-plant-recommendations", "/soil-crop-recommendations",
            "/send-alert", "/alert-history",
            "/voice-webhook", "/voice-respond",
            "/reports",
        ]
    })


if __name__ == '__main__':
    print("=" * 50)
    print("  AgriShield AI Backend v4.0")
    print("  Powered by Groq Vision AI + Twilio Smart Alerts")
    print("=" * 50)
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 5000)),
        debug=True
    )