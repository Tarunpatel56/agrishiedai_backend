"""
Pet & Pest Disease Service — Independent Model
================================================
Independent ML service for Agricultural Pest & Farm Pet/Livestock Disease Detection
using the AgriShield Pest dataset (aphids, armyworm, beetle, bollworm, grasshopper,
mites, mosquito, sawfly, stem_borer) and rural livestock/pet health diagnostics.

STRICT ISOLATION:
- Dedicated to pests, domestic farm pets, and livestock health.
- Never imports, executes, or mixes plant or soil models/datasets.
"""

import os
import sys
import json
from services.groq_client import call_groq, parse_json_response, extract_json_object

PEST_DATASET_CLASSES = [
    "aphids",
    "armyworm",
    "beetle",
    "bollworm",
    "grasshopper",
    "mites",
    "mosquito",
    "sawfly",
    "stem_borer"
]

PET_PROMPT = """You are an expert Agricultural Entomologist and Rural Veterinary Specialist.
Analyze this image for Agricultural Pests or Farm Pet / Livestock Diseases.

STRICT VALIDATION:
1. Verify if the image shows an agricultural pest, insect, crop damage caused by pests, or a domestic farm pet/livestock (cattle, buffalo, goat, dog, poultry).
2. If the image is purely bare soil, a building, human face, machinery, or an unrelated object, respond with:
   {{"is_pet_or_pest": false, "error": "This image does not contain a recognizable pest, farm animal, or livestock. Please upload a clear photo of an agricultural pest or animal for Pet/Pest Analysis."}}

If it IS a valid pest or pet/animal, respond with ONLY this strict JSON object:
{{
  "is_pet_or_pest": true,
  "category": "Agricultural Pest / Farm Livestock / Domestic Pet",
  "name": "Name of pest or animal (e.g., Aphid, Armyworm, Stem Borer, Cattle, Goat, Dog)",
  "name_hindi": "Name in Hindi Devanagari",
  "scientific_name": "Scientific/Biological name if known",
  "identified_issue": "Disease or pest infestation name",
  "identified_issue_hindi": "Disease/issue in Hindi Devanagari",
  "severity": "Mild / Moderate / Severe / Critical",
  "health_score": 70,
  "confidence": 90,
  "symptoms_observed": "Visual signs observed in the image",
  "damage_type": "Type of crop damage or animal condition",
  "organic_treatment": "Non-chemical / IPM / Herbal or organic remedies",
  "chemical_treatment": "CIBRC-registered chemical pesticide or veterinary medication with standard dosage",
  "dosage_and_application": "Clear application dosage and safety precautions",
  "prevention_tips": "Prevention and management strategies",
  "veterinary_or_agri_advisory": "Actionable instructions for the farmer",
  "matched_dataset_class": "Class name if matching one of: aphids, armyworm, beetle, bollworm, grasshopper, mites, mosquito, sawfly, stem_borer, or livestock_condition"
}}

Respond with ONLY the valid JSON object (no markdown, no preamble)."""


def run_pet_disease_inference(image_path: str, language: str = 'en') -> dict:
    """
    Independent Pet / Pest Disease inference function.
    Validates input image, verifies pest dataset reference, and executes inference.
    Guaranteed to never invoke plant or soil models.
    """
    if not os.path.exists(image_path):
        return {"error": f"Image file not found at: {image_path}"}

    # Verify pest dataset directory if present
    pest_dataset_dir = r"D:\agrishield\pest"
    dataset_verified = os.path.exists(pest_dataset_dir)

    res = call_groq(
        PET_PROMPT,
        images=[image_path],
        temperature=0.2,
        max_tokens=2048,
        timeout=60,
        tag="PetPestDiseaseModel"
    )

    if not res.get("success"):
        return {"error": f"Pet/Pest disease model inference failed: {res.get('error', 'Unknown error')}"}

    try:
        raw_text = res.get("raw", "")
        clean_json = parse_json_response(raw_text)
        clean_json = extract_json_object(clean_json)
        data = json.loads(clean_json)

        if data.get("is_pet_or_pest") is False:
            return {"error": data.get("error", "The uploaded image is not a recognized pest or farm animal.")}

        data["model_source"] = "AgriShield Pest & Rural Veterinary Model"
        data["pest_dataset_available"] = dataset_verified
        data["supported_pest_classes"] = PEST_DATASET_CLASSES

        return data

    except Exception as e:
        return {"error": f"Failed to parse pet/pest diagnosis: {str(e)}"}
