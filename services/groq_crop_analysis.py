"""
Crop Analysis Service
=====================
Uses groq_client for all API calls.
"""

import re
import json
from datetime import datetime, timedelta
from services.groq_client import call_groq, parse_json_response, extract_json_object


# Crop lifecycle database for harvest prediction
CROP_LIFECYCLE = {
    "wheat": {"total_days": 120, "hindi": "गेहूं"},
    "rice": {"total_days": 150, "hindi": "चावल"},
    "maize": {"total_days": 100, "hindi": "मक्का"},
    "corn": {"total_days": 100, "hindi": "मक्का"},
    "soybean": {"total_days": 110, "hindi": "सोयाबीन"},
    "cotton": {"total_days": 180, "hindi": "कपास"},
    "sugarcane": {"total_days": 365, "hindi": "गन्ना"},
    "mustard": {"total_days": 130, "hindi": "सरसों"},
    "chickpea": {"total_days": 110, "hindi": "चना"},
    "potato": {"total_days": 90, "hindi": "आलू"},
    "tomato": {"total_days": 75, "hindi": "टमाटर"},
    "onion": {"total_days": 130, "hindi": "प्याज"},
    "groundnut": {"total_days": 120, "hindi": "मूंगफली"},
    "millet": {"total_days": 80, "hindi": "बाजरा"},
    "sorghum": {"total_days": 110, "hindi": "ज्वार"},
    "lentil": {"total_days": 100, "hindi": "मसूर"},
    "pigeon pea": {"total_days": 160, "hindi": "अरहर"},
    "barley": {"total_days": 110, "hindi": "जौ"},
    "sesame": {"total_days": 95, "hindi": "तिल"},
    "sunflower": {"total_days": 100, "hindi": "सूरजमुखी"},
}

ANALYSIS_PROMPT = """You are AgriShield AI — an expert agricultural scientist and crop doctor. 
Analyze this crop image very carefully and provide a COMPLETE analysis in STRICT JSON format.

You MUST respond with ONLY a valid JSON object (no markdown, no explanation, no extra text).

Required JSON structure:
{
  "crop_name": "exact crop name (e.g., Wheat, Rice, Maize, Tomato, Cotton)",
  "crop_name_hindi": "crop name in Hindi",
  "estimated_age_days": "age range in days (e.g., 30-35)",
  "growth_stage": "one of: Germination, Seedling, Vegetative, Flowering, Maturity",
  "health_score": 85,
  "health_status": "Healthy / Moderate Stress / Severe Stress / Critical",
  "pros": "2-3 positive observations about the crop (leaf color, growth pattern, etc.)",
  "cons": "2-3 issues or concerns observed (yellowing, spots, wilting, etc.) or 'No significant issues' if healthy",
  "nutrient_requirements": "what nutrients the crop needs at this stage (NPK ratio, micronutrients)",
  "recommended_products": "specific fertilizers and products to use (e.g., DAP, Urea, Potash with dosage)",
  "disease_detected": "disease name if any, or 'No disease detected'",
  "disease_cause": "what causes this disease (pathogen, conditions)",
  "disease_prevention": "how to prevent this disease",
  "disease_treatment": "specific treatment with product names and dosage",
  "irrigation_advice": "how much and how often to water at this growth stage",
  "fertilizer_recommendation": "what fertilizer to apply now with exact dosage per acre",
  "growth_tips": "3-4 tips to maximize growth at this stage",
  "harvest_readiness": "how to know when crop is ready for harvest",
  "pest_detected": "pest name if any visible (e.g., Aphids, Bollworm, Stem Borer, Whitefly, Jassids, Thrips, Mealybug), or 'No pest detected'",
  "pest_type": "type of pest (e.g., Sucking pest, Boring pest, Chewing pest, Defoliator) or 'N/A'",
  "pest_removal_organic": "organic/natural methods to remove this pest — neem oil spray, bio-agents like Trichogramma, pheromone traps, sticky traps, etc. with dosage. Or 'N/A' if no pest",
  "pest_removal_chemical": "chemical pesticide names with exact dosage per acre — e.g., Imidacloprid 17.8 SL @ 100ml/acre, Chlorpyrifos 20 EC @ 500ml/acre. Or 'N/A' if no pest",
  "confidence": 88
}

IMPORTANT RULES:
1. Identify the EXACT crop type from the image
2. Give REALISTIC age estimation based on visual maturity
3. Health score should be 0-100 based on actual visible condition
4. Confidence should be 0-100 based on image clarity
5. Be specific with product names and dosages
6. If you cannot identify the crop clearly, still provide your best analysis
7. For pest detection, look for visible insect damage, holes in leaves, curling, webbing, etc.
8. RESPOND WITH ONLY THE JSON — no other text before or after"""


