"""
AgriShield AI — Advanced Agriculture Services
================================================
Recovery Advisor, ROI Calculator, Market Predictor, AgriBot Chatbot.
All powered by AI via groq_client (Groq + Gemini fallback).
"""

import json
from services.groq_client import (
    call_groq, parse_json_response, extract_json_object, extract_json_array,
    call_groq_json_object, call_groq_json_array,
    GROQ_API_KEY, GROQ_TEXT_MODEL, GROQ_FALLBACK_MODEL,
)


# ══════════════════════════════════════════════════════════════
# 1. RECOVERY ADVISOR — AI Business Pivot when damage > 50%
# ══════════════════════════════════════════════════════════════

RECOVERY_PROMPT = """You are AgriShield AI Recovery Advisor — an expert in agricultural crisis management and alternative farming.

A farmer's crop has been severely damaged. Analyze and provide a SMART RECOVERY PLAN.

Crop Data:
- Crop: {crop_name}
- Health Score: {health_score}/100
- Damage: {damage_percent}%
- Disease: {disease}

You MUST respond with ONLY a valid JSON object (no markdown, no explanation):
{{
  "damage_level": "Severe / Critical / Moderate",
  "pivot_title": "A short title for the recovery plan (e.g., 'Convert to Organic Vermicompost Unit')",
  "pivot_description": "2-3 lines explaining why this pivot makes sense for the farmer",
  "alternative_options": [
    {{
      "name": "Alternative business 1 (e.g., Poultry Farm, Mushroom Cultivation, Vermicompost, Bee Keeping)",
      "investment_required": 25000,
      "monthly_income": 15000,
      "setup_days": 30,
      "description": "1-2 lines about this option"
    }},
    {{
      "name": "Alternative business 2",
      "investment_required": 15000,
      "monthly_income": 10000,
      "setup_days": 15,
      "description": "1-2 lines"
    }},
    {{
      "name": "Alternative business 3",
      "investment_required": 10000,
      "monthly_income": 8000,
      "setup_days": 20,
      "description": "1-2 lines"
    }}
  ],
  "loss_without_pivot": 45000,
  "projected_profit_with_pivot": 35000,
  "recovery_timeline_days": 60,
  "immediate_steps": ["Step 1", "Step 2", "Step 3"],
  "government_schemes": ["Relevant scheme 1 for this situation", "Scheme 2"]
}}

RULES:
1. Give REALISTIC Indian farming alternatives based on the damage level
2. All amounts in Indian Rupees (INR)
3. Consider the season and crop type for recommendations
4. Include practical government schemes available in India
"""


def get_recovery_advice(scan_data: dict) -> dict:
    """Generate AI-powered recovery plan for damaged crops."""
    prompt = RECOVERY_PROMPT.format(
        crop_name=scan_data.get("crop_name", "Unknown"),
        health_score=scan_data.get("health_score", 0),
        damage_percent=scan_data.get("damage_percent", 0),
        disease=scan_data.get("disease", "Unknown"),
    )

    result = call_groq_json_object(prompt, temperature=0.4, max_tokens=2048, tag="RecoveryAdvisor")
    if "error" in result:
        return {"error": result["error"]}
    return result


# ══════════════════════════════════════════════════════════════
# 2. ROI CALCULATOR — Smart Investment Planner
# ══════════════════════════════════════════════════════════════

ROI_PROMPT = """You are AgriShield AI Investment Advisor — an expert in farm economics and agricultural ROI calculation.

Calculate a SMART ROI breakdown for a farmer's investment.

Input:
- Investment Amount: ₹{investment_amount}
- Land Size: {land_size} acres
- Current/Primary Crop: {crop_name}

You MUST respond with ONLY a valid JSON object:
{{
  "total_investment": {investment_amount},
  "land_size_acres": {land_size},
  "roi_breakdown": [
    {{
      "category": "Primary Crop ({crop_name})",
      "allocation_percent": 40,
      "investment_amount": 20000,
      "expected_return": 35000,
      "roi_percent": 75,
      "timeline_months": 4
    }},
    {{
      "category": "Poultry Farming",
      "allocation_percent": 25,
      "investment_amount": 12500,
      "expected_return": 22000,
      "roi_percent": 76,
      "timeline_months": 3
    }},
    {{
      "category": "Mushroom Cultivation",
      "allocation_percent": 20,
      "investment_amount": 10000,
      "expected_return": 18000,
      "roi_percent": 80,
      "timeline_months": 2
    }},
    {{
      "category": "Remaining/Emergency Fund",
      "allocation_percent": 15,
      "investment_amount": 7500,
      "expected_return": 7500,
      "roi_percent": 0,
      "timeline_months": 0
    }}
  ],
  "total_expected_return": 82500,
  "total_roi_percent": 65,
  "payback_period_months": 6,
  "risk_level": "Low / Medium / High",
  "tips": ["Tip 1 for maximizing returns", "Tip 2", "Tip 3"]
}}

RULES:
1. All amounts in Indian Rupees (INR)
2. ROI calculations should be REALISTIC for Indian farming
3. allocation_percent of all categories MUST add up to 100
4. Consider land size for scaling recommendations
5. Give at least 4 diversification categories
"""


def calculate_roi(investment_amount: int, land_size: float, crop_name: str) -> dict:
    """Calculate ROI distribution for farmer investment."""
    prompt = ROI_PROMPT.format(
        investment_amount=investment_amount,
        land_size=land_size,
        crop_name=crop_name if crop_name else "General",
    )

    result = call_groq_json_object(prompt, temperature=0.3, max_tokens=2048, tag="ROICalculator")
    if "error" in result:
        return {"error": result["error"]}
    return result


