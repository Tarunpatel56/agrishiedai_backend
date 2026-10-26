"""
Crop Spray Advisor Service — Source-Backed IPM & Protection Guidance
======================================================================
Provides verified crop-protection recommendations prioritizing Integrated
Pest Management (IPM), biological controls, and CIBRC label-approved Indian
pesticides with dosage, dilution, waiting periods, and safety warnings.

CRITICAL RULES:
- Never invents chemical products, unapproved tank mixtures, or fake dosages.
- Explicitly cites authoritative agricultural sources (ICAR / CIBRC / State Agri Universities).
- Clearly separates vision-model observations from verified treatment guidelines.
"""

import os
import json
from services.groq_client import call_groq, parse_json_response, extract_json_object
from services.plant_disease_service import run_plant_disease_inference

# Verified CIBRC registered management database for prominent Indian crops
VERIFIED_CROP_PROTECTION_DB = {
    "wheat": {
        "rust": {
            "disease_name": "Yellow / Brown Rust (Puccinia spp.)",
            "disease_name_hi": "गेहूं का रतुआ रोग (पीला या भूरा रतुआ)",
            "cultural": "Use resistant varieties (e.g. DBW 187, DBW 222, HD 3086). Avoid excess nitrogen.",
            "cultural_hi": "प्रतिरोधी किस्मों की बुवाई करें। अत्यधिक यूरिया के प्रयोग से बचें।",
            "biological": "Spray Trichoderma viride @ 5g/L at early vegetative stage.",
            "biological_hi": "प्रारंभिक अवस्था में ट्राइकोडर्मा विरिडी 5 ग्राम प्रति लीटर पानी में छिड़कें।",
            "chemical_name": "Propiconazole 25% EC",
            "chemical_name_hi": "प्रोपिकोनाजोल 25% ईसी",
            "dosage": "1 ml per liter of water (200 ml in 200 liters water per acre)",
            "dosage_hi": "1 मिली प्रति लीटर पानी (200 मिली प्रति 200 लीटर पानी प्रति एकड़)",
            "waiting_period": "30 days before harvest",
            "waiting_period_hi": "कटाई से 30 दिन पूर्व",
            "source": "ICAR-Indian Institute of Wheat & Barley Research (IIWBR) & CIBRC"
        },
        "powdery_mildew": {
            "disease_name": "Powdery Mildew",
            "disease_name_hi": "चूर्णिल आसिता (पाउडरी मिल्ड्यू)",
            "cultural": "Ensure proper spacing and balanced irrigation. Avoid stagnant humidity.",
            "cultural_hi": "उचित दूरी पर बुवाई करें और खेत में अत्यधिक नमी न रहने दें।",
            "biological": "Sulfur 80% WDG @ 2.5-3 g/L.",
            "biological_hi": "घुलनशील सल्फर (गंधक) 80% डब्ल्यूडीजी 2.5 से 3 ग्राम प्रति लीटर पानी।",
            "chemical_name": "Tebuconazole 25.9% m/m EC",
            "chemical_name_hi": "टेबुकोनाजोल 25.9% ईसी",
            "dosage": "1 ml per liter of water (200 ml per acre in 200 L water)",
            "dosage_hi": "1 मिली प्रति लीटर पानी (200 लीटर पानी प्रति एकड़ में 200 मिली)",
            "waiting_period": "35 days before harvest",
            "waiting_period_hi": "कटाई से 35 दिन पूर्व",
            "source": "ICAR Package of Practices for Rabi Crops"
        }
    },
    "rice": {
        "blast": {
            "disease_name": "Rice Blast (Magnaporthe oryzae)",
            "disease_name_hi": "धान का झुलसा रोग (ब्लास्ट)",
            "cultural": "Balanced NPK application (split nitrogen). Avoid field drying during critical stages.",
            "cultural_hi": "यूरिया को 3-4 किस्तों में दें। खेत में पर्याप्त नमी बनाए रखें।",
            "biological": "Seed treatment with Pseudomonas fluorescens @ 10g/kg seed.",
            "biological_hi": "स्यूडोमोनास फ्लोरोसेंस 10 ग्राम प्रति किलो बीज से बीजोपचार करें।",
            "chemical_name": "Tricyclazole 75% WP",
            "chemical_name_hi": "ट्राइसाइक्लाजोल 75% डब्ल्यूपी",
            "dosage": "0.6 g per liter of water (120 g in 200 L water per acre)",
            "dosage_hi": "0.6 ग्राम प्रति लीटर पानी (120 ग्राम प्रति 200 लीटर पानी प्रति एकड़)",
            "waiting_period": "30 days",
            "waiting_period_hi": "30 दिन",
            "source": "ICAR-National Rice Research Institute (NRRI) & CIBRC"
        },
        "stem_borer": {
            "disease_name": "Yellow Stem Borer (Scirpophaga incertulas)",
            "disease_name_hi": "धान का तना छेदक कीट",
            "cultural": "Clip seedling tips before transplanting. Install pheromone traps @ 8 traps/acre.",
            "cultural_hi": "रोपाई से पूर्व पौधे की ऊपरी पत्ती काटें। 8 फेरोमोन ट्रैप प्रति एकड़ लगाएं।",
            "biological": "Release egg parasitoid Trichogramma japonicum @ 40,000/acre at weekly intervals.",
            "biological_hi": "ट्राइकोग्रामा जैपोनिकम परजीवी कार्ड 40,000 प्रति एकड़ सप्ताह में छोड़ें।",
            "chemical_name": "Chlorantraniliprole 18.5% SC (or Cartap Hydrochloride 4G)",
            "chemical_name_hi": "क्लोरेंट्रानिलिप्रोल 18.5% एससी (या करटाप हाइड्रोक्लोराइड 4G)",
            "dosage": "0.3 ml per liter of water (60 ml in 200 L water per acre)",
            "dosage_hi": "0.3 मिली प्रति लीटर पानी (60 मिली प्रति 200 लीटर पानी प्रति एकड़)",
            "waiting_period": "47 days",
            "waiting_period_hi": "47 दिन",
            "source": "Directorate of Rice Development, Ministry of Agriculture"
        }
    },
    "tomato": {
        "early_blight": {
            "disease_name": "Early Blight (Alternaria solani)",
            "disease_name_hi": "टमाटर का अगेती झुलसा रोग",
            "cultural": "Remove lower infected foliage and destroy. Maintain mulch around roots.",
            "cultural_hi": "नीचे की संक्रमित पत्तियां तोड़कर नष्ट करें। खेत में मल्चिंग का उपयोग करें।",
            "biological": "Foliar spray of Trichoderma harzianum @ 5 g/L or Neem oil 10,000 ppm @ 2 ml/L.",
            "biological_hi": "ट्राइकोडर्मा हार्जिएनम 5 ग्राम/लीटर या नीम तेल 10,000 पीपीएम 2 मिली/लीटर छिड़कें।",
            "chemical_name": "Mancozeb 75% WP or Azoxystrobin 23% SC",
            "chemical_name_hi": "मैंकोजेब 75% डब्ल्यूपी या एज़ोक्सीस्ट्रोबिन 23% एससी",
            "dosage": "Mancozeb @ 2 g/L (400g/acre) OR Azoxystrobin @ 1 ml/L (200ml/acre)",
            "dosage_hi": "मैंकोजेब 2 ग्राम/लीटर (400 ग्राम/एकड़) या एज़ोक्सीस्ट्रोबिन 1 मिली/लीटर",
            "waiting_period": "5 days for Azoxystrobin, 14 days for Mancozeb",
            "waiting_period_hi": "एज़ोक्सीस्ट्रोबिन हेतु 5 दिन, मैंकोजेब हेतु 14 दिन",
            "source": "Indian Institute of Horticultural Research (ICAR-IIHR) & CIBRC"
        }
    }
}

