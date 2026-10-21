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
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ── Model Constants (Active on Groq LPU) ──────────────────────
# High-intelligence text model (OpenAI OSS 120B, 131K ctx)
GROQ_TEXT_MODEL     = "openai/gpt-oss-120b"
# Fastest Multimodal Vision model (Qwen 3.8 27B — 0.9s response, 131K ctx)
GROQ_VISION_MODEL   = "qwen/qwen3.8-27b"
# Ultra-fast lightweight fallback model (OpenAI OSS 20B)
GROQ_FALLBACK_MODEL = "openai/gpt-oss-20b"


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


# ── Core API Call ────────────────────────────────────────────
def call_groq(
    prompt: str,
    images: list = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
    timeout: int = 60,
    tag: str = "Groq",
) -> dict:
    """
    Call AI API via Groq.

    Args:
        prompt:      Text prompt to send
        images:      List of image file paths (optional, for vision)
        temperature: Sampling temperature
        max_tokens:  Max response tokens
        timeout:     Request timeout in seconds
        tag:         Log tag for identification

    Returns:
        dict with either:
          {"raw": "...", "success": True}   on success
          {"error": "...", "success": False} on failure
    """
    if not GROQ_API_KEY:
        return {"error": "No API keys configured", "success": False}

    # Build message content
    if images:
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
        "max_tokens": max_tokens,
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        print(f"[AgriShield][{tag}] Calling Groq ({selected_model})...")
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=timeout)

        if resp.status_code != 200:
            error_text = resp.text[:300]
            print(f"[AgriShield][{tag}] Groq Error {resp.status_code}: {error_text}")

            # Auto-fallback to backup model if primary fails
            if not images and selected_model != GROQ_FALLBACK_MODEL:
                print(f"[AgriShield][{tag}] Retrying with fallback: {GROQ_FALLBACK_MODEL}")
                payload["model"] = GROQ_FALLBACK_MODEL
                resp2 = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=timeout)
                if resp2.status_code == 200:
                    raw2 = resp2.json()["choices"][0]["message"]["content"]
                    print(f"[AgriShield][{tag}] Fallback OK ({len(raw2)} chars)")
                    return {"raw": raw2, "success": True, "model": GROQ_FALLBACK_MODEL}

            return {"error": f"Groq API Error: {resp.status_code} - {error_text}", "success": False}

        raw = resp.json()["choices"][0]["message"]["content"]
        print(f"[AgriShield][{tag}] Response received ({len(raw)} chars) from {selected_model}")
        return {"raw": raw, "success": True, "model": selected_model}

    except requests.exceptions.Timeout:
        print(f"[AgriShield][{tag}] Timeout after {timeout}s")
        return {"error": "API request timed out", "success": False}
    except Exception as e:
        print(f"[AgriShield][{tag}] Error: {e}")
        return {"error": str(e), "success": False}


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
        print(f"[AgriShield] JSON parse error: {e}")
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
