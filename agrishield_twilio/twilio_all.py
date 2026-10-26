"""
AgriShield Twilio — All-in-One
================================
SMS, WhatsApp, Voice Calls, and Voice IVR with Groq AI.
All Twilio functionality in one file.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# ══════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
FARMER_PHONE_NUMBER = os.getenv("FARMER_PHONE_NUMBER", "+918989550196")
FARMER_WHATSAPP_NUMBER = os.getenv("FARMER_WHATSAPP_NUMBER")

_client = None


def _get_client():
    """Lazy-initialize Twilio client safely."""
    global _client
    if _client is None:
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            print("[Twilio] ⚠️ Twilio credentials missing (notifications disabled)")
            return None
        try:
            from twilio.rest import Client
            _client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            print("[Twilio] ✅ Twilio client initialized")
        except Exception as e:
            print(f"[Twilio] ⚠️ Could not initialize Twilio client: {e}")
            return None
    return _client


# ══════════════════════════════════════════════════════════════
# 1. SMS
# ══════════════════════════════════════════════════════════════
def send_sms(to: str, body: str):
    """Send SMS via Twilio."""
    try:
        client = _get_client()
        if not client:
            return {"success": False, "error": "Twilio not configured on server", "type": "sms"}
        message = client.messages.create(
            to=to,
            from_=TWILIO_PHONE_NUMBER,
            body=body
        )
        print(f"[Twilio] ✅ SMS sent to {to}: {body[:50]}...")
        return {"success": True, "sid": message.sid, "type": "sms"}
    except Exception as e:
        print(f"[Twilio] ❌ SMS Error: {e}")
        return {"success": False, "error": str(e), "type": "sms"}


# ══════════════════════════════════════════════════════════════
# 2. WHATSAPP
# ══════════════════════════════════════════════════════════════
def send_whatsapp(to: str, body: str):
    """Send WhatsApp message via Twilio."""
    try:
        client = _get_client()
        if not client:
            return {"success": False, "error": "Twilio not configured on server", "type": "whatsapp"}
        message = client.messages.create(
            to=f"whatsapp:{to}",
            from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
            body=body
        )
        print(f"[Twilio] ✅ WhatsApp sent to {to}: {body[:50]}...")
        return {"success": True, "sid": message.sid, "type": "whatsapp"}
    except Exception as e:
        print(f"[Twilio] ❌ WhatsApp Error: {e}")
        return {"success": False, "error": str(e), "type": "whatsapp"}


# ══════════════════════════════════════════════════════════════
# 3. VOICE CALL
# ══════════════════════════════════════════════════════════════
def make_voice_call(to: str, webhook_url: str = None, twiml_text: str = None, language: str = 'hi-IN'):
    """
    Initiate a voice call via Twilio.

    - webhook_url: Public URL for IVR (Groq AI interaction) — needs ngrok
    - twiml_text: Static text to speak on the call (works without ngrok)
    - language: Speech language ('hi-IN' for Hindi, 'en-IN' for English)
    """
    try:
        client = _get_client()
        if not client:
            return {"success": False, "error": "Twilio not configured on server", "type": "voice_call"}
        call_params = {
            "to": to,
            "from_": TWILIO_PHONE_NUMBER,
        }

        voice_lang = 'en-IN' if 'en' in str(language).lower() else 'hi-IN'

        if webhook_url:
            call_params["url"] = webhook_url
            print(f"[Twilio] 📞 Using webhook URL: {webhook_url}")
        elif twiml_text:
            call_params["twiml"] = (
                f"<Response>"
                f"<Say language='{voice_lang}' voice='Polly.Aditi'>{twiml_text}</Say>"
                f"</Response>"
            )
        else:
            if voice_lang == 'en-IN':
                default_msg = "Hello farmer! I am AgriShield AI. I am here to help care for your crops. Thank you!"
            else:
                default_msg = "नमस्ते किसान भाई! मैं AgriShield AI हूं। आपकी फसलों की देखभाल के लिए मैं यहां हूं। धन्यवाद!"
            call_params["twiml"] = (
                f"<Response>"
                f"<Say language='{voice_lang}' voice='Polly.Aditi'>{default_msg}</Say>"
                f"</Response>"
            )

        call = client.calls.create(**call_params)
        print(f"[Twilio] ✅ Voice call initiated to {to}, SID: {call.sid}")
        return {"success": True, "sid": call.sid, "type": "voice_call"}
    except Exception as e:
        print(f"[Twilio] ❌ Voice Call Error: {e}")
        return {"success": False, "error": str(e), "type": "voice_call"}


# ══════════════════════════════════════════════════════════════
# 4. ALERT MESSAGE FORMATTERS
# ══════════════════════════════════════════════════════════════
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
    """Generate speech text for voice call alert in Hindi."""
    crop = scan_data.get("crop_name", "crop")
    crop_hi = scan_data.get("crop_name_hindi", crop)
    health = scan_data.get("health_score", "Unknown")
    disease = scan_data.get("disease", "no disease")
    speech = f"किसान भाई ध्यान दें! आपकी {crop_hi} फसल की सेहत सिर्फ {health} प्रतिशत है। बीमारी: {disease}। कृपया तुरंत देखभाल करें।"
    return speech


# ══════════════════════════════════════════════════════════════
# 5. VOICE IVR — Groq AI Agriculture Answers on Call (Bilingual)
# ══════════════════════════════════════════════════════════════

AGRI_VOICE_PROMPT_HI = (
    'You are AgriShield AI — a FEMALE farming assistant that ONLY discusses agriculture topics.\n\n'
    'IMPORTANT: You are a FEMALE assistant. Always use FEMININE Hindi verb forms:\n'
    '- "मैं बता सकती हूं" (NOT "बता सकता हूं")\n'
    '- "मैं सहायता कर सकती हूं" (NOT "कर सकता हूं")\n\n'
    'You MUST:\n'
    '- Only answer questions about farming, crops, soil, weather, irrigation, fertilizers, pesticides, pests, harvest\n'
    '- Respond in HINDI (Devanagari script) ONLY with FEMININE verb forms\n'
    '- Keep responses SHORT (under 3 sentences for telephone voice call)\n'
    '- Be warm, polite, and caring — address farmer as "किसान भाई" or "भैया"\n\n'
    'User said: "{user_speech}"\n\n'
    'Respond in 2-3 short HINDI sentences:'
)

AGRI_VOICE_PROMPT_EN = (
    'You are AgriShield AI — a friendly and helpful agricultural expert assistant calling an Indian farmer.\n\n'
    'You MUST:\n'
    '- Only answer questions about agriculture, crops, soil, pests, diseases, weather, fertilizers, and farming\n'
    '- Respond in CLEAR, SIMPLE ENGLISH that is very easy to understand over a phone call\n'
    '- Keep responses SHORT (under 3 sentences for telephone voice call)\n'
    '- Be respectful and polite, address the caller as "farmer" or "friend"\n\n'
    'User said: "{user_speech}"\n\n'
    'Respond in 2-3 short ENGLISH sentences:'
)


def _call_groq_for_voice(speech_text: str, lang: str = 'hi') -> str:
    """Call Groq API for voice response in selected language (hi or en)."""
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)

    try:
        from services.groq_client import call_groq
        if lang == 'en':
            prompt = AGRI_VOICE_PROMPT_EN.format(user_speech=speech_text)
            fallback = "Hello farmer. Please check your crops regularly and ensure proper irrigation. Happy farming!"
        else:
            prompt = AGRI_VOICE_PROMPT_HI.format(user_speech=speech_text)
            fallback = "नमस्ते किसान भाई। कृपया अपनी फसलों की नियमित निगरानी करें और संतुलित खाद का प्रयोग करें।"

        result = call_groq(
            prompt=prompt,
            temperature=0.5,
            max_tokens=200,
            timeout=15,
            tag="VoiceAI"
        )
        if result.get("success"):
            return result.get("raw", fallback).strip().strip('"\'')
        else:
            return fallback
    except Exception as e:
        print(f"[Twilio] ❌ Groq voice error: {e}")
        return "Sorry, I am having trouble responding right now. Please call again later." if lang == 'en' else "माफ करें भैया, अभी उत्तर देने में समस्या हो रही है। कृपया कुछ समय बाद प्रयास करें।"


def generate_language_selection_twiml() -> str:
    """
    Generate TwiML for incoming call: Plays bilingual language selection prompt.
    Press 1 for Hindi, Press 2 for English.
    """
    from twilio.twiml.voice_response import VoiceResponse, Gather

    response = VoiceResponse()
    gather = Gather(
        input='dtmf',
        num_digits=1,
        action='/voice-lang-select',
        method='POST',
        timeout=8
    )
    gather.say(
        'एग्रीशील्ड एआई में आपका स्वागत है। हिंदी के लिए 1 दबाएं।',
        language='hi-IN',
        voice='Polly.Aditi'
    )
    gather.say(
        'Welcome to AgriShield AI. For English, press 2.',
        language='en-IN',
        voice='Polly.Aditi'
    )
    response.append(gather)

    # Fallback if no key was pressed within timeout -> default to Hindi
    response.say('कोई इनपुट नहीं मिला। हिंदी में जारी रखा जा रहा है।', language='hi-IN', voice='Polly.Aditi')
    response.redirect('/voice-lang-select?Digits=1', method='POST')
    return str(response)


def handle_language_selection(digits: str) -> str:
    """
    Handles user's DTMF selection:
    1 -> Hindi welcome & gather
    2 -> English welcome & gather
    Other -> prompt error and re-gather
    """
    from twilio.twiml.voice_response import VoiceResponse, Gather

    digits = str(digits).strip()
    response = VoiceResponse()

    if digits == '1':
        # Selected: Hindi
        gather = Gather(
            input='speech',
            action='/voice-respond?lang=hi',
            method='POST',
            language='hi-IN',
            speech_timeout='auto',
            timeout=10
        )
        gather.say(
            'नमस्ते किसान भाई! मैं AgriShield AI हूं। मैं आपकी खेती से जुड़ी किसी भी समस्या में सहायता कर सकती हूं। कृपया अपना सवाल बोलिए।',
            language='hi-IN',
            voice='Polly.Aditi'
        )
        response.append(gather)
        response.say(
            'धन्यवाद किसान भाई! आपका दिन शुभ हो। जय किसान!',
            language='hi-IN',
            voice='Polly.Aditi'
        )
        return str(response)

    elif digits == '2':
        # Selected: English
        gather = Gather(
            input='speech',
            action='/voice-respond?lang=en',
            method='POST',
            language='en-IN',
            speech_timeout='auto',
            timeout=10
        )
        gather.say(
            'Hello farmer! I am AgriShield AI. I am here to help you with crop diseases, fertilizers, weather, and farming advice. Please ask your question now.',
            language='en-IN',
            voice='Polly.Aditi'
        )
        response.append(gather)
        response.say(
            'Thank you farmer! AgriShield AI wishes you a successful harvest. Happy farming!',
            language='en-IN',
            voice='Polly.Aditi'
        )
        return str(response)

    else:
        # Invalid selection: Re-prompt
        gather = Gather(
            input='dtmf',
            num_digits=1,
            action='/voice-lang-select',
            method='POST',
            timeout=7
        )
        gather.say(
            'अमान्य विकल्प। हिंदी के लिए 1 दबाएं।',
            language='hi-IN',
            voice='Polly.Aditi'
        )
        gather.say(
            'Invalid option. For English, press 2.',
            language='en-IN',
            voice='Polly.Aditi'
        )
        response.append(gather)
        # Final fallback to Hindi
        response.redirect('/voice-lang-select?Digits=1', method='POST')
        return str(response)


def generate_welcome_twiml() -> str:
    """Legacy helper: points directly to language selection."""
    return generate_language_selection_twiml()


def handle_voice_input(speech_text: str, lang: str = 'hi') -> str:
    """Process farmer's speech in selected language and return Groq AI response as TwiML."""
    from twilio.twiml.voice_response import VoiceResponse, Gather

    lang = 'en' if str(lang).lower().startswith('en') else 'hi'
    voice_lang = 'en-IN' if lang == 'en' else 'hi-IN'

    ai_response = _call_groq_for_voice(speech_text, lang=lang)

    response = VoiceResponse()
    response.say(ai_response, language=voice_lang, voice='Polly.Aditi')

    # Allow follow-up question in the same language
    gather = Gather(
        input='speech',
        action=f'/voice-respond?lang={lang}',
        method='POST',
        language=voice_lang,
        speech_timeout='auto',
        timeout=9
    )

    if lang == 'en':
        gather.say(
            'Do you have any other questions about your crops or farm? Please speak now.',
            language='en-IN',
            voice='Polly.Aditi'
        )
        response.append(gather)
        response.say(
            'Thank you farmer! AgriShield AI is always here for your crops. Have a wonderful day!',
            language='en-IN',
            voice='Polly.Aditi'
        )
    else:
        gather.say(
            'भैया, क्या आप कुछ और पूछना चाहते हैं? मैं आपकी सहायता के लिए यहां हूं।',
            language='hi-IN',
            voice='Polly.Aditi'
        )
        response.append(gather)
        response.say(
            'धन्यवाद किसान भाई! आपका दिन शुभ हो। AgriShield AI आपकी सेवा में हमेशा तैयार है। जय किसान!',
            language='hi-IN',
            voice='Polly.Aditi'
        )

    return str(response)


