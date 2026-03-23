from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
from dotenv import load_dotenv

# Add parent directory to path so we can import agrishield_twilio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import services
from services.groq_crop_analysis import analyze_crop_with_groq
from services.weather_service import get_recent_weather
from services.market_service import get_market_prices
from services.groq_soil_analysis import analyze_soil_image, get_plant_recommendations, get_crop_recommendations
from services.groq_agri_services import get_recovery_advice, calculate_roi, get_market_predictions, agri_chat
from services.groq_client import call_groq

# ── All Twilio imports from agrishield_twilio ──
from agrishield_twilio import (
    send_sms, make_voice_call,
    format_crop_alert, format_voice_alert,
    generate_welcome_twiml, handle_voice_input, generate_alert_call_twiml,
    FARMER_PHONE_NUMBER,
)

from datetime import datetime

load_dotenv()
app = Flask(__name__)
CORS(app)

DATA_FILE = "last_scan.json"
UPLOAD_FOLDER = "stored_crops"
SOIL_UPLOAD_FOLDER = "stored_soil"
ALERT_HISTORY_FILE = os.path.join("project_data", "alert_history.json")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SOIL_UPLOAD_FOLDER, exist_ok=True)
os.makedirs("project_data", exist_ok=True)


# ========================
# 1. CROP ANALYSIS (Groq Vision AI)
# ========================
@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        filename = f"crop_{len(os.listdir(UPLOAD_FOLDER)) + 1}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        print(f"[AgriShield] Image saved: {filepath}")

        analysis_data = analyze_crop_with_groq(filepath)
        if "error" in analysis_data:
            return jsonify({"status": "Error", "error": analysis_data["error"]}), 500

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
# 5. SOIL ANALYSIS
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
        return jsonify({"status": "Success", "data": result})
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
        season = request.form.get('season', None)
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
# 6. RECOVERY ADVISOR
# ========================
@app.route('/recovery-advice', methods=['POST'])
def recovery_advice():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        result = get_recovery_advice(data)
        if "error" in result:
            return jsonify({"status": "Error", "error": result["error"]}), 500
        return jsonify({"status": "Success", "data": result})
    except Exception as e:
        print(f"[AgriShield] Recovery Error: {e}")
        return jsonify({"error": str(e)}), 500


# ========================
# 7. ROI CALCULATOR
# ========================
@app.route('/roi-calculate', methods=['POST'])
def roi_calculate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        investment = int(data.get('investment_amount', 50000))
        land_size = float(data.get('land_size', 5))
        crop_name = data.get('crop_name', 'General')
        result = calculate_roi(investment, land_size, crop_name)
        if "error" in result:
            return jsonify({"status": "Error", "error": result["error"]}), 500
        return jsonify({"status": "Success", "data": result})
    except Exception as e:
        print(f"[AgriShield] ROI Error: {e}")
        return jsonify({"error": str(e)}), 500


# ========================
# 8. MARKET PREDICTIONS
# ========================
@app.route('/market-predictions', methods=['GET'])
def market_predictions():
    try:
        result = get_market_predictions()
        if "error" in result:
            return jsonify({"status": "Error", "error": result["error"]}), 500
        return jsonify({"status": "Success", "data": result["predictions"]})
    except Exception as e:
        print(f"[AgriShield] Market Prediction Error: {e}")
        return jsonify({"error": str(e)}), 500


# ========================
# 9. AGRIBOT CHATBOT
# ========================
@app.route('/agri-chat', methods=['POST'])
def agri_chat_route():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        message = data['message']
        language = data.get('language', 'hi')
        history = data.get('history', [])
        result = agri_chat(message, language, history)
        if "error" in result:
            return jsonify({"status": "Error", "error": result["error"]}), 500
        return jsonify({"status": "Success", "data": result})
    except Exception as e:
        print(f"[AgriShield] Chat Error: {e}")
        return jsonify({"error": str(e)}), 500


# ========================
# 10. TWILIO VOICE WEBHOOKS — IVR with Groq AI
# ========================
@app.route('/voice-incoming', methods=['POST', 'GET'])
def voice_incoming():
    """Twilio webhook — farmer calls this number → AI welcomes in Hindi."""
    print("[AgriShield] 📞 Incoming call received! Generating Hindi welcome...")
    twiml = generate_welcome_twiml()
    return twiml, 200, {'Content-Type': 'application/xml'}


@app.route('/voice-respond', methods=['POST'])
def voice_respond():
    """Twilio webhook — farmer speaks → Groq AI answers in Hindi."""
    speech = request.form.get('SpeechResult', '')
    print(f"[AgriShield] 🗣️ Farmer said: '{speech}'")

    if not speech:
        from twilio.twiml.voice_response import VoiceResponse, Gather
        response = VoiceResponse()
        gather = Gather(input='speech', action='/voice-respond', method='POST',
                        language='hi-IN', speech_timeout='auto', timeout=10)
        gather.say('भैया, मुझे आपकी आवाज़ नहीं सुनाई दी। कृपया अपना सवाल दोबारा बोलिए।',
                   language='hi-IN', voice='Polly.Aditi')
        response.append(gather)
        response.say('धन्यवाद किसान भाई! आपका दिन शुभ हो। जय किसान!', language='hi-IN', voice='Polly.Aditi')
        return str(response), 200, {'Content-Type': 'application/xml'}

    twiml = handle_voice_input(speech)
    print("[AgriShield] 🤖 AI response generated for farmer")
    return twiml, 200, {'Content-Type': 'application/xml'}


