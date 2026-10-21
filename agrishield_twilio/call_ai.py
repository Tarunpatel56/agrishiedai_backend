"""
🌾 AgriShield AI — Interactive Agriculture Call (Terminal)
===========================================================
Tujhe AI se baat karni hai agriculture ke baare me?
Ye run kar: py call_ai.py

Features:
- Hindi me jawab dega (Devanagari)
- Sirf agriculture ke baare me batayega
- Cross question kar sakta hai — conversation history maintain hogi
- Type 'exit' to end the call
- Uses Groq API directly!
"""

import os
import sys
import requests
from datetime import datetime

# Fix Windows terminal encoding for emoji output
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Setup paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'agrishield_backend', 'agrishield_backend')))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'agrishield_backend', 'agrishield_backend', '.env'))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"



SYSTEM_PROMPT = """You are AgriShield AI — an expert agriculture assistant on a PHONE CALL with an Indian farmer.

STRICT RULES:
1. ONLY answer questions about: farming, crops, soil, weather, irrigation, fertilizers, pesticides, harvest, seeds, government schemes for farmers, animal husbandry, dairy farming, poultry, fishery, organic farming
2. ALWAYS respond in HINDI (Devanagari script) — simple Hindi that any farmer can understand
3. Keep responses SHORT (3-5 sentences) since this is a voice call
4. Be warm, friendly, and practical
5. If farmer asks about disease/pest, give: cause + organic solution + chemical solution
6. If farmer asks about crop, give: season, soil type, irrigation, fertilizer info
7. If someone asks NON-agriculture question, politely say: "माफ करें किसान भाई, मैं सिर्फ खेती-बाड़ी से जुड़े सवालों में मदद कर सकता हूं। कृपया खेती से जुड़ा सवाल पूछें।"
8. Address the farmer as "किसान भाई" or "भाई"
9. End important advice with "जय किसान! 🌾"

You are having a CONVERSATION — remember what the farmer said earlier and answer follow-up questions accordingly."""


def call_groq_chat(messages: list) -> str:
    """Call Groq API with full conversation history."""
    if not GROQ_API_KEY:
        return "❌ GROQ_API_KEY not set in .env!"

    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 500,
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=20)
        if resp.status_code != 200:
            error_text = resp.text[:300]
            return f"❌ API Error {resp.status_code}: {resp.text[:100]}"
        return resp.json()["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "❌ API timeout! Dobara try karo."
    except Exception as e:
        return f"❌ Error: {e}"


def main():
    print()
    print("=" * 55)
    print("  📞 AgriShield AI — Interactive Agriculture Call")
    print("  🌾 Hindi me baat karo, agriculture ke baare me!")
    print("=" * 55)
    print()
    print("  💡 Commands:")
    print("     • Agriculture question type karo Hindi/English me")
    print("     • Cross questions bhi pooch sakte ho")
    print("     • 'history' — puri conversation dekho")
    print("     • 'clear'   — naya topic shuru karo")
    print("     • 'exit'    — call end karo")
    print()
    print("-" * 55)

    # Conversation history with system prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    turn_count = 0

    # Welcome message
    welcome = call_groq_chat(messages + [{"role": "user", "content": "Mujhe namaste bolo aur batao ki tum kya kya help kar sakte ho farming me. 2-3 lines me batao."}])
    print(f"\n  🤖 AI: {welcome}")
    messages.append({"role": "assistant", "content": welcome})
    print()

    while True:
        try:
            user_input = input("  👨‍🌾 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  [👋] Call end! Jay Kisaan! 🌾\n")
            break

        if not user_input:
            continue

        # Commands
        if user_input.lower() == 'exit':
            # Goodbye
            messages.append({"role": "user", "content": "Alvida bolo aur ek achhi farming tip do."})
            goodbye = call_groq_chat(messages)
            print(f"\n  🤖 AI: {goodbye}")
            print(f"\n  [📞 Call Ended — {turn_count} questions asked]\n")
            break

        if user_input.lower() == 'clear':
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            turn_count = 0
            print("\n  [🔄] Conversation cleared! Naya topic shuru karo.\n")
            continue

        if user_input.lower() == 'history':
            print(f"\n  [📋] Conversation History ({turn_count} turns):")
            print("  " + "-" * 50)
            for m in messages[1:]:  # Skip system prompt
                role = "👨‍🌾 You" if m["role"] == "user" else "🤖 AI"
                print(f"  {role}: {m['content'][:200]}")
            print("  " + "-" * 50 + "\n")
            continue

        # Send to AI with full history
        turn_count += 1
        messages.append({"role": "user", "content": user_input})

        print(f"\n  [⏳] Groq AI soch rha hai...\n")
        ai_response = call_groq_chat(messages)

        messages.append({"role": "assistant", "content": ai_response})
        print(f"  🤖 AI: {ai_response}")
        print()


if __name__ == "__main__":
    main()