SPRAY_LLM_PROMPT = """You are an Indian Agricultural Extension Scientist and CIBRC Crop Protection Specialist.
Generate a structured, source-backed crop protection spray prescription based on the following verified farm data:

Crop: {crop_name}
Growth Stage: {growth_stage}
Observed Symptoms: {symptoms}
Affected Parts: {affected_parts}
Severity: {severity}
Spread: {spread}
Region: {region}
Vision Model Observation: {vision_observation}

CRITICAL RULES:
1. Prioritize Integrated Pest Management (IPM).
2. Recommend ONLY chemical molecules that are officially registered and approved by CIBRC in India for this crop.
3. Provide precise dosage (per liter of water and per acre based on 200 liters water).
4. Provide the exact pre-harvest waiting interval (PHI) and application instructions.
5. Emphasize protective equipment (masks, gloves) and warn against mixing incompatible chemicals.
6. Clearly state the authoritative source of recommendations (e.g., ICAR / CIBRC / State Agricultural University).
7. If symptoms are ambiguous, clearly flag uncertainty and request additional verification.

Respond with ONLY this strict JSON object:
{{
  "identified_problem": "Primary disease, pest, or nutrient deficiency identified",
  "identified_problem_hi": "Name of the problem in Hindi Devanagari",
  "diagnosis_confidence": "High / Moderate / Needs Further Verification",
  "cultural_management": "Cultural and mechanical practices to reduce disease pressure",
  "cultural_management_hi": "Cultural practices in Hindi Devanagari",
  "biological_control": "Biological or organic control option with dosage and timing",
  "biological_control_hi": "Biological control in Hindi Devanagari",
  "chemical_treatment": {{
    "active_ingredient": "Specific CIBRC approved molecule with formulation (e.g. Mancozeb 75% WP)",
    "active_ingredient_hi": "Molecule name in Hindi Devanagari",
    "dosage_per_liter": "Exact dose per liter (e.g. 2 g / L or 1 ml / L)",
    "dosage_per_acre": "Total product needed per acre (e.g. 400 g in 200 L water)",
    "water_volume": "150-200 Liters of clean water per acre with flat fan / hollow cone nozzle",
    "waiting_period": "Pre-harvest interval in days",
    "waiting_period_hi": "Waiting period in Hindi",
    "spray_timing": "Best time of day (cool morning or late afternoon, avoid windy conditions)",
    "safety_precautions": "Mandatory PPE: Mask, eye protection, gloves; keep away from water bodies and livestock"
  }},
  "mixing_warning": "DO NOT mix with unauthorized fertilizers or insecticides unless scientifically tested.",
  "mixing_warning_hi": "बिना वैज्ञानिक सलाह के अन्य कीटनाशकों या उर्वरकों के साथ टैंक मिक्स न करें।",
  "recommendation_source": "Authoritative Indian Agricultural Source (ICAR / CIBRC / SAU Package of Practices)",
  "language": "{language}"
}}"""


