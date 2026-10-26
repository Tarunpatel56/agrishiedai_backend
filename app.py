from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json
from dotenv import load_dotenv

# Fix Windows terminal encoding for emoji output
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Add parent directory (workspace root) to path so we can import agrishield_twilio
_backend_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.abspath(os.path.join(_backend_dir, '..'))
for _p in [_backend_dir, _root_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Import services
from services.plant_disease_service import run_plant_disease_inference
from services.pet_disease_service import run_pet_disease_inference
from services.soil_analysis_service import run_soil_analysis_inference
from services.spray_advisor_service import get_spray_recommendation
from services.fertilizer_advisor_service import calculate_fertilizer_prescription
from services.govt_schemes_service import get_all_schemes
from services.groq_crop_analysis import analyze_crop_with_groq
from services.weather_service import get_recent_weather
from services.market_service import get_market_prices
from services.groq_soil_analysis import analyze_soil_image, get_plant_recommendations, get_crop_recommendations
from services.groq_agri_services import get_recovery_advice, calculate_roi, get_market_predictions, agri_chat
from services.groq_client import call_groq, GROQ_TEXT_MODEL, GROQ_VISION_MODEL, GROQ_FALLBACK_MODEL

# ── Twilio imports with safe fallbacks (optional for cloud deployment) ──
try:
    from agrishield_twilio import (
        send_sms, make_voice_call,
        format_crop_alert, format_voice_alert,
        generate_language_selection_twiml, handle_language_selection,
        generate_welcome_twiml, handle_voice_input, generate_alert_call_twiml,
        FARMER_PHONE_NUMBER,
    )
    TWILIO_AVAILABLE = True
except Exception as _t_err:
    print(f"[AgriShield] Twilio optional/disabled: {_t_err}")
    TWILIO_AVAILABLE = False
    FARMER_PHONE_NUMBER = os.getenv("FARMER_PHONE_NUMBER", "+918989550196")
    def send_sms(*a, **kw): return {"success": False, "error": "Twilio not configured"}
    def make_voice_call(*a, **kw): return {"success": False, "error": "Twilio not configured"}
    def format_crop_alert(d): return f"Alert: {d.get('crop_name', 'Crop')}"
    def format_voice_alert(d): return f"Fasal update: {d.get('crop_name', '')}"
    def generate_language_selection_twiml(): return "<Response><Say>AgriShield</Say></Response>"
    def handle_language_selection(*a, **kw): return "<Response><Say>AgriShield Language</Say></Response>"
    def generate_welcome_twiml(): return "<Response><Say>AgriShield</Say></Response>"
    def handle_voice_input(*a, **kw): return "<Response><Say>OK</Say></Response>"
    def generate_alert_call_twiml(*a, **kw): return "<Response><Say>Alert</Say></Response>"

from datetime import datetime

load_dotenv()
app = Flask(__name__)
CORS(app)

DATA_FILE = "last_scan.json"
UPLOAD_FOLDER = "stored_crops"
PET_UPLOAD_FOLDER = "stored_pets"
SOIL_UPLOAD_FOLDER = "stored_soil"
SPRAY_UPLOAD_FOLDER = "stored_sprays"
ALERT_HISTORY_FILE = os.path.join("project_data", "alert_history.json")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PET_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SOIL_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SPRAY_UPLOAD_FOLDER, exist_ok=True)
os.makedirs("project_data", exist_ok=True)


# ========================
# 1. INDEPENDENT AI/ML MODEL ROUTES
# ========================

