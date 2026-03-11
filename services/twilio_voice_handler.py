"""
Twilio Voice Webhook Handler
=============================
Handles incoming voice webhooks from Twilio.
Agriculture-only AI voice responses using Groq.
"""
from twilio.twiml.voice_response import VoiceResponse, Gather
from services.groq_client import call_groq

AGRI_VOICE_PROMPT = (
    'You are AgriShield AI — a farming assistant that ONLY discusses agriculture topics.\n\n'
    'You MUST:\n'
    '- Only answer questions about farming, crops, soil, weather, irrigation, fertilizers, pesticides, harvest\n'
    '- Respond in simple English\n'
    '- Keep responses SHORT (under 3 sentences for voice)\n'
    '- Be helpful and practical for Indian farmers\n\n'
    'You MUST NOT:\n'
    '- Discuss any non-agricultural topics\n'
    '- If asked about anything else, politely say: "I can only help with agriculture-related topics."\n\n'
    'User said: "{user_speech}"\n\n'
    'Respond in 2-3 short English sentences:'
)


def generate_welcome_twiml() -> str:
    """Generate TwiML for incoming call welcome + gather speech input."""
    response = VoiceResponse()
    gather = Gather(
        input='speech',
        action='/voice-respond',
        method='POST',
        language='en-IN',
        speech_timeout='auto',
        timeout=10
    )
    gather.say(
        'Hello! This is AgriShield AI. You can ask any question about your crops or farming. Please speak now.',
        language='en-IN',
        voice='Polly.Aditi'
    )
    response.append(gather)
    response.say(
        'Sorry, we could not hear you. Please call again. Thank you!',
        language='en-IN',
        voice='Polly.Aditi'
    )
    return str(response)


def handle_voice_input(speech_text: str) -> str:
    """
    Process farmer's speech input and generate AI response.
    Only agriculture topics allowed.
    """
    prompt = AGRI_VOICE_PROMPT.format(user_speech=speech_text)

    result = call_groq(
        prompt=prompt,
        temperature=0.5,
        max_tokens=200,
        timeout=15,
        tag="VoiceAI"
    )

    if result.get("success"):
        ai_response = result.get("raw", "Sorry, there is a problem responding right now. Please try again later.")
    else:
        ai_response = "Sorry, there is a problem responding right now. Please try again later."

    response = VoiceResponse()
    response.say(ai_response, language='en-IN', voice='Polly.Aditi')

    # Allow follow-up
    if len(ai_response) > 0:
        gather = Gather(
            input='speech',
            action='/voice-respond',
            method='POST',
            language='en-IN',
            speech_timeout='auto',
            timeout=10
        )
        gather.say(
            'Would you like to ask anything else?',
            language='en-IN',
            voice='Polly.Aditi'
        )
        response.append(gather)

    response.say(
        'Thank you! AgriShield AI is always here to help. Happy Farming!',
        language='en-IN',
        voice='Polly.Aditi'
    )
    return str(response)


def generate_alert_call_twiml(scan_data: dict) -> str:
    """
    Generate TwiML for an automated alert call about crop issues.
    This speaks the alert in Hindi and offers to answer questions.
    """
    crop = scan_data.get("crop_name", "crop")
    crop_hi = scan_data.get("crop_name_hindi", "crop")
    health = scan_data.get("health_score", "Unknown")
    disease = scan_data.get("disease", "no disease")
    treatment = scan_data.get("treatment", "")
    fertilizer = scan_data.get("fertilizer_recommendation", "")

    response = VoiceResponse()

    # Build alert speech
    speech = f"Hello farmer! This is an emergency alert from AgriShield AI. Your {crop} crop health is only {health} percent. "

    if disease and disease.lower() not in ("no disease detected", "none", "n/a", ""):
        speech += f"{disease} disease has been detected in the crop. "
    if treatment:
        speech += f"Treatment: {treatment}. "
    if fertilizer:
        speech += f"Fertilizer recommendation: {fertilizer}"

    response.say(speech, language='en-IN', voice='Polly.Aditi')

    # Allow follow-up questions
    if len(speech) > 0:
        gather = Gather(
            input='speech',
            action='/voice-respond',
            method='POST',
            language='en-IN',
            speech_timeout='auto',
            timeout=10
        )
        gather.say(
            'Would you like to know more about this? Please speak.',
            language='en-IN',
            voice='Polly.Aditi'
        )
        response.append(gather)

    response.say(
        'Thank you! The full report has been sent to your WhatsApp. Happy Farming!',
        language='en-IN',
        voice='Polly.Aditi'
    )
    return str(response)