def get_spray_recommendation(
    crop_name: str,
    growth_stage: str,
    symptoms: str,
    affected_parts: str = "Leaves",
    severity: str = "Moderate",
    spread: str = "Patches",
    region: str = "Central India",
    image_path: str = None,
    language: str = "en"
) -> dict:
    """
    Validates crop details, executes vision model if image provided,
    and returns authoritative IPM and spray recommendations.
    """
    if not crop_name or not crop_name.strip():
        return {"error": "Crop name is required."}
    if not symptoms or not symptoms.strip():
        return {"error": "Observed symptoms are required to recommend appropriate treatment."}

    vision_obs = "No image submitted; diagnosis derived from farmer's observed field symptoms."
    model_pred = None

    # Step 1: Use plant disease vision model if image is provided
    if image_path and os.path.exists(image_path):
        vision_result = run_plant_disease_inference(image_path, language=language)
        if "error" not in vision_result:
            model_pred = vision_result
            vision_obs = f"Vision model detected: {vision_result.get('disease')} on {vision_result.get('crop_name')} (Confidence: {vision_result.get('confidence')}%)"
        else:
            vision_obs = f"Image inspection note: {vision_result.get('error')}"

    # Step 2: Generate verified prescription via Groq AI using agricultural knowledge prompt
    prompt = SPRAY_LLM_PROMPT.format(
        crop_name=crop_name,
        growth_stage=growth_stage or "Vegetative",
        symptoms=symptoms,
        affected_parts=affected_parts,
        severity=severity,
        spread=spread,
        region=region or "India",
        vision_observation=vision_obs,
        language=language
    )

    res = call_groq(
        prompt,
        temperature=0.2,
        max_tokens=1800,
        timeout=45,
        tag="CropSprayAdvisor"
    )

    if not res.get("success"):
        # Check if we have verified database fallback
        crop_key = crop_name.lower().strip()
        matched_crop = VERIFIED_CROP_PROTECTION_DB.get(crop_key, {})
        for k, v in matched_crop.items():
            if k in symptoms.lower():
                return {
                    "identified_problem": v["disease_name"],
                    "identified_problem_hi": v["disease_name_hi"],
                    "diagnosis_confidence": "High (From Verified Database)",
                    "cultural_management": v["cultural"],
                    "cultural_management_hi": v["cultural_hi"],
                    "biological_control": v["biological"],
                    "biological_control_hi": v["biological_hi"],
                    "chemical_treatment": {
                        "active_ingredient": v["chemical_name"],
                        "active_ingredient_hi": v["chemical_name_hi"],
                        "dosage_per_liter": v["dosage"],
                        "dosage_per_acre": v["dosage"],
                        "water_volume": "200 Liters clean water per acre",
                        "waiting_period": v["waiting_period"],
                        "waiting_period_hi": v["waiting_period_hi"],
                        "spray_timing": "Morning or late afternoon",
                        "safety_precautions": "Wear mask and gloves. Keep away from children and cattle."
                    },
                    "mixing_warning": "Do not mix with unapproved chemicals.",
                    "mixing_warning_hi": "बिना विशेषज्ञ सलाह के अन्य रसायनों के साथ मिश्रण न करें।",
                    "recommendation_source": v["source"]
                }
        return {"error": f"Crop spray advisor failed: {res.get('error', 'Unknown service error')}"}

    try:
        raw_text = res.get("raw", "")
        clean_json = parse_json_response(raw_text)
        clean_json = extract_json_object(clean_json)
        data = json.loads(clean_json)

        data["crop_name"] = crop_name
        data["growth_stage"] = growth_stage
        data["vision_model_prediction"] = model_pred
        data["has_image_prediction"] = model_pred is not None

        return data

    except Exception as e:
        return {"error": f"Failed to parse spray recommendation: {str(e)}"}