# ── 1.A Dedicated Plant Disease Detection ──
@app.route('/predict-plant', methods=['POST'])
def predict_plant():
    """Independent Plant Disease Detection (PlantVillage architecture & vision)."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No plant image file uploaded"}), 400

        file = request.files['file']
        language = request.form.get('language', 'en')
        filename = f"plant_{len(os.listdir(UPLOAD_FOLDER)) + 1}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        print(f"[AgriShield] Plant image saved: {filepath}")

        result = run_plant_disease_inference(filepath, language=language)
        if "error" in result:
            return jsonify({"status": "Error", "error": result["error"]}), 400

        # Save to last_scan.json for home screen backward compatibility
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return jsonify({
            "status": "Success",
            "model_type": "Plant Disease Model (PlantVillage)",
            "data": result,
            "confidence": result.get("confidence", 0)
        })
    except Exception as e:
        print(f"[AgriShield] Plant Inference Error: {e}")
        return jsonify({"error": str(e)}), 500


# ── 1.B Dedicated Pet / Pest & Livestock Disease Detection ──
@app.route('/predict-pet', methods=['POST'])
def predict_pet():
    """Independent Pet / Pest & Livestock Disease Detection (AgriShield Pest dataset)."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No pet or pest image file uploaded"}), 400

        file = request.files['file']
        language = request.form.get('language', 'en')
        filename = f"pet_{len(os.listdir(PET_UPLOAD_FOLDER)) + 1}.jpg"
        filepath = os.path.join(PET_UPLOAD_FOLDER, filename)
        file.save(filepath)
        print(f"[AgriShield] Pet/Pest image saved: {filepath}")

        result = run_pet_disease_inference(filepath, language=language)
        if "error" in result:
            return jsonify({"status": "Error", "error": result["error"]}), 400

        return jsonify({
            "status": "Success",
            "model_type": "Pet & Pest Disease Model",
            "data": result,
            "confidence": result.get("confidence", 0)
        })
    except Exception as e:
        print(f"[AgriShield] Pet/Pest Inference Error: {e}")
        return jsonify({"error": str(e)}), 500