def calculate_harvest_prediction(crop_name, estimated_age_str):
    """Calculate harvest prediction from crop lifecycle database."""
    crop_key = crop_name.lower().strip()

    # Find matching crop in database
    lifecycle_info = None
    for key, val in CROP_LIFECYCLE.items():
        if key in crop_key or crop_key in key:
            lifecycle_info = val
            break

    if not lifecycle_info:
        lifecycle_info = {"total_days": 120, "hindi": crop_name}

    total_days = lifecycle_info["total_days"]

    # Parse age range (e.g., "30-35" -> average 32)
    try:
        age_parts = re.findall(r'\d+', str(estimated_age_str))
        if len(age_parts) >= 2:
            avg_age = (int(age_parts[0]) + int(age_parts[1])) // 2
        elif len(age_parts) == 1:
            avg_age = int(age_parts[0])
        else:
            avg_age = total_days // 3
    except:
        avg_age = total_days // 3

    days_remaining = max(0, total_days - avg_age)
    harvest_date = (datetime.now() + timedelta(days=days_remaining)).strftime("%d %B %Y")

    return {
        "total_lifecycle_days": total_days,
        "estimated_current_age": avg_age,
        "days_to_harvest": days_remaining,
        "expected_harvest_date": harvest_date,
    }


def analyze_crop_with_groq(image_path):
    """
    Send crop image to Groq Vision for comprehensive analysis.
    Uses central groq_client for the API call.
    """
    result = call_groq(
        ANALYSIS_PROMPT,
        images=[image_path],
        temperature=0.3,
        max_tokens=2048,
        timeout=60,
        tag="CropAnalysis",
    )

    if not result["success"]:
        return {"error": result["error"]}

    raw_text = result["raw"]

    try:
        json_text = parse_json_response(raw_text)
        json_text = extract_json_object(json_text)
        analysis = json.loads(json_text)

        # Calculate harvest prediction
        harvest_info = calculate_harvest_prediction(
            analysis.get("crop_name", "Unknown"),
            analysis.get("estimated_age_days", "30-40")
        )

        # Build final structured response
        final_result = {
            "crop_name": analysis.get("crop_name", "Unknown Crop"),
            "crop_name_hindi": analysis.get("crop_name_hindi", ""),
            "age": analysis.get("estimated_age_days", "N/A"),
            "stage": analysis.get("growth_stage", "N/A"),
            "health_score": analysis.get("health_score", 0),
            "health_status": analysis.get("health_status", "N/A"),
            "pros": analysis.get("pros", "No data"),
            "cons": analysis.get("cons", "No data"),
            "requirements": analysis.get("nutrient_requirements", "N/A"),
            "growth_products": analysis.get("recommended_products", "N/A"),
            "disease": analysis.get("disease_detected", "No disease detected"),
            "disease_cause": analysis.get("disease_cause", "N/A"),
            "disease_prevention": analysis.get("disease_prevention", "N/A"),
            "treatment": analysis.get("disease_treatment", "No treatment needed"),
            "irrigation_advice": analysis.get("irrigation_advice", "N/A"),
            "fertilizer_recommendation": analysis.get("fertilizer_recommendation", "N/A"),
            "growth_tips": analysis.get("growth_tips", "N/A"),
            "harvest_readiness": analysis.get("harvest_readiness", "N/A"),
            "harvest_days": harvest_info["days_to_harvest"],
            "harvest_date": harvest_info["expected_harvest_date"],
            "total_lifecycle": harvest_info["total_lifecycle_days"],
            "pest_detected": analysis.get("pest_detected", "No pest detected"),
            "pest_type": analysis.get("pest_type", "N/A"),
            "pest_removal_organic": analysis.get("pest_removal_organic", "N/A"),
            "pest_removal_chemical": analysis.get("pest_removal_chemical", "N/A"),
            "confidence": analysis.get("confidence", 0),
        }

        return final_result

    except json.JSONDecodeError as e:
        print(f"[AgriShield] JSON Parse Error: {e}")
        return {"error": "Failed to parse AI response", "raw_response": raw_text[:500]}
    except Exception as e:
        print(f"[AgriShield] Error: {e}")
        return {"error": str(e)}
