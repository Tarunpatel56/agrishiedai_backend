"""
🌾 AgriShield AI — Phone Call Setup + Interactive IVR
======================================================
Ye script:
1. Ngrok tunnel start karegi (public URL banegi)
2. Twilio phone number ka webhook update karegi
3. Ab farmer +13639990565 pe call karega → AI Hindi me jawab dega!

Run: py setup_call.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'agrishield_backend', 'agrishield_backend')))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'agrishield_backend', 'agrishield_backend', '.env'))

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
FARMER_PHONE_NUMBER = os.getenv("FARMER_PHONE_NUMBER")


def step1_check_ngrok_auth():
    """Check if ngrok auth token is configured."""
    print("\n[Step 1] 🔑 Checking ngrok auth token...")

    try:
        from pyngrok import ngrok, conf
        # Try to start a tunnel to see if auth works
        try:
            tunnel = ngrok.connect(5000, "http")
            public_url = tunnel.public_url
            print(f"[✅] Ngrok auth OK! URL: {public_url}")
            ngrok.disconnect(public_url)
            return True
        except Exception as e:
            if "ERR_NGROK_4018" in str(e) or "authentication" in str(e).lower():
                print("[❌] Ngrok auth token nahi set hai!")
                print()
                print("  👉 Ye kar:")
                print("  1. Browser me jaa: https://dashboard.ngrok.com/signup")
                print("  2. Free account bana (Google se sign up kar)")
                print("  3. Dashboard pe jaa: https://dashboard.ngrok.com/get-started/your-authtoken")
                print("  4. Auth token copy kar")
                print()

                token = input("  🔑 Apna ngrok auth token paste kar: ").strip()
                if not token:
                    print("[❌] Token empty hai! Pehle ngrok signup karo.")
                    return False

                # Set the token
                os.system(f'ngrok config add-authtoken {token}')
                print("[✅] Auth token set ho gaya!")
                return True
            else:
                print(f"[❌] Ngrok error: {e}")
                return False
    except ImportError:
        print("[❌] pyngrok installed nahi hai! Run: pip install pyngrok")
        return False


def step2_start_tunnel():
    """Start ngrok tunnel."""
    print("\n[Step 2] 🌐 Starting ngrok tunnel on port 5000...")

    from pyngrok import ngrok

    # Kill existing tunnels
    try:
        for t in ngrok.get_tunnels():
            ngrok.disconnect(t.public_url)
    except:
        pass

    tunnel = ngrok.connect(5000, "http")
    public_url = tunnel.public_url
    print(f"[✅] Ngrok tunnel LIVE: {public_url}")
    return public_url


def step3_update_twilio_webhook(ngrok_url):
    """Update Twilio phone number webhook to point to our ngrok URL."""
    print(f"\n[Step 3] 📞 Updating Twilio webhook for {TWILIO_PHONE_NUMBER}...")

    from twilio.rest import Client
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    # Find the phone number
    numbers = client.incoming_phone_numbers.list(phone_number=TWILIO_PHONE_NUMBER)

    if not numbers:
        print(f"[❌] Phone number {TWILIO_PHONE_NUMBER} not found in Twilio account!")
        return False

    phone_sid = numbers[0].sid

    # Update webhook URLs
    voice_url = f"{ngrok_url}/voice-incoming"
    voice_fallback = f"{ngrok_url}/voice-incoming"

    numbers[0].update(
        voice_url=voice_url,
        voice_method="POST",
        voice_fallback_url=voice_fallback,
        voice_fallback_method="POST",
    )

    print(f"[✅] Webhook updated!")
    print(f"     Voice URL: {voice_url}")
    return True


def main():
    print()
    print("=" * 55)
    print(" 📞 AgriShield AI — Phone Call IVR Setup")
    print(" 🌾 Farmer call karega → AI Hindi me jawab dega!")
    print("=" * 55)
    print(f"  Twilio Number : {TWILIO_PHONE_NUMBER}")
    print(f"  Farmer Number : {FARMER_PHONE_NUMBER}")
    print("=" * 55)

    # Check backend server
    import requests
    try:
        r = requests.get("http://localhost:5000/", timeout=3)
        print(f"\n[✅] Backend server chal rha hai (v{r.json().get('version', '?')})")
    except:
        print("\n[❌] Backend server nahi chal rha!")
        print("    Pehle ye run kar dusre terminal me: py app.py")
        return

    # Step 1: Ngrok auth
    if not step1_check_ngrok_auth():
        return

    # Step 2: Start tunnel
    try:
        ngrok_url = step2_start_tunnel()
    except Exception as e:
        print(f"[❌] Tunnel start nahi hua: {e}")
        return

    # Step 3: Update Twilio webhook
    try:
        if not step3_update_twilio_webhook(ngrok_url):
            return
    except Exception as e:
        print(f"[❌] Twilio update error: {e}")
        return

    # Done!
    print()
    print("=" * 55)
    print(" ✅ SETUP COMPLETE! Phone Call IVR Ready!")
    print("=" * 55)
    print()
    print(f" 📞 Ab {TWILIO_PHONE_NUMBER} pe call karo apne phone se!")
    print(f"    → AI Hindi me welcome karega")
    print(f"    → Apna agriculture sawaal bolo")
    print(f"    → AI Groq se jawab dega Hindi me")
    print(f"    → Cross question bhi pooch sakte ho!")
    print()
    print(f" 🌐 Ngrok URL: {ngrok_url}")
    print(f" 📡 Webhook:   {ngrok_url}/voice-incoming")
    print()
    print(" ⚠️  Ye terminal band mat karna! Ngrok tunnel yahi se chal rhi hai.")
    print(" ⚠️  Ctrl+C se band kar sakte ho jab done ho jao.")
    print()

    # Keep running
    try:
        print(" [🟢 LIVE — Waiting for calls... Press Ctrl+C to stop]\n")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n [🔴] Ngrok tunnel stopped. Bye! Jay Kisaan! 🌾\n")
        from pyngrok import ngrok
        ngrok.kill()


if __name__ == "__main__":
    main()
