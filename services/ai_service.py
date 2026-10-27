"""
AgriShield AI — Centralized Multi-Provider AI Service
======================================================
Unified AI layer supporting:
1. Google Gemini API (Fastest Model: gemini-2.5-flash-lite)
2. xAI Grok API (grok-beta / grok-2-latest)
3. Groq LPU (Ultra-fast fallback)

Provides automatic fallback handling, timeout protection, response normalization,
and natural language steering (Hindi / English).
"""

import os
import sys
import json
import base64
import re
import requests
from dotenv import load_dotenv

# Load .env (find near current file or current directory)
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)
else:
    load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
XAI_API_KEY = (os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY", "")).strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

# Default Models
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_FALLBACK_MODEL = "gemini-2.5-flash"
GROK_MODEL = "grok-beta"
GROQ_TEXT_MODEL = os.getenv("GROQ_TEXT_MODEL", "openai/gpt-oss-120b")
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.8-27b")
GROQ_FALLBACK_MODEL = os.getenv("GROQ_FALLBACK_MODEL", "openai/gpt-oss-20b")


def _encode_image(image_path: str) -> tuple:
    """Encode local image file to base64 and guess mime type."""
    if not image_path or not os.path.exists(image_path):
        return None, None
    ext = os.path.splitext(image_path)[1].lower()
    mime = "image/jpeg"
    if ext in ['.png']:
        mime = "image/png"
    elif ext in ['.webp']:
        mime = "image/webp"

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return encoded, mime


def extract_json_object(text: str) -> str:
    """Safely extract JSON substring from Markdown fenced code blocks or raw text."""
    if not text:
        return "{}"
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    # Find outermost { ... } or [ ... ]
    match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)
    if match:
        return match.group(1).strip()
    return text.strip()


def call_gemini(
    prompt: str,
    image_path: str = None,
    json_mode: bool = False,
    system_instruction: str = None,
    max_tokens: int = 2048,
    temperature: float = 0.2,
    timeout: int = 25
) -> dict:
    """Call Google Gemini Generative Language API (gemini-2.5-flash-lite)."""
    if not GEMINI_API_KEY:
        return {"success": False, "error": "GEMINI_API_KEY is not configured", "provider": "gemini"}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

    parts = []
    if image_path and os.path.exists(image_path):
        b64_data, mime = _encode_image(image_path)
        if b64_data:
            parts.append({
                "inlineData": {
                    "mimeType": mime,
                    "data": b64_data
                }
            })

    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        }
    }

    if json_mode:
        payload["generationConfig"]["responseMimeType"] = "application/json"

    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return {"success": True, "text": text, "provider": "gemini", "model": GEMINI_MODEL}
            return {"success": False, "error": "No candidates returned from Gemini", "provider": "gemini"}
        return {"success": False, "error": f"Gemini error HTTP {resp.status_code}: {resp.text[:200]}", "provider": "gemini"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Gemini request timed out", "provider": "gemini"}
    except Exception as e:
        return {"success": False, "error": f"Gemini exception: {str(e)}", "provider": "gemini"}


def call_grok(
    prompt: str,
    json_mode: bool = False,
    system_instruction: str = None,
    max_tokens: int = 2048,
    temperature: float = 0.2,
    timeout: int = 25
) -> dict:
    """Call xAI Grok API (grok-beta)."""
    if not XAI_API_KEY:
        return {"success": False, "error": "XAI_API_KEY is not configured", "provider": "grok"}

    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": GROK_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            choices = data.get("choices", [])
            if choices:
                text = choices[0].get("message", {}).get("content", "")
                return {"success": True, "text": text, "provider": "grok", "model": GROK_MODEL}
            return {"success": False, "error": "No choices returned from Grok", "provider": "grok"}
        return {"success": False, "error": f"Grok error HTTP {resp.status_code}: {resp.text[:200]}", "provider": "grok"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Grok request timed out", "provider": "grok"}
    except Exception as e:
        return {"success": False, "error": f"Grok exception: {str(e)}", "provider": "grok"}


def call_groq(
    prompt: str,
    image_path: str = None,
    json_mode: bool = False,
    system_instruction: str = None,
    max_tokens: int = 2048,
    temperature: float = 0.2,
    timeout: int = 25
) -> dict:
    """Call Groq LPU API as reliable ultra-fast fallback."""
    if not GROQ_API_KEY:
        return {"success": False, "error": "GROQ_API_KEY is not configured", "provider": "groq"}

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    model = GROQ_TEXT_MODEL
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})

    if image_path and os.path.exists(image_path):
        model = GROQ_VISION_MODEL
        b64_data, mime = _encode_image(image_path)
        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64_data}"}}
        ]
        messages.append({"role": "user", "content": content})
    else:
        messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": min(max_tokens, 750) if (image_path and os.path.exists(image_path)) else max_tokens,
    }

    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            choices = data.get("choices", [])
            if choices:
                text = choices[0].get("message", {}).get("content", "")
                return {"success": True, "text": text, "provider": "groq", "model": model}
            return {"success": False, "error": "No choices returned from Groq", "provider": "groq"}

        # Retry with fallback model if not image
        if not image_path:
            payload["model"] = GROQ_FALLBACK_MODEL
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    text = choices[0].get("message", {}).get("content", "")
                    return {"success": True, "text": text, "provider": "groq", "model": GROQ_FALLBACK_MODEL}

        return {"success": False, "error": f"Groq error HTTP {resp.status_code}: {resp.text[:200]}", "provider": "groq"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Groq request timed out", "provider": "groq"}
    except Exception as e:
        return {"success": False, "error": f"Groq exception: {str(e)}", "provider": "groq"}


def call_ai(
    prompt: str,
    provider: str = "groq",
    image_path: str = None,
    json_mode: bool = False,
    system_instruction: str = None,
    language: str = "en",
    max_tokens: int = 2048,
    temperature: float = 0.2,
    timeout: int = 25
) -> dict:
    """
    Central AI Dispatcher with Automatic Multi-Provider Fallback.
    """
    # Enforce language directive in prompt
    lang_clean = "Hindi" if str(language).lower().startswith("hi") else "English"
    if f"respond in {lang_clean}" not in prompt.lower() and f"{lang_clean} language" not in prompt.lower():
        prompt = f"{prompt}\n\nIMPORTANT LANGUAGE INSTRUCTION: The user selected language is '{lang_clean}'. Every single user-facing text, explanation, recommendation, and title MUST be in natural, fluent {lang_clean}."

    providers_order = []
    p = (provider or "groq").lower()
    if p == "grok":
        providers_order = [("grok", call_grok), ("groq", call_groq), ("gemini", call_gemini)]
    elif p == "gemini":
        providers_order = [("gemini", call_gemini), ("groq", call_groq), ("grok", call_grok)]
    else:
        providers_order = [("groq", call_groq), ("gemini", call_gemini), ("grok", call_grok)]

    last_error = None
    for prov_name, prov_func in providers_order:
        try:
            # Grok does not support image upload directly through this endpoint
            if prov_name == "grok" and image_path:
                continue

            kwargs = {
                "prompt": prompt,
                "json_mode": json_mode,
                "system_instruction": system_instruction,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "timeout": timeout
            }
            if prov_name in ["gemini", "groq"]:
                kwargs["image_path"] = image_path

            res = prov_func(**kwargs)
            if res.get("success"):
                raw_text = res.get("text", "")
                if json_mode:
                    clean_json = extract_json_object(raw_text)
                    try:
                        parsed = json.loads(clean_json)
                        return {
                            "success": True,
                            "data": parsed,
                            "raw": raw_text,
                            "provider": res.get("provider"),
                            "model": res.get("model")
                        }
                    except Exception as parse_err:
                        # Continue to fallback if json parsing failed
                        last_error = f"JSON parse error from {prov_name}: {parse_err}"
                        continue
                return {
                    "success": True,
                    "text": raw_text,
                    "provider": res.get("provider"),
                    "model": res.get("model")
                }
            else:
                last_error = f"{prov_name} error: {res.get('error')}"
        except Exception as e:
            last_error = f"{prov_name} exception: {str(e)}"

    return {
        "success": False,
        "error": f"All AI providers failed. Last error: {last_error}",
        "provider": "none"
    }


# Friendly alias
generate_ai_response = call_ai