# ── 1.C Dedicated Soil Analysis Model ──
@app.route('/predict-soil', methods=['POST'])
def predict_soil():
    """Independent Soil Analysis & Classification Model."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No soil image file uploaded"}), 400

        file = request.files['file']
        language = request.form.get('language', 'en')
        filename = f"soil_{len(os.listdir(SOIL_UPLOAD_FOLDER)) + 1}.jpg"
        filepath = os.path.join(SOIL_UPLOAD_FOLDER, filename)
        file.save(filepath)
        print(f"[AgriShield] Soil image saved: {filepath}")

        result = run_soil_analysis_inference(filepath, language=language)
        if "error" in result:
            return jsonify({"status": "Error", "error": result["error"]}), 400

        return jsonify({
            "status": "Success",
            "model_type": "Soil Analysis Model",
            "data": result
        })
    except Exception as e:
        print(f"[AgriShield] Soil Inference Error: {e}")
        return jsonify({"error": str(e)}), 500


# ── 1.D Legacy Predict (Backward Compatible for existing Flutter ScanView) ──
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

        # Execute plant disease detection
        analysis_data = run_plant_disease_inference(filepath)
        if "error" in analysis_data:
            # Fallback to general crop analysis
            analysis_data = analyze_crop_with_groq(filepath)

        if "error" in analysis_data:
            return jsonify({"status": "Error", "error": analysis_data["error"]}), 400

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)

        return jsonify({
            "status": "Success",
            "data": analysis_data,
            "confidence": analysis_data.get("confidence", 0)
        })
    except Exception as e:
        print(f"[AgriShield] Server Error: {e}")
        return jsonify({"error": str(e)}), 500


# ========================
# 1.E CROP SPRAY ADVISOR (IPM & CIBRC Approved)
# ========================
@app.route('/crop-spray-advisor', methods=['POST'])
def crop_spray_advisor_route():
    try:
        # Support both multipart form data and json
        image_path = None
        if 'image' in request.files:
            img = request.files['image']
            fn = f"spray_{len(os.listdir(SPRAY_UPLOAD_FOLDER)) + 1}.jpg"
            image_path = os.path.join(SPRAY_UPLOAD_FOLDER, fn)
            img.save(image_path)

        crop_name = request.form.get('crop_name') or request.json.get('crop_name') if request.is_json else request.form.get('crop_name', '')
        growth_stage = request.form.get('growth_stage') or (request.json.get('growth_stage') if request.is_json else 'Vegetative')
        symptoms = request.form.get('symptoms') or (request.json.get('symptoms') if request.is_json else '')
        affected_parts = request.form.get('affected_parts') or (request.json.get('affected_parts') if request.is_json else 'Leaves')
        severity = request.form.get('severity') or (request.json.get('severity') if request.is_json else 'Moderate')
        spread = request.form.get('spread') or (request.json.get('spread') if request.is_json else 'Patches')
        region = request.form.get('region') or (request.json.get('region') if request.is_json else 'India')
        language = request.form.get('language') or (request.json.get('language') if request.is_json else 'en')

        result = get_spray_recommendation(
            crop_name=crop_name,
            growth_stage=growth_stage,
            symptoms=symptoms,
            affected_parts=affected_parts,
            severity=severity,
            spread=spread,
            region=region,
            image_path=image_path,
            language=language
        )

        if "error" in result:
            return jsonify({"status": "Error", "error": result["error"]}), 400

        return jsonify({"status": "Success", "data": result})
    except Exception as e:
        print(f"[AgriShield] Spray Advisor Error: {e}")
        return jsonify({"error": str(e)}), 500


# ========================
# 1.F FERTILIZER PRESCRIPTION & NUTRIENT ADVISOR
# ========================
@app.route('/fertilizer-advisor', methods=['POST'])
def fertilizer_advisor_route():
    try:
        data = request.get_json() if request.is_json else request.form
        crop_name = data.get('crop_name') or data.get('crop', 'Wheat')
        try:
            farm_area = float(data.get('farm_area', 1.0))
        except:
            farm_area = 1.0

        area_unit = data.get('area_unit', 'acre')
        growth_stage = data.get('growth_stage', 'Basal / Sowing')
        soil_type = data.get('soil_type', 'Loamy')
        soil_test_n = data.get('soil_test_n')
        soil_test_p = data.get('soil_test_p')
        soil_test_k = data.get('soil_test_k')
        irrigation_type = data.get('irrigation_type', 'Irrigated')
        language = data.get('language', 'en')

        result = calculate_fertilizer_prescription(
            crop_name=crop_name,
            farm_area=farm_area,
            area_unit=area_unit,
            growth_stage=growth_stage,
            soil_type=soil_type,
            soil_test_n=soil_test_n,
            soil_test_p=soil_test_p,
            soil_test_k=soil_test_k,
            irrigation_type=irrigation_type,
            language=language
        )

        if "error" in result:
            return jsonify({"status": "Error", "error": result["error"]}), 400

        return jsonify({"status": "Success", "data": result})
    except Exception as e:
        print(f"[AgriShield] Fertilizer Advisor Error: {e}")
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
# 4. MANDI PRICES (Government of India Agmarknet / data.gov.in)
# ========================
@app.route('/mandi-prices', methods=['GET'])
def mandi_prices():
    try:
        state = request.args.get('state')
        district = request.args.get('district')
        market = request.args.get('market')
        commodity = request.args.get('commodity')
        search = request.args.get('search') or request.args.get('q')
        sort_by = request.args.get('sort_by')
        order = request.args.get('order', 'desc')

        prices = get_market_prices(
            state=state,
            district=district,
            market=market,
            commodity=commodity,
            search=search,
            sort_by=sort_by,
            order=order
        )
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
        # ========================
# 10. TWILIO VOICE WEBHOOKS — Bilingual IVR with Groq AI
# ========================
@app.route('/voice-incoming', methods=['POST', 'GET'])
def voice_incoming():
    """Twilio webhook — farmer calls this number → Language Selection (1: Hindi, 2: English)."""
    print("[AgriShield] 📞 Incoming call received! Presenting language selection prompt...")
    twiml = generate_language_selection_twiml()
    return twiml, 200, {'Content-Type': 'application/xml'}


@app.route('/voice-lang-select', methods=['POST'])
def voice_lang_select():
    """Twilio webhook — receives farmer's DTMF keypress (1 for Hindi, 2 for English)."""
    digits = request.form.get('Digits', request.args.get('Digits', '1'))
    print(f"[AgriShield] 🔢 Farmer selected language option: {digits}")
    twiml = handle_language_selection(digits)
    return twiml, 200, {'Content-Type': 'application/xml'}


