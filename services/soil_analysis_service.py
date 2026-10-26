"""
Soil Analysis Service — Independent Soil Model
================================================
Independent ML service for Agricultural Soil Health & Soil Type Classification.

STRICT ISOLATION:
- Dedicated to soil physics, chemistry estimation, and soil classification.
- Never imports, executes, or mixes plant or pet models/datasets.
"""

import os
import sys
import json
from services.groq_client import call_groq, parse_json_response, extract_json_object

SOIL_TYPES = [
    "Clay", "Sandy", "Loamy", "Silty", "Peaty", "Chalky",
    "Laterite", "Black Cotton Soil", "Red Soil", "Alluvial Soil"
]

SOIL_INDEPENDENT_PROMPT = """You are an expert Agricultural Pedologist (Soil Scientist).
Analyze this image specifically for Soil Classification and Physical Health.

STRICT VALIDATION:
1. First verify if the image actually shows SOIL, FARMLAND EARTH, GROUND, or TOPSOIL.
2. If the image is a person, animal/pet, crop leaf/plant foliage without visible soil, building, food, vehicle, or document, you MUST respond with:
   {{"is_soil": false, "error": "This is not a soil image. Please upload a clear photograph of your field or garden soil for Soil Analysis."}}

If it IS a soil image, respond with ONLY this strict JSON object:
{{
  "is_soil": true,
  "soil_type": "Clay / Sandy / Loamy / Silty / Peaty / Chalky / Laterite / Black Cotton / Red / Alluvial",
  "soil_type_hindi": "Soil type name in Hindi Devanagari",
  "ph_level": "Estimated pH range (e.g. Slightly Acidic: 6.0 - 6.5, Neutral: 6.5 - 7.5, Alkaline: 7.5 - 8.5)",
  "soil_texture": "Fine-grained / Medium-grained / Coarse / Gritty",
  "soil_color": "Observed visual color (Dark Brown, Reddish, Black, Sandy Grey)",
  "soil_health": "Good / Fair / Degraded",
  "health_score": 78,
  "confidence": 88,
  "moisture_level": "Dry / Optimum Moist / Waterlogged",
  "organic_matter": "Low / Medium / High",
  "nitrogen_level": "Low / Medium / High",
  "phosphorus_level": "Low / Medium / High",
  "potassium_level": "Low / Medium / High",
  "aeration_and_drainage": "Assessment of water percolation and root aeration",
  "recommended_crops": ["3-5 crops best naturally suited to this soil type"],
  "advisory": "2-3 practical lines of soil conditioning guidance in English",
  "advisory_hindi": "2-3 practical lines of soil conditioning guidance in Hindi Devanagari",
  "laboratory_recommendation": "Always confirm with a Government Soil Health Card lab test for exact chemical nutrients."
}}

Respond with ONLY the valid JSON object (no markdown, no preamble)."""


def run_soil_analysis_inference(image_path: str, language: str = 'en') -> dict:
    """
    Independent Soil Analysis inference function.
    Validates soil image, performs soil classification, and returns structured soil report.
    Guaranteed to never invoke plant or pet models.
    """
    if not os.path.exists(image_path):
        return {"error": f"Soil image file not found at: {image_path}"}

    res = call_groq(
        SOIL_INDEPENDENT_PROMPT,
        images=[image_path],
        temperature=0.2,
        max_tokens=2048,
        timeout=60,
        tag="SoilAnalysisModel"
    )

    if not res.get("success"):
        return {"error": f"Soil analysis model inference failed: {res.get('error', 'Unknown error')}"}

    try:
        raw_text = res.get("raw", "")
        clean_json = parse_json_response(raw_text)
        clean_json = extract_json_object(clean_json)
        data = json.loads(clean_json)

        if data.get("is_soil") is False:
            return {"error": data.get("error", "The uploaded image does not appear to be soil.")}

        data["model_source"] = "AgriShield Pedological Soil Classification Model"
        data["supported_soil_types"] = SOIL_TYPES

        return data

    except Exception as e:
        return {"error": f"Failed to parse soil analysis report: {str(e)}"}