# ══════════════════════════════════════════════════════════════
# 3. MARKET DEMAND PREDICTOR — High-Value Crop Intelligence
# ══════════════════════════════════════════════════════════════

MARKET_PREDICTION_PROMPT = """You are AgriShield AI Market Intelligence — an expert in agricultural market trends and demand forecasting for Indian markets.

Predict the TOP 10 high-demand, high-value crops for the NEXT QUARTER in India.

You MUST respond with ONLY a valid JSON array:
[
  {{
    "crop_name": "Dragon Fruit",
    "crop_name_hindi": "ड्रैगन फ्रूट",
    "category": "Exotic Fruit / Spice / Medicinal Herb / Vegetable / Grain",
    "demand_score": 9.5,
    "current_price_per_kg": 250,
    "predicted_price_per_kg": 320,
    "price_growth_percent": 28,
    "quarterly_trend": [200, 230, 260, 320],
    "why_trending": "1-2 lines why this crop is in high demand",
    "best_states": ["Rajasthan", "Maharashtra"],
    "investment_per_acre": 50000,
    "profit_per_acre": 120000
  }}
]

RULES:
1. Include a MIX of: exotic fruits, spices, medicinal herbs, and high-value vegetables
2. demand_score is out of 10 (realistic — not all 9+)
3. All prices in Indian Rupees (INR) per kg
4. quarterly_trend is an array of 4 price points (last 3 months + next quarter prediction)
5. Include at least 8-10 crops
6. Focus on crops with REAL market demand in India
7. Include some unconventional but profitable crops (Moringa, Stevia, Lavender etc.)
"""


def get_market_predictions() -> dict:
    """Get AI-predicted high-value crops with demand scores."""
    result = call_groq_json_array(
        MARKET_PREDICTION_PROMPT,
        temperature=0.5,
        max_tokens=4096,
        tag="MarketPredictor",
    )
    if isinstance(result, dict) and "error" in result:
        return {"error": result["error"]}
    return {"predictions": result}


# ══════════════════════════════════════════════════════════════
# 4. AGRIBOT CHATBOT — Agriculture-Only AI Assistant
# ══════════════════════════════════════════════════════════════

AGRIBOT_SYSTEM_PROMPT = """You are AgriBot — AgriShield AI's expert agriculture assistant chatbot.

STRICT RULES:
1. You ONLY answer questions related to AGRICULTURE, FARMING, CROPS, SOIL, WEATHER, MARKET PRICES, DISEASES, PESTS, FERTILIZERS, IRRIGATION, GOVERNMENT SCHEMES FOR FARMERS, ANIMAL HUSBANDRY, and related topics.
2. If someone asks a NON-AGRICULTURE question, politely refuse and say "Main sirf kheti-baadi se jude sawaalon ka jawab de sakta hoon." (if Hindi) or "I can only answer agriculture-related questions." (if English).
3. You are an EXPERT — give detailed, practical, actionable advice.
4. Include specific product names, dosages, and timelines when relevant.
5. If asked about diseases, give: cause, symptoms, organic solution, and chemical solution.
6. If asked about market prices, give approximate current Indian market rates.
7. RESPOND IN {language} LANGUAGE ONLY.
8. Be friendly and use farmer-friendly language (not too technical).
9. If the farmer describes symptoms, diagnose the likely issue and provide solution.
10. For Hindi responses, use Devanagari script mixed with common farming terms.

You are chatting with an Indian farmer. Help them with all agriculture needs."""


def agri_chat(message: str, language: str = "hi", history: list = None) -> dict:
    """
    Agriculture-only chatbot powered by AI via Groq.
    language: 'hi' for Hindi, 'en' for English
    history: list of {"role": "user"/"assistant", "content": "..."} messages
    """
    lang_full = "HINDI (Devanagari script)" if language == "hi" else "ENGLISH"
    system_prompt = AGRIBOT_SYSTEM_PROMPT.format(language=lang_full)

    # Build conversation with history
    messages = [{"role": "system", "content": system_prompt}]

    if history:
        for h in history[-10:]:  # Keep last 10 messages for context
            messages.append({
                "role": h.get("role", "user"),
                "content": h.get("content", "")
            })

    messages.append({"role": "user", "content": message})

    # Import current state from groq_client
    import services.groq_client as gc

    if not gc.GROQ_API_KEY:
        return {"error": "GROQ_API_KEY is not configured"}

    # Try with primary model, fallback if it fails
    import services.groq_client as gc

    import requests

    def _try_chat(model_id):
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": 0.6,
            "max_tokens": 1024,
        }
        headers = {
            "Authorization": f"Bearer {gc.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        return resp

    try:
        print(f"[AgriShield][AgriBot] Calling Groq ({gc.GROQ_TEXT_MODEL})...")
        resp = _try_chat(gc.GROQ_TEXT_MODEL)

        # Auto-fallback
        if resp.status_code != 200:
            print(f"[AgriBot] Primary model error {resp.status_code}, trying fallback...")
            resp = _try_chat(gc.GROQ_FALLBACK_MODEL)

        if resp.status_code != 200:
            error_text = resp.text[:300]
            print(f"[AgriBot] Error {resp.status_code}: {error_text}")
            return {"error": f"API Error: {resp.status_code} - {error_text}"}

        reply = resp.json()["choices"][0]["message"]["content"]
        used_model = resp.json()["model"]
        return {
            "reply": reply,
            "language": language,
            "model": used_model,
        }

    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except Exception as e:
        print(f"[AgriBot] Error: {e}")
        return {"error": str(e)}