@app.route('/voice-respond', methods=['POST'])
def voice_respond():
    """Twilio webhook — farmer speaks → Groq AI answers in chosen language (hi / en)."""
    lang = request.args.get('lang') or request.form.get('lang', 'hi')
    lang = 'en' if str(lang).lower().startswith('en') else 'hi'
    speech = request.form.get('SpeechResult', '')
    print(f"[AgriShield] 🗣️ Farmer ({lang}) said: '{speech}'")

    if not speech:
        from twilio.twiml.voice_response import VoiceResponse, Gather
        response = VoiceResponse()
        voice_lang = 'en-IN' if lang == 'en' else 'hi-IN'
        gather = Gather(
            input='speech',
            action=f'/voice-respond?lang={lang}',
            method='POST',
            language=voice_lang,
            speech_timeout='auto',
            timeout=9
        )
        if lang == 'en':
            gather.say('Sorry, I did not catch that. Please speak your farming question again.',
                       language='en-IN', voice='Polly.Aditi')
            response.append(gather)
            response.say('Thank you farmer! AgriShield AI is always here to assist you. Happy farming!',
                         language='en-IN', voice='Polly.Aditi')
        else:
            gather.say('भैया, मुझे आपकी आवाज़ नहीं सुनाई दी। कृपया अपना सवाल दोबारा बोलिए।',
                       language='hi-IN', voice='Polly.Aditi')
            response.append(gather)
            response.say('धन्यवाद किसान भाई! आपका दिन शुभ हो। जय किसान!',
                         language='hi-IN', voice='Polly.Aditi')
        return str(response), 200, {'Content-Type': 'application/xml'}

    twiml = handle_voice_input(speech, lang=lang)
    print(f"[AgriShield] 🤖 AI response generated for farmer in {lang}")
    return twiml, 200, {'Content-Type': 'application/xml'}


# ========================
# 11. TWILIO OUTGOING CALL — Bilingual Groq AI Agriculture Call
# ========================
VOICE_AGRI_PROMPT_HI = """You are AgriShield AI — a FEMALE assistant calling a farmer to give agriculture advice.

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

VOICE_AGRI_PROMPT_EN = """You are AgriShield AI — a knowledgeable and friendly agricultural assistant calling a farmer to give practical farming advice.

Generate a SHORT, helpful voice message (3-5 sentences) IN ENGLISH.
The message should:
1. Greet warmly: "Hello farmer!"
2. Introduce yourself: "This is AgriShield AI"
3. Give useful farming tip or crop management advice
4. Be practical for Indian farmers
5. End with: "Wishing you a bountiful harvest! Happy farming!"

If crop data is provided, give specific advice about that crop.

{crop_info}