def generate_alert_call_twiml(scan_data: dict) -> str:
    """Generate TwiML for automated alert call about crop issues."""
    from twilio.twiml.voice_response import VoiceResponse, Gather

    crop = scan_data.get("crop_name", "crop")
    health = scan_data.get("health_score", "Unknown")
    disease = scan_data.get("disease", "no disease")
    treatment = scan_data.get("treatment", "")
    fertilizer = scan_data.get("fertilizer_recommendation", "")

    response = VoiceResponse()

    speech = (
        f"किसान भैया ध्यान दीजिए! मैं AgriShield AI हूं और आपके लिए एक ज़रूरी अलर्ट लेकर आई हूं। "
        f"आपकी {crop} फसल की सेहत सिर्फ {health} प्रतिशत है। "
    )
    if disease and disease.lower() not in ("no disease detected", "none", "n/a", ""):
        speech += f"{disease} बीमारी पाई गई है। "
    if treatment:
        speech += f"इलाज: {treatment}। "
    if fertilizer:
        speech += f"खाद की सिफारिश: {fertilizer}"

    response.say(speech, language='hi-IN', voice='Polly.Aditi')

    # Allow follow-up
    gather = Gather(
        input='speech',
        action='/voice-respond',
        method='POST',
        language='hi-IN',
        speech_timeout='auto',
        timeout=10
    )
    gather.say(
        'भैया, क्या आप इसके बारे में और जानना चाहते हैं? मैं आपकी सहायता कर सकती हूं।',
        language='hi-IN',
        voice='Polly.Aditi'
    )
    response.append(gather)

    response.say(
        'धन्यवाद किसान भाई! आपका दिन शुभ हो। मैं AgriShield AI, आपकी सेवा में हमेशा तैयार हूं। जय किसान!',
        language='hi-IN',
        voice='Polly.Aditi'
    )
    return str(response)
