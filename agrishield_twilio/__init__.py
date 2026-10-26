"""
AgriShield Twilio Module
========================
All Twilio-related code: SMS, WhatsApp, Voice Calls, Voice IVR with Groq AI,
and Bilingual Language Selection (Hindi/English).
"""

from agrishield_twilio.twilio_all import (
    # Config
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
    FARMER_PHONE_NUMBER,
    FARMER_WHATSAPP_NUMBER,
    # SMS / WhatsApp
    send_sms,
    send_whatsapp,
    # Voice Call
    make_voice_call,
    # Alert Formatters
    format_crop_alert,
    format_soil_alert,
    format_voice_alert,
    # Voice IVR (Groq AI) & Bilingual Language Selection
    generate_language_selection_twiml,
    handle_language_selection,
    generate_welcome_twiml,
    handle_voice_input,
    generate_alert_call_twiml,
)
