"""
AgriShield Twilio Test Script
==============================
Terminal se run karo: py test_twilio.py

Ye script Twilio call feature test karti hai.
Real scan data bhi use kar sakte ho!
"""

import os
import sys
import json

# Add paths for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'agrishield_backend', 'agrishield_backend')))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'agrishield_backend', 'agrishield_backend', '.env'))

from agrishield_twilio import make_voice_call, format_voice_alert, FARMER_PHONE_NUMBER, TWILIO_PHONE_NUMBER
from services.groq_client import call_groq


# ══════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════
LAST_SCAN_FILE = os.path.join(os.path.dirname(__file__), '..', 'agrishield_backend', 'agrishield_backend', 'last_scan.json')

VOICE_PROMPT_HINDI = """You are AgriShield AI — calling a farmer to give agriculture advice.

Generate a SHORT voice message (3-5 sentences) IN HINDI (Devanagari script).
Rules:
1. Greet: "नमस्ते किसान भाई!"
2. Give farming advice in simple Hindi
3. End with "जय किसान!"
4. NO English, NO formatting, NO quotes

{crop_info}

Respond in HINDI only (Devanagari):"""


def load_last_scan():
    """Load the last crop scan data from file."""
    if os.path.exists(LAST_SCAN_FILE):
        with open(LAST_SCAN_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"[✅] Last scan loaded: {data.get('crop_name', '?')} ({data.get('crop_name_hindi', '?')})")
            print(f"     Health: {data.get('health_score', '?')}/100 | Disease: {data.get('disease', '?')}")
            return data
    else:
        print("[❌] No last_scan.json found! Pehle app me crop scan karo.")
        return None


def generate_hindi_message(scan_data=None, custom_message=None):
    """Groq AI se Hindi agriculture message banao."""
    if scan_data:
        crop_info = (
            f"Crop: {scan_data.get('crop_name', 'Unknown')} ({scan_data.get('crop_name_hindi', '')})\n"
            f"Health: {scan_data.get('health_score', 'N/A')}/100\n"
            f"Disease: {scan_data.get('disease', 'None')}\n"
            f"Treatment: {scan_data.get('treatment', 'N/A')}\n"
            f"Fertilizer: {scan_data.get('fertilizer_recommendation', 'N/A')}\n"
            f"Irrigation: {scan_data.get('irrigation_advice', 'N/A')}"
        )
    elif custom_message:
        crop_info = f"Context: {custom_message}"
    else:
        crop_info = "General seasonal farming advice for Indian farmers."

    prompt = VOICE_PROMPT_HINDI.format(crop_info=crop_info)

    print("[🤖] Groq AI se Hindi message generate ho rha hai...")
    result = call_groq(prompt=prompt, temperature=0.6, max_tokens=300, timeout=15, tag="TestCall")

    if result.get("success"):
        msg = result["raw"].strip().strip('"\'')
        print(f"[🤖] AI Message: {msg[:150]}...")
        return msg
    else:
        print(f"[❌] Groq error: {result.get('error')}")
        fallback = "नमस्ते किसान भाई! अपनी फसलों की देखभाल करें। सही समय पर सिंचाई और खाद डालें। जय किसान!"
        print(f"[⚠️] Fallback message use ho rha hai")
        return fallback


def test_call_with_scan():
    """Test 1: Real scan data se call karo."""
    print("\n" + "=" * 50)
    print("📞 TEST 1: REAL SCAN DATA SE CALL")
    print("=" * 50)

    scan_data = load_last_scan()
    if not scan_data:
        return

    voice_text = generate_hindi_message(scan_data=scan_data)

    print(f"\n[📞] Calling {FARMER_PHONE_NUMBER}...")
    result = make_voice_call(to=FARMER_PHONE_NUMBER, twiml_text=voice_text)

    if result.get("success"):
        print(f"[✅] Call Success! SID: {result['sid']}")
        print(f"[📱] {FARMER_PHONE_NUMBER} pe call aa rahi hai!")
    else:
        print(f"[❌] Call Failed: {result.get('error')}")
    return result


def test_call_custom_message(message):
    """Test 2: Custom message se call karo."""
    print("\n" + "=" * 50)
    print(f"📞 TEST 2: CUSTOM MESSAGE CALL")
    print(f"   Message: {message}")
    print("=" * 50)

    voice_text = generate_hindi_message(custom_message=message)

    print(f"\n[📞] Calling {FARMER_PHONE_NUMBER}...")
    result = make_voice_call(to=FARMER_PHONE_NUMBER, twiml_text=voice_text)

    if result.get("success"):
        print(f"[✅] Call Success! SID: {result['sid']}")
    else:
        print(f"[❌] Call Failed: {result.get('error')}")
    return result


def test_call_simple():
    """Test 3: Simple static Hindi message call."""
    print("\n" + "=" * 50)
    print("📞 TEST 3: SIMPLE STATIC CALL")
    print("=" * 50)

    message = "नमस्ते किसान भाई! यह AgriShield AI है। अपनी फसलों की नियमित जांच करें। धन्यवाद!"
    print(f"[💬] Message: {message}")

    print(f"\n[📞] Calling {FARMER_PHONE_NUMBER}...")
    result = make_voice_call(to=FARMER_PHONE_NUMBER, twiml_text=message)

    if result.get("success"):
        print(f"[✅] Call Success! SID: {result['sid']}")
    else:
        print(f"[❌] Call Failed: {result.get('error')}")
    return result


def show_menu():
    """Show test options."""
    print("\n" + "=" * 50)
    print("  🌾 AgriShield Twilio Test Menu 🌾")
    print("=" * 50)
    print(f"  Twilio Number : {TWILIO_PHONE_NUMBER}")
    print(f"  Farmer Number : {FARMER_PHONE_NUMBER}")
    print("=" * 50)
    print()
    print("  1. 📞 Real Scan Data se Call  (last_scan.json)")
    print("  2. 📞 Custom Message Call     (tu likh ke de)")
    print("  3. 📞 Simple Static Call      (fixed Hindi msg)")
    print("  4. 📋 Last Scan Data Dekho")
    print("  5. ❌ Exit")
    print()


def main():
    """Interactive test menu."""
    show_menu()

    while True:
        choice = input("👉 Choose (1-5): ").strip()

        if choice == "1":
            test_call_with_scan()
        elif choice == "2":
            msg = input("💬 Apna message likho: ").strip()
            if msg:
                test_call_custom_message(msg)
            else:
                print("[⚠️] Message empty hai!")
        elif choice == "3":
            test_call_simple()
        elif choice == "4":
            scan = load_last_scan()
            if scan:
                print(json.dumps(scan, indent=2, ensure_ascii=False))
        elif choice == "5":
            print("\n[👋] Bye! Jay Kisaan! 🌾")
            break
        else:
            print("[⚠️] 1-5 me se choose karo!")

        print()


if __name__ == "__main__":
    main()
