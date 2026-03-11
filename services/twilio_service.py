"""
Twilio Communication Service
==============================
Handles SMS, WhatsApp, and Voice Calls via Twilio.

✅ ALL TWILIO CALLS ARE NOW ENABLED
"""
import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
FARMER_PHONE_NUMBER = os.getenv("FARMER_PHONE_NUMBER", "+918989550196")
FARMER_WHATSAPP_NUMBER = os.getenv("FARMER_WHATSAPP_NUMBER")

_client = None


def _get_client():
    """Lazy-initialize Twilio client."""
    global _client
    if _client is None:
        from twilio.rest import Client
        _client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        print("[Twilio] ✅ Twilio client initialized")
    return _client


def send_sms(to: str, body: str):
    """Send SMS via Twilio."""
    try:
        client = _get_client()
        message = client.messages.create(
            to=to,
            from_=TWILIO_PHONE_NUMBER,
            body=body
        )
        print(f"[Twilio] ✅ SMS sent to {to}: {body[:50]}...")
        return {
            "success": True,
            "sid": message.sid,
            "type": "sms"
        }
    except Exception as e:
        print(f"[Twilio] ❌ SMS Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "type": "sms"
        }


def send_whatsapp(to: str, body: str):
    """Send WhatsApp message via Twilio."""
    try:
        client = _get_client()
        message = client.messages.create(
            to=f"whatsapp:{to}",
            from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
            body=body
        )
        print(f"[Twilio] ✅ WhatsApp sent to {to}: {body[:50]}...")
        return {
            "success": True,
            "sid": message.sid,
            "type": "whatsapp"
        }
    except Exception as e:
        print(f"[Twilio] ❌ WhatsApp Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "type": "whatsapp"
        }


def make_voice_call(to: str, twiml_url: str = None, twiml_text: str = None):
    """
    Initiate a voice call via Twilio.
    ✅ NOW ENABLED
    """
    try:
        client = _get_client()
        call_params = {
            "to": to,
            "from_": TWILIO_PHONE_NUMBER,
        }
        if twiml_url:
            call_params["url"] = twiml_url
        elif twiml_text:
            call_params["twiml"] = f"<Response><Say>{twiml_text}</Say></Response>"

        call = client.calls.create(**call_params)
        print(f"[Twilio] ✅ Voice call initiated to {to}, SID: {call.sid}")
        return {
            "success": True,
            "sid": call.sid,
            "type": "voice_call"
        }
    except Exception as e:
        print(f"[Twilio] ❌ Voice Call Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "type": "voice_call"
        }


def format_crop_alert(scan_data: dict) -> str:
    """Format crop scan data into a readable English alert message."""
    crop = scan_data.get("crop_name", "Unknown")
    crop_hi = scan_data.get("crop_name_hindi", "Unknown")
    health = scan_data.get("health_score", "Unknown")
    disease = scan_data.get("disease", "No disease")
    treatment = scan_data.get("treatment", "N/A")
    irrigation = scan_data.get("irrigation_advice", "N/A")
    fertilizer = scan_data.get("fertilizer_recommendation", "N/A")
    harvest_days = scan_data.get("harvest_days", "N/A")

    msg = (
        f"🌾 *AgriShield AI Alert* 🌾\n\n"
        f"📋 Crop: {crop} ({crop_hi})\n"
        f"❤️ Health Score: {health}/100\n"
        f"🦠 Disease: {disease}\n"
        f"💊 Treatment: {treatment}\n"
        f"💧 Irrigation: {irrigation}\n"
        f"🧪 Fertilizer: {fertilizer}\n"
        f"📅 Harvest: in {harvest_days} days\n\n"
        f"⚠️ Please take care of your crop immediately!\n"
        f"🤖 Powered by AgriShield AI"
    )
    return msg


def format_soil_alert(soil_data: dict) -> str:
    """Format soil analysis data into a readable alert message."""
    soil_type = soil_data.get("soil_type", "Unknown")
    ph = soil_data.get("ph", "N/A")
    nitrogen = soil_data.get("nitrogen", "N/A")
    phosphorus = soil_data.get("phosphorus", "N/A")
    potassium = soil_data.get("potassium", "N/A")
    organic_matter = soil_data.get("organic_matter", "N/A")

    msg = (
        f"🌍 *AgriShield Soil Report* 🌍\n\n"
        f"🏷️ Soil Type: {soil_type}\n"
        f"📊 pH Level: {ph}\n"
        f"🟢 Nitrogen: {nitrogen}\n"
        f"🔵 Phosphorus: {phosphorus}\n"
        f"🟡 Potassium: {potassium}\n"
        f"🟤 Organic Matter: {organic_matter}\n\n"
        f"🧑‍🌾 Choose crops according to your soil type!\n"
        f"🤖 Powered by AgriShield AI"
    )
    return msg


def format_voice_alert(scan_data: dict) -> str:
    """Generate TwiML string for voice call alert."""
    crop = scan_data.get("crop_name", "crop")
    crop_hi = scan_data.get("crop_name_hindi", "crop")
    health = scan_data.get("health_score", "Unknown")
    disease = scan_data.get("disease", "no disease")

    speech = f"Alert: {crop} crop health {health}%. Disease: {disease}."
    return speech
