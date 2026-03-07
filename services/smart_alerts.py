"""
Smart Alert Engine
==================
Automatically evaluates scan/analysis data and triggers
appropriate Twilio alerts (SMS, WhatsApp, Voice Call).

Alert Levels:
  🔴 CRITICAL (health < 30)  → Voice Call + WhatsApp + SMS
  🟡 WARNING  (health < 50 OR disease) → WhatsApp + SMS
  🟢 INFO     (low confidence, weather) → SMS only
"""

import json
import os
from datetime import datetime
from services.twilio_service import (
    send_sms, send_whatsapp, make_voice_call,
    format_crop_alert, format_soil_alert, format_voice_alert,
)

# Alert history stored in-memory + file
ALERT_HISTORY_FILE = "project_data/alert_history.json"
os.makedirs("project_data", exist_ok=True)

def _load_alert_history() -> list:
    """Load alert history from file."""
    try:
        if os.path.exists(ALERT_HISTORY_FILE):
            with open(ALERT_HISTORY_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return []


def _save_alert(alert_record: dict):
    """Save alert to history file."""
    try:
        history = _load_alert_history()
        history.insert(0, alert_record)
        # Keep last 100 alerts
        history = history[:100]
        with open(ALERT_HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[SmartAlert] ❌ Error saving alert: {e}")


def get_alert_history(limit: int = 50) -> list:
    """Get recent alert history."""
    history = _load_alert_history()
    return history[:limit]


# ── Main Alert Engine ────────────────────────────────────────
def check_and_trigger_crop_alerts(scan_data: dict) -> dict:
    """
    Evaluate crop scan data and automatically trigger alerts.
    
    Logic:
      - health_score < 30 → CRITICAL → Call + WhatsApp + SMS
      - health_score < 50 OR disease → WARNING → WhatsApp + SMS
      - health_score >= 50 → INFO → SMS only (report)
    """
    health_score = scan_data.get("health_score", 100)
    disease = scan_data.get("disease", "No disease detected")
    crop_name = scan_data.get("crop_name", "Unknown")
    
    has_disease = disease.lower() not in ["no disease detected", "none", "n/a", ""]
    
    alert_level = "INFO"
    actions_taken = []
    
    # Determine alert level
    if health_score < 30:
        alert_level = "CRITICAL"
    elif health_score < 50 or has_disease:
        alert_level = "WARNING"
    
    print(f"[SmartAlert] 🔔 Crop: {crop_name} | Health: {health_score} | "
          f"Disease: {disease} | Level: {alert_level}")
    
    # Format messages
    sms_body = format_crop_alert(scan_data)
    
    # Execute alerts based on level
    if alert_level == "CRITICAL":
        # 🔴 CRITICAL: Call + WhatsApp + SMS
        voice_twiml = format_voice_alert(scan_data)
        call_result = make_voice_call(twiml_text=voice_twiml)
        actions_taken.append({"type": "voice_call", "result": call_result})
        
        wa_result = send_whatsapp(body=sms_body)
        actions_taken.append({"type": "whatsapp", "result": wa_result})
        
        sms_result = send_sms(body=f"🚨 CRITICAL ALERT: {crop_name} health {health_score}%! Check WhatsApp for details.")
        actions_taken.append({"type": "sms", "result": sms_result})
        
    elif alert_level == "WARNING":
        # 🟡 WARNING: WhatsApp + SMS
        wa_result = send_whatsapp(body=sms_body)
        actions_taken.append({"type": "whatsapp", "result": wa_result})
        
        sms_result = send_sms(body=f"⚠️ WARNING: {crop_name} needs attention! Health: {health_score}%. Disease: {disease}")
        actions_taken.append({"type": "sms", "result": sms_result})
        
    else:
        # 🟢 INFO: SMS only
        sms_result = send_sms(body=f"✅ {crop_name} scan complete. Health: {health_score}%. All good!")
        actions_taken.append({"type": "sms", "result": sms_result})
    
    # Save to alert history
    alert_record = {
        "timestamp": datetime.now().isoformat(),
        "type": "crop_scan",
        "alert_level": alert_level,
        "crop_name": crop_name,
        "health_score": health_score,
        "disease": disease,
        "actions": [a["type"] for a in actions_taken],
        "results": actions_taken,
    }
    _save_alert(alert_record)
    
    return {
        "alert_level": alert_level,
        "actions_taken": len(actions_taken),
        "details": actions_taken,
    }


def check_and_trigger_soil_alerts(soil_data: dict) -> dict:
    """
    Evaluate soil analysis and send report via WhatsApp + SMS.
    Soil alerts are typically INFO level.
    """
    soil_type = soil_data.get("soil_type", "Unknown")
    
    print(f"[SmartAlert] 🔔 Soil Analysis: {soil_type}")
    
    body = format_soil_alert(soil_data)
    actions_taken = []
    
    # Always send soil report via WhatsApp + SMS
    wa_result = send_whatsapp(body=body)
    actions_taken.append({"type": "whatsapp", "result": wa_result})
    
    sms_result = send_sms(body=f"🌍 Soil Report: {soil_type}. Check WhatsApp for details!")
    actions_taken.append({"type": "sms", "result": sms_result})
    
    alert_record = {
        "timestamp": datetime.now().isoformat(),
        "type": "soil_analysis",
        "alert_level": "INFO",
        "soil_type": soil_type,
        "actions": [a["type"] for a in actions_taken],
        "results": actions_taken,
    }
    _save_alert(alert_record)
    
    return {
        "alert_level": "INFO",
        "actions_taken": len(actions_taken),
        "details": actions_taken,
    }


def send_manual_alert(message: str, level: str = "INFO") -> dict:
    """Send a manual alert (for testing or custom notifications)."""
    actions_taken = []
    
    if level == "CRITICAL":
        # ⚠️ COMMENTED OUT — Twilio disabled
        # response = __import__("twilio.twiml.voice_response", fromlist=["VoiceResponse"]).VoiceResponse()
        # response.say(message, language="en-IN", voice="Polly.Aditi")
        voice_twiml = message  # Plain text instead of TwiML
        call_result = make_voice_call(twiml_text=voice_twiml)
        actions_taken.append({"type": "voice_call", "result": call_result})
    
    wa_result = send_whatsapp(body=message)
    actions_taken.append({"type": "whatsapp", "result": wa_result})
    
    sms_result = send_sms(body=message[:160])  # SMS limit
    actions_taken.append({"type": "sms", "result": sms_result})
    
    alert_record = {
        "timestamp": datetime.now().isoformat(),
        "type": "manual",
        "alert_level": level,
        "message": message[:200],
        "actions": [a["type"] for a in actions_taken],
    }
    _save_alert(alert_record)
    
    return {
        "alert_level": level,
        "actions_taken": len(actions_taken),
        "details": actions_taken,
    }


# ── Weather Alert Engine ─────────────────────────────────────
def check_and_trigger_weather_alerts(weather_data: dict) -> dict:
    """
    Evaluate weather data and automatically trigger alerts.
    
    Logic:
      - Heat wave (>38°C), Frost (<5°C), Heavy rain (>10mm) → CRITICAL → Call + WhatsApp + SMS
      - High temp (>34°C), High humidity (>85%), Strong wind (>20 km/h) → WARNING → WhatsApp + SMS
      - Normal weather → No alert triggered (skip)
    """
    temp = weather_data.get("temperature", 25)
    rain = weather_data.get("rainfall", 0)
    humidity = weather_data.get("humidity", 50)
    wind = weather_data.get("wind_speed", 5)
    condition = weather_data.get("condition", "Clear")
    
    # Determine alert level and reasons
    alert_level = None
    reasons = []
    
    # CRITICAL conditions
    if temp > 38:
        alert_level = "CRITICAL"
        reasons.append(f"🔥 Heat Wave: {temp}°C")
    if temp < 5:
        alert_level = "CRITICAL"
        reasons.append(f"🥶 Frost Warning: {temp}°C")
    if rain > 10:
        alert_level = "CRITICAL"
        reasons.append(f"🌧️ Heavy Rainfall: {rain}mm")
    
    # WARNING conditions (only if not already CRITICAL)
    if not alert_level:
        if temp > 34:
            alert_level = "WARNING"
            reasons.append(f"🌡️ High Temperature: {temp}°C")
        if humidity > 85:
            alert_level = "WARNING"
            reasons.append(f"💧 High Humidity: {humidity}% — Disease Risk")
        if wind > 20:
            alert_level = "WARNING"
            reasons.append(f"💨 Strong Wind: {wind} km/h")
    
    # No alert needed
    if not alert_level:
        return {"alert_level": "NONE", "skipped": True, "message": "Weather is normal"}
    
    reason_text = "\n".join(reasons)
    
    msg = f"""⛈️ *AgriShield Weather Alert* ⛈️

🚨 Level: {alert_level}
🌤️ Condition: {condition}
🌡️ Temperature: {temp}°C
💧 Humidity: {humidity}%
🌧️ Rainfall: {rain}mm
💨 Wind: {wind} km/h

{reason_text}

⚠️ Take precautions to protect your crops!
🤖 Powered by AgriShield AI"""
    
    actions_taken = []
    
    print(f"[SmartAlert] 🌦️ Weather Alert: {alert_level} | Reasons: {reasons}")
    
    if alert_level == "CRITICAL":
        # Voice call for critical weather
        # ⚠️ COMMENTED OUT — Twilio disabled
        # from twilio.twiml.voice_response import VoiceResponse
        # response = VoiceResponse()
        speech = (
            f"Hello farmer! This is an urgent weather alert from AgriShield AI. "
            f"{'. '.join(reasons)}. "
            f"Please take immediate action to protect your crops. "
            f"Check your WhatsApp for full details. Thank you!"
        )
        # response.say(speech, language="en-IN", voice="Polly.Aditi")
        call_result = make_voice_call(twiml_text=speech)
        actions_taken.append({"type": "voice_call", "result": call_result})
        
        wa_result = send_whatsapp(body=msg)
        actions_taken.append({"type": "whatsapp", "result": wa_result})
        
        sms_result = send_sms(body=f"🚨 CRITICAL WEATHER: {', '.join(reasons)}. Check WhatsApp!")
        actions_taken.append({"type": "sms", "result": sms_result})
        
    elif alert_level == "WARNING":
        wa_result = send_whatsapp(body=msg)
        actions_taken.append({"type": "whatsapp", "result": wa_result})
        
        sms_result = send_sms(body=f"⚠️ WEATHER WARNING: {', '.join(reasons)}. Check WhatsApp!")
        actions_taken.append({"type": "sms", "result": sms_result})
    
    # Save to alert history
    alert_record = {
        "timestamp": datetime.now().isoformat(),
        "type": "weather",
        "alert_level": alert_level,
        "temperature": temp,
        "humidity": humidity,
        "rainfall": rain,
        "wind_speed": wind,
        "reasons": reasons,
        "actions": [a["type"] for a in actions_taken],
        "results": actions_taken,
    }
    _save_alert(alert_record)
    
    return {
        "alert_level": alert_level,
        "actions_taken": len(actions_taken),
        "details": actions_taken,
    }