Generate ONLY the spoken text in clear, simple English.
No formatting, no quotes, no special characters.
Keep it under 150 words."""


@app.route('/send-alert', methods=['POST'])
def send_alert():
    """Send voice call alert to farmer with Groq AI agriculture content in chosen language."""
    try:
        data = request.get_json() or {}
        phone = data.get('phone', FARMER_PHONE_NUMBER)
        scan_data = data.get('scan_data', {})
        message = data.get('message', '')
        level = data.get('level', 'INFO')
        language = data.get('language', 'hi')

        results = []

        # ── Generate AI Agriculture Message via Groq ──
        print(f"[AgriShield] 🤖 Generating AI agriculture message ({language}) via Groq...")

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

        if str(language).lower().startswith('en'):
            ai_prompt = VOICE_AGRI_PROMPT_EN.format(crop_info=crop_info)
            voice_lang = 'en-IN'
        else:
            ai_prompt = VOICE_AGRI_PROMPT_HI.format(crop_info=crop_info)
            voice_lang = 'hi-IN'

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
                voice_text = message or ("Hello farmer! This is AgriShield AI. Please check your crops regularly and use proper fertilizers. Happy farming!" if voice_lang == 'en-IN' else "नमस्ते किसान भाई! मैं AgriShield AI हूं। कृपया अपनी फसलों की नियमित देखभाल करें। धन्यवाद!")
            print(f"[AgriShield] ⚠️ Groq failed, using fallback message")

        # ── Make the voice call ──
        print(f"[AgriShield] 📞 Calling {phone} in {voice_lang}...")
        call_result = make_voice_call(to=phone, twiml_text=voice_text, language=voice_lang)
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
# 12. GOVERNMENT SCHEMES
# ========================
@app.route('/govt-schemes', methods=['GET'])
def govt_schemes():
    """Get verified Indian central and state government agricultural schemes."""
    try:
        category = request.args.get('category')
        level = request.args.get('level')
        state = request.args.get('state')
        search = request.args.get('search') or request.args.get('q')

        schemes = get_all_schemes(
            category=category,
            level=level,
            state=state,
            search=search
        )
        return jsonify({"status": "Success", "data": schemes})
    except Exception as e:
        print(f"[AgriShield] Govt Schemes Error: {e}")
        return jsonify({"error": str(e)}), 500


# ========================
# 13. HEALTH CHECK
# ========================
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "AgriShield AI Backend Running",
        "version": "5.0",
        "ai_provider": "Groq LPU + PlantVillage & Pest ML Architecture",
        "primary_model": GROQ_TEXT_MODEL,
        "vision_model": GROQ_VISION_MODEL,
        "fallback_model": GROQ_FALLBACK_MODEL,
        "twilio": "Bilingual Twilio Voice IVR (1: Hindi, 2: English)",
        "endpoints": [
            "/predict-plant", "/predict-pet", "/predict-soil", "/predict",
            "/crop-spray-advisor", "/fertilizer-advisor",
            "/last-scan", "/weather-advisory", "/mandi-prices",
            "/analyze-soil", "/soil-plant-recommendations", "/soil-crop-recommendations",
            "/recovery-advice", "/roi-calculate", "/market-predictions", "/agri-chat",
            "/voice-incoming", "/voice-lang-select", "/voice-respond",
            "/send-alert", "/alert-history", "/govt-schemes", "/ai-info"
        ]
    })


# ========================
# 14. AI MODEL INFO
# ========================
@app.route('/ai-info', methods=['GET'])
def ai_info():
    """Returns current AI model configuration."""
    return jsonify({
        "status": "Success",
        "data": {
            "provider": "Groq",
            "provider_url": "https://api.groq.com",
            "hardware": "Groq LPU (Language Processing Unit)",
            "models": {
                "text": {
                    "id": GROQ_TEXT_MODEL,
                    "name": "OpenAI GPT OSS 120B",
                    "by": "OpenAI (hosted on Groq LPU)",
                    "params": "120B",
                    "context_window": 131072,
                    "use": "All text generation: chat, analysis, predictions, ROI"
                },
                "vision": {
                    "id": GROQ_VISION_MODEL,
                    "name": "Qwen 3.8 27B Vision",
                    "by": "Alibaba Cloud (hosted on Groq LPU)",
                    "params": "27B Multimodal",
                    "context_window": 131072,
                    "use": "Fastest crop & soil image analysis (<1s)"
                },
                "fallback": {
                    "id": GROQ_FALLBACK_MODEL,
                    "name": "OpenAI GPT OSS 20B",
                    "by": "OpenAI (hosted on Groq LPU)",
                    "params": "20B",
                    "context_window": 131072,
                    "use": "Ultra-fast auto-fallback"
                }
            }
        }
    })


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))

    print("=" * 55)
    print("  AgriShield AI Backend v4.4")
    print(f"  Primary AI : {GROQ_TEXT_MODEL}")
    print(f"  Vision AI  : {GROQ_VISION_MODEL}")
    print(f"  Fallback   : {GROQ_FALLBACK_MODEL}")
    print("  Powered by Groq LPU + Twilio Voice")
    print("=" * 55)
    print(f"\n[AgriShield] Farmer phone: {FARMER_PHONE_NUMBER}")
    print(f"[AgriShield] Server starting on port {port}...")
    print("=" * 55)

    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=port,
        debug=True
    )