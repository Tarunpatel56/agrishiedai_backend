"""
Central AI API Client — Groq (Latest Models)
=============================================
Single source of truth for all AI API interactions.

Model Hierarchy (as of Oct 2026):
  TEXT  → moonshotai/kimi-k2-instruct   (1T MoE params, 128K ctx — Groq's fastest/smartest)
  VISION→ meta-llama/llama-4-scout-17b-16e-instruct  (multimodal vision support)
  FALLBACK → openai/gpt-oss-120b        (120B OpenAI OSS on Groq LPU)

All API keys loaded from .env
"""

import os
import base64
import json
import re
import time
import requests
from dotenv import load_dotenv

# Load .env once
load_dotenv()

# ── Config ───────────────────────────────────────────────────
# Load .env (find near current file or current directory)
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)
else:
    load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_FALLBACK_MODEL = "gemini-2.5-flash"

# ── Model Constants (Active on Groq LPU) ──────────────────────
GROQ_TEXT_MODEL     = os.getenv("GROQ_TEXT_MODEL", "openai/gpt-oss-120b")
GROQ_VISION_MODEL   = os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.8-27b")
GROQ_FALLBACK_MODEL = os.getenv("GROQ_FALLBACK_MODEL", "openai/gpt-oss-20b")

# Maximum output tokens allowed for Groq Vision (qwen/qwen3.8-27b on on_demand tier has 1000 OTPM rate limit)
GROQ_VISION_MAX_TOKENS = 750