# ========================
# 11. TWILIO OUTGOING CALL — Groq AI Agriculture Call
# ========================
VOICE_AGRI_PROMPT = """You are AgriShield AI — a FEMALE assistant calling a farmer to give agriculture advice.

IMPORTANT: You are FEMALE. Always use FEMININE Hindi verb forms:
- "मैं बता सकती हूं" (NOT "सकता हूं")
- "मैं आई हूं" (NOT "आया हूं")
- "मैंने सोचा" with feminine endings

Generate a SHORT, helpful voice message (3-5 sentences) IN HINDI (Devanagari script).
The message should:
1. Greet warmly: "नमस्ते किसान भाई!"
2. Introduce yourself: "मैं AgriShield AI हूं"
3. Give useful farming tip/advice in simple feminine Hindi
4. Be practical for Indian farmers
5. End with: "आपका दिन शुभ हो। जय किसान!"

If crop data is provided, give specific advice about that crop.

{crop_info}

Generate ONLY the spoken text in HINDI Devanagari with FEMININE verb forms.
No formatting, no quotes, no special characters, no English.
Keep it under 200 words."""


@app.route('/send-alert', methods=['POST'])
def send_alert():
    """Send voice call alert to farmer with Groq AI agriculture content."""
    try:
        data = request.get_json() or {}
        phone = data.get('phone', FARMER_PHONE_NUMBER)
        scan_data = data.get('scan_data', {})
        message = data.get('message', '')
        level = data.get('level', 'INFO')

        results = []

        # ── Generate AI Agriculture Message via Groq ──
        print("[AgriShield] 🤖 Generating AI agriculture message via Groq...")

        if scan_data:
            crop_info = (
                f"Crop: {scan_data.get('crop_name', 'Unknown')}\n"
                f"Health Score: {scan_data.get('health_score', 'N/A')}/100\n"
                f"Disease: {scan_data.get('disease', 'None')}\n"
                f"Treatment: {scan_data.get('treatment', 'N/A')}\n"
                f"Fertilizer: {scan_data.get('fertilizer_recommendation', 'N/A')}"
            )
        elif message:
            crop_info = f"Context: {message}"
        else:
            crop_info = "No specific crop data. Give general seasonal farming advice for Indian farmers."

        ai_prompt = VOICE_AGRI_PROMPT.format(crop_info=crop_info)

        groq_result = call_groq(
            prompt=ai_prompt,
            temperature=0.6,
            max_tokens=300,
            timeout=15,
            tag="VoiceCall"
        )

        if groq_result.get("success"):
            voice_text = groq_result["raw"].strip().strip('"\'')
            print(f"[AgriShield] 🤖 AI Message: {voice_text[:100]}...")
        else:
            if scan_data:
                voice_text = format_voice_alert(scan_data)
            else:
                voice_text = message or "Hello farmer! This is AgriShield AI. Please check your crops regularly. Use proper irrigation and fertilizers. Happy farming!"
            print(f"[AgriShield] ⚠️ Groq failed, using fallback message")

        # ── Make the voice call ──
        print(f"[AgriShield] 📞 Calling {phone}...")
        call_result = make_voice_call(to=phone, twiml_text=voice_text)
        results.append(call_result)

        if call_result.get("success"):
            print(f"[AgriShield] ✅ Call initiated! SID: {call_result.get('sid')}")
        else:
            print(f"[AgriShield] ❌ Call failed: {call_result.get('error')}")

        # Save to alert history
        alert_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'crop_scan' if scan_data else 'manual',
            'alert_level': level,
            'crop_name': scan_data.get('crop_name', ''),
            'health_score': scan_data.get('health_score', ''),
            'phone': phone,
            'ai_message': voice_text[:200],
            'results': results,
        }
        _save_alert_history(alert_entry)

        return jsonify({'status': 'Success', 'results': results, 'ai_message': voice_text})
    except Exception as e:
        print(f'[AgriShield] Alert Error: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/alert-history', methods=['GET'])
def alert_history():
    """Get alert history."""
    try:
        limit = int(request.args.get('limit', 50))
        history = _load_alert_history()
        return jsonify({'status': 'Success', 'data': history[:limit]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _save_alert_history(entry):
    history = _load_alert_history()
    history.insert(0, entry)
    history = history[:200]
    with open(ALERT_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def _load_alert_history():
    if os.path.exists(ALERT_HISTORY_FILE):
        with open(ALERT_HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []


# ========================
# 11. HEALTH CHECK
# ========================
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "AgriShield AI Backend Running",
        "version": "4.3",
        "twilio": "agrishield_twilio module",
        "endpoints": [
            "/predict", "/last-scan", "/weather-advisory", "/mandi-prices",
            "/analyze-soil", "/soil-plant-recommendations", "/soil-crop-recommendations",
            "/recovery-advice", "/roi-calculate", "/market-predictions", "/agri-chat",
            "/voice-incoming", "/voice-respond",
            "/send-alert", "/alert-history"
        ]
    })


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))

    print("=" * 50)
    print("  AgriShield AI Backend v4.3")
    print("  Powered by Groq AI + Twilio Voice")
    print("  Twilio: agrishield_twilio/")
    print("=" * 50)
    print(f"\n[AgriShield] 📞 Farmer phone: {FARMER_PHONE_NUMBER}")
    print(f"[AgriShield] 🌐 Server starting on port {port}...")
    print("=" * 50)

    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=port,
        debug=True
    )