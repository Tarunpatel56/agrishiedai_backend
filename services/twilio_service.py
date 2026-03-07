"""
Twilio Communication Service
==============================
Handles SMS, WhatsApp, and Voice Calls via Twilio.

⚠️ ALL TWILIO CALLS ARE CURRENTLY DISABLED (COMMENTED OUT)
   Uncomment the actual API calls below to re-enable.
"""

import os
# from twilio.rest import Client                    # COMMENTED OUT
# from twilio.twiml.voice_response import VoiceResponse  # COMMENTED OUT
from dotenv import load_dotenv

load_dotenv()

# ── Twilio Config ────────────────────────────────────────────
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
FARMER_PHONE_NUMBER = os.getenv("FARMER_PHONE_NUMBER", "+918989550196")
FARMER_WHATSAPP_NUMBER = os.getenv("FARMER_WHATSAPP_NUMBER", "+918989550196")

# Initialize Twilio client
_client = None

def _get_client():
    """Lazy-initialize Twilio client."""
    # ⚠️ COMMENTED OUT — Twilio disabled
    # global _client
    # if _client is None:
    #     if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    #         print("[Twilio] ❌ Missing credentials in .env")
    #         return None
    #     _client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    #     print("[Twilio] ✅ Client initialized")
    # return _client
    print("[Twilio] ⏸️ Twilio is DISABLED — no messages will be sent")
    return None


# ── SMS ──────────────────────────────────────────────────────
def send_sms(to: str = None, body: str = "AgriShield Alert"):
    """Send SMS via Twilio. ⚠️ CURRENTLY DISABLED"""
    # client = _get_client()
    # if not client:
    #     return {"success": False, "error": "Twilio not configured"}
    # 
    # to = to or FARMER_PHONE_NUMBER
    # try:
    #     message = client.messages.create(
    #         body=body,
    #         from_=TWILIO_PHONE_NUMBER,
    #         to=to,
    #     )
    #     print(f"[Twilio] ✅ SMS sent: {message.sid}")
    #     return {"success": True, "sid": message.sid, "type": "sms"}
    # except Exception as e:
    #     print(f"[Twilio] ❌ SMS Error: {e}")
    #     return {"success": False, "error": str(e)}
    
    print(f"[Twilio] ⏸️ SMS SKIPPED (disabled): {body[:50]}...")
    return {"success": True, "sid": "disabled", "type": "sms", "note": "Twilio disabled"}


# ── WhatsApp ─────────────────────────────────────────────────
def send_whatsapp(to: str = None, body: str = "AgriShield Alert"):
    """Send WhatsApp message via Twilio. ⚠️ CURRENTLY DISABLED"""
    # client = _get_client()
    # if not client:
    #     return {"success": False, "error": "Twilio not configured"}
    # 
    # to = to or FARMER_WHATSAPP_NUMBER
    # try:
    #     message = client.messages.create(
    #         body=body,
    #         from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
    #         to=f"whatsapp:{to}",
    #     )
    #     print(f"[Twilio] ✅ WhatsApp sent: {message.sid}")
    #     return {"success": True, "sid": message.sid, "type": "whatsapp"}
    # except Exception as e:
    #     print(f"[Twilio] ❌ WhatsApp Error: {e}")
    #     return {"success": False, "error": str(e)}
    
    print(f"[Twilio] ⏸️ WhatsApp SKIPPED (disabled): {body[:50]}...")
    return {"success": True, "sid": "disabled", "type": "whatsapp", "note": "Twilio disabled"}


# ── Voice Call ───────────────────────────────────────────────
def make_voice_call(to: str = None, twiml_url: str = None, twiml_text: str = None):
    """
    Initiate a voice call via Twilio.
    ⚠️ CURRENTLY DISABLED
    """
    # client = _get_client()
    # if not client:
    #     return {"success": False, "error": "Twilio not configured"}
    # 
    # to = to or FARMER_PHONE_NUMBER
    # try:
    #     call_params = {
    #         "to": to,
    #         "from_": TWILIO_PHONE_NUMBER,
    #     }
    #     
    #     if twiml_url:
    #         call_params["url"] = twiml_url
    #     elif twiml_text:
    #         call_params["twiml"] = twiml_text
    #     else:
    #         response = VoiceResponse()
    #         response.say(
    #             "Hello! This is an AgriShield AI alert. "
    #             "A problem has been detected in your crop. "
    #             "Please check your phone and view the WhatsApp message.",
    #             language="en-IN",
    #             voice="Polly.Aditi",
    #         )
    #         call_params["twiml"] = str(response)
    #     
    #     call = client.calls.create(**call_params)
    #     print(f"[Twilio] ✅ Call initiated: {call.sid}")
    #     return {"success": True, "sid": call.sid, "type": "voice_call"}
    # except Exception as e:
    #     print(f"[Twilio] ❌ Call Error: {e}")
    #     return {"success": False, "error": str(e)}
    
    print(f"[Twilio] ⏸️ Voice Call SKIPPED (disabled)")
    return {"success": True, "sid": "disabled", "type": "voice_call", "note": "Twilio disabled"}


# ── Alert Message Formatter ─────────────────────────────────
# (These are just string formatters — no Twilio calls — keeping active)

def format_crop_alert(scan_data: dict) -> str:
    """Format crop scan data into a readable English alert message."""
    crop = scan_data.get("crop_name", "Unknown")
    crop_hi = scan_data.get("crop_name_hindi", crop)
    health = scan_data.get("health_score", 0)
    disease = scan_data.get("disease", "No disease")
    treatment = scan_data.get("treatment", "N/A")
    irrigation = scan_data.get("irrigation_advice", "N/A")
    fertilizer = scan_data.get("fertilizer_recommendation", "N/A")
    harvest_days = scan_data.get("harvest_days", 0)
    
    msg = f"""🌾 *AgriShield AI Alert* 🌾

📋 Crop: {crop} ({crop_hi})
❤️ Health Score: {health}/100
🦠 Disease: {disease}
💊 Treatment: {treatment}
💧 Irrigation: {irrigation}
🧪 Fertilizer: {fertilizer}
📅 Harvest: in {harvest_days} days

⚠️ Please take care of your crop immediately!
🤖 Powered by AgriShield AI"""
    return msg


def format_soil_alert(soil_data: dict) -> str:
    """Format soil analysis data into a readable alert message."""
    soil_type = soil_data.get("soil_type", "Unknown")
    ph = soil_data.get("ph", "N/A")
    nitrogen = soil_data.get("nitrogen", "N/A")
    phosphorus = soil_data.get("phosphorus", "N/A")
    potassium = soil_data.get("potassium", "N/A")
    organic_matter = soil_data.get("organic_matter", "N/A")
    
    msg = f"""🌍 *AgriShield Soil Report* 🌍

🏷️ Soil Type: {soil_type}
📊 pH Level: {ph}
🟢 Nitrogen: {nitrogen}
🔵 Phosphorus: {phosphorus}
🟡 Potassium: {potassium}
🟤 Organic Matter: {organic_matter}

🧑‍🌾 Choose crops according to your soil type!
🤖 Powered by AgriShield AI"""
    return msg


def format_voice_alert(scan_data: dict) -> str:
    """Generate TwiML string for voice call alert. ⚠️ Returns plain text since Twilio disabled."""
    crop = scan_data.get("crop_name", "crop")
    crop_hi = scan_data.get("crop_name_hindi", crop)
    health = scan_data.get("health_score", 0)
    disease = scan_data.get("disease", "no disease")
    
    # ⚠️ COMMENTED OUT — VoiceResponse needs twilio import
    # response = VoiceResponse()
    # response.say(speech, language="en-IN", voice="Polly.Aditi")
    # return str(response)
    
    # Return plain text instead (no TwiML)
    speech = f"Alert: {crop_hi} crop health {health}%. Disease: {disease}."
    return speech