# ── Shared Helpers ───────────────────────────────────────────
def encode_image_to_base64(image_path: str) -> str:
    """Encode an image file to base64 string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_mime_type(image_path: str) -> str:
    """Get MIME type from file extension."""
    ext = image_path.lower().split('.')[-1]
    mime_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
    }
    return mime_map.get(ext, "image/jpeg")


def parse_json_response(raw_text: str) -> str:
    """Strip markdown fences from response text."""
    text = raw_text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    return text


def extract_json_object(text: str) -> str:
    """Find the first JSON object {...} in text."""
    match = re.search(r'\{[\s\S]*\}', text)
    return match.group() if match else text


def extract_json_array(text: str) -> str:
    """Find the first JSON array [...] in text."""
    match = re.search(r'\[[\s\S]*\]', text)
    return match.group() if match else text


# ── Gemini Multi-Modal Fallback ──────────────────────────────
def call_gemini_api(
    prompt: str,
    images: list = None,
    temperature: float = 0.2,
    max_tokens: int = 2048,
    timeout: int = 30,
    tag: str = "Gemini",
) -> dict:
    """
    Direct high-throughput multimodal call via Google Gemini Generative Language API.
    Used seamlessly when Groq LPU hits rate limits (429 OTPM) or server spikes.
    """
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY not configured", "success": False}

    parts = []
    if images:
        for img_path in images:
            if img_path and os.path.exists(img_path):
                b64 = encode_image_to_base64(img_path)
                mime = get_mime_type(img_path)
                parts.append({
                    "inlineData": {
                        "mimeType": mime,
                        "data": b64
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

    # Attempt primary model then fallback model
    models_to_try = [GEMINI_MODEL]
    if GEMINI_FALLBACK_MODEL not in models_to_try:
        models_to_try.append(GEMINI_FALLBACK_MODEL)

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        try:
            print(f"[AgriShield][{tag}] Calling Gemini Vision/Text ({model_name})...")
            resp = requests.post(url, json=payload, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    raw = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    print(f"[AgriShield][{tag}] ✅ Gemini responded ({len(raw)} chars) from {model_name}")
                    return {"raw": raw, "success": True, "model": model_name, "provider": "gemini"}
            elif resp.status_code in [503, 429, 404]:
                print(f"[AgriShield][{tag}] Gemini {model_name} HTTP {resp.status_code}, trying next candidate...")
                continue
            else:
                print(f"[AgriShield][{tag}] Gemini {model_name} HTTP {resp.status_code}: {resp.text[:200]}")
        except requests.exceptions.Timeout:
            print(f"[AgriShield][{tag}] Gemini timeout on {model_name}")
            continue
        except Exception as e:
            print(f"[AgriShield][{tag}] Gemini exception on {model_name}: {e}")
            continue

    return {"error": "All Gemini endpoints unavailable", "success": False}


# ── Core AI API Call (Groq + Gemini Dual-Engine) ──────────────
def call_groq(
    prompt: str,
    images: list = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
    timeout: int = 60,
    tag: str = "Groq",
) -> dict:
    """
    Call AI API via Groq with automated Gemini dual-engine fallback.
    Safely handles Groq free tier 429 rate limit (1000 OTPM) by clamping tokens
    and immediately falling back to Gemini Vision on any 429 or server error.
    """
    if not GROQ_API_KEY and not GEMINI_API_KEY:
        return {"error": "No AI API keys configured", "success": False}

    # If Groq key not set, route immediately to Gemini
    if not GROQ_API_KEY and GEMINI_API_KEY:
        return call_gemini_api(prompt, images=images, temperature=temperature, max_tokens=max_tokens, timeout=30, tag=f"{tag}-Gemini")

    # For vision requests, prefer Gemini Generative AI (1M TPM, rich JSON, no 429 OTPM limit)
    # with automatic seamless fallback to Groq Vision
    if images and GEMINI_API_KEY and os.getenv("VISION_PREFERRED_PROVIDER", "gemini").lower() == "gemini":
        print(f"[AgriShield][{tag}] 🚀 Vision request: routing to high-throughput Gemini Vision...")
        gemini_res = call_gemini_api(prompt, images=images, temperature=temperature, max_tokens=max_tokens, timeout=30, tag=tag)
        if gemini_res.get("success"):
            return gemini_res
        print(f"[AgriShield][{tag}] Gemini Vision failed ({gemini_res.get('error')}), falling back to Groq Vision...")

    # Build Groq payload
    groq_max_tokens = max_tokens
    if images:
        # Clamp Groq Vision max_tokens to 750 so Groq token estimator doesn't trigger:
        # "Request too large ... on output tokens per minute (OTPM): Limit 1000, Requested 1173"
        groq_max_tokens = min(max_tokens, GROQ_VISION_MAX_TOKENS)
        content = [{"type": "text", "text": prompt}]
        for img_path in images:
            b64 = encode_image_to_base64(img_path)
            mime = get_mime_type(img_path)
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"}
            })
    else:
        content = prompt

    # Use vision model when images provided, text model otherwise
    selected_model = GROQ_VISION_MODEL if images else GROQ_TEXT_MODEL

    payload = {
        "model": selected_model,
        "messages": [{"role": "user", "content": content}],
        "temperature": temperature,
        "max_tokens": groq_max_tokens,
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        print(f"[AgriShield][{tag}] Calling Groq ({selected_model})...")
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=timeout)

        if resp.status_code == 200:
            raw = resp.json()["choices"][0]["message"]["content"]
            print(f"[AgriShield][{tag}] Response received ({len(raw)} chars) from {selected_model}")
            return {"raw": raw, "success": True, "model": selected_model, "provider": "groq"}

        # Groq returned non-200 (e.g. 429 Rate Limit, 503, 400, etc.)
        error_text = resp.text[:300]
        print(f"[AgriShield][{tag}] Groq Error {resp.status_code}: {error_text}")

        # If Vision failed (especially 429 OTPM limit exceeded), seamlessly fall back to Gemini Vision
        if images and GEMINI_API_KEY:
            print(f"[AgriShield][{tag}] 🔄 Groq Vision rate-limited/failed ({resp.status_code}), seamlessly falling back to Gemini Vision...")
            gemini_res = call_gemini_api(prompt, images=images, temperature=temperature, max_tokens=max_tokens, timeout=30, tag=f"{tag}-GeminiVision")
            if gemini_res.get("success"):
                return gemini_res

        # If Text failed and model is not fallback model, retry with Groq text fallback
        if not images and selected_model != GROQ_FALLBACK_MODEL:
            print(f"[AgriShield][{tag}] Retrying with Groq fallback: {GROQ_FALLBACK_MODEL}")
            payload["model"] = GROQ_FALLBACK_MODEL
            resp2 = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=timeout)
            if resp2.status_code == 200:
                raw2 = resp2.json()["choices"][0]["message"]["content"]
                print(f"[AgriShield][{tag}] Fallback OK ({len(raw2)} chars)")
                return {"raw": raw2, "success": True, "model": GROQ_FALLBACK_MODEL, "provider": "groq"}

        # If Groq text failed completely, fall back to Gemini Text
        if not images and GEMINI_API_KEY:
            print(f"[AgriShield][{tag}] 🔄 Groq Text failed, falling back to Gemini Text...")
            gemini_res = call_gemini_api(prompt, images=None, temperature=temperature, max_tokens=max_tokens, timeout=30, tag=f"{tag}-GeminiText")
            if gemini_res.get("success"):
                return gemini_res

        return {"error": f"Groq API Error: {resp.status_code} - {error_text}", "success": False}

    except requests.exceptions.Timeout:
        print(f"[AgriShield][{tag}] Timeout after {timeout}s on Groq")
        if GEMINI_API_KEY:
            print(f"[AgriShield][{tag}] 🔄 Groq timed out, falling back to Gemini...")
            gemini_res = call_gemini_api(prompt, images=images, temperature=temperature, max_tokens=max_tokens, timeout=30, tag=f"{tag}-GeminiFallback")
            if gemini_res.get("success"):
                return gemini_res
        return {"error": "API request timed out", "success": False}

    except Exception as e:
        print(f"[AgriShield][{tag}] Groq Exception: {e}")
        if GEMINI_API_KEY:
            print(f"[AgriShield][{tag}] 🔄 Groq exception, falling back to Gemini...")
            gemini_res = call_gemini_api(prompt, images=images, temperature=temperature, max_tokens=max_tokens, timeout=30, tag=f"{tag}-GeminiFallback")
            if gemini_res.get("success"):
                return gemini_res
        return {"error": str(e), "success": False}


def _repair_truncated_json_object(text: str) -> dict | None:
    """Try to repair a truncated JSON object by searching backwards from truncation point."""
    start = text.find('{')
    if start == -1:
        return None
    sub = text[start:]
    for closer in ['}', '"}', 'null}', '"]}', ']}']:
        for i in range(len(sub) - 1, max(0, len(sub) - 400), -1):
            cand = sub[:i].rstrip()
            if cand.endswith(',') or cand.endswith(':') or cand.endswith('"'):
                cand = cand.rstrip(',:"')
            try:
                res = json.loads(cand + closer)
                if isinstance(res, dict) and len(res) > 2:
                    print(f"[AgriShield] JSON object repaired successfully ({len(res)} keys)")
                    return res
            except Exception:
                continue
    return None


# ── Convenience: call + parse JSON object ────────────────────
def call_groq_json_object(prompt, images=None, **kwargs) -> dict:
    """Call AI and parse response as JSON object {...}."""
    result = call_groq(prompt, images, **kwargs)
    if not result["success"]:
        return {"error": result["error"]}
    try:
        text = parse_json_response(result["raw"])
        text = extract_json_object(text)
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[AgriShield] JSON parse error: {e}, attempting repair...")
        repaired = _repair_truncated_json_object(text)
        if repaired is not None:
            return repaired
        return {"error": "Failed to parse AI response"}


def _repair_truncated_json_array(text: str) -> list | None:
    """Try to repair a truncated JSON array by finding the last complete object."""
    # Find the opening bracket
    start = text.find('[')
    if start == -1:
        return None
    # Find the last complete object closing brace
    last_brace = text.rfind('}')
    if last_brace == -1:
        return None
    # Take everything up to and including the last complete }, then close the array
    repaired = text[start:last_brace + 1].rstrip().rstrip(',') + ']'
    try:
        result = json.loads(repaired)
        print(f"[AgriShield] JSON repaired successfully ({len(result)} items)")
        return result
    except json.JSONDecodeError:
        return None


def call_groq_json_array(prompt, images=None, **kwargs) -> list | dict:
    """Call AI and parse response as JSON array [...]."""
    result = call_groq(prompt, images, **kwargs)
    if not result["success"]:
        return {"error": result["error"]}
    try:
        text = parse_json_response(result["raw"])
        text = extract_json_array(text)
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[AgriShield] JSON parse error: {e}, attempting repair...")
        # Try to repair truncated JSON array
        repaired = _repair_truncated_json_array(text)
        if repaired is not None:
            return repaired
        return {"error": "Failed to parse AI response"}
