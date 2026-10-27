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

ANALYSIS_PROMPT_EN = """You are AgriShield AI — an expert agricultural scientist and crop doctor. 
Analyze this crop image very carefully and provide a COMPLETE analysis in STRICT JSON format.

You MUST respond with ONLY a valid JSON object (no markdown, no explanation, no extra text).

Required JSON structure:
{
  "crop_name": "exact crop name (e.g., Wheat, Rice, Maize, Tomato, Cotton)",
  "crop_name_hindi": "crop name in Hindi (Devanagari script)",
  "estimated_age_days": "age range in days (e.g., 30-35)",
  "growth_stage": "one of: Germination, Seedling, Vegetative, Flowering, Maturity",
  "health_score": 85,
  "health_status": "Healthy / Moderate Stress / Severe Stress / Critical",
  "pros": "2-3 positive observations about the crop",
  "cons": "2-3 issues or concerns observed or 'No significant issues' if healthy",
  "nutrient_requirements": "what nutrients the crop needs at this stage (NPK ratio, micronutrients)",
  "recommended_products": "specific fertilizers and products to use (e.g., DAP, Urea, Potash with dosage)",
  "disease_detected": "disease name if any, or 'No disease detected'",
  "disease_cause": "what causes this disease",
  "disease_prevention": "how to prevent this disease",
  "disease_treatment": "specific treatment with product names and dosage",
  "irrigation_advice": "how much and how often to water at this growth stage",
  "fertilizer_recommendation": "what fertilizer to apply now with exact dosage per acre",
  "growth_tips": "3-4 tips to maximize growth at this stage",
  "harvest_readiness": "how to know when crop is ready for harvest",
  "confidence": 88
}
"""

ANALYSIS_PROMPT_HI = """You are AgriShield AI — an expert agricultural scientist and crop doctor.
Analyze this crop image very carefully and provide a COMPLETE analysis in STRICT JSON format.

CRITICAL LANGUAGE REQUIREMENT:
The user is an Indian farmer using the app in HINDI.
All text fields (crop_name_hindi, growth_stage, health_status, pros, cons, nutrient_requirements, recommended_products, disease_detected, disease_cause, disease_prevention, disease_treatment, irrigation_advice, fertilizer_recommendation, growth_tips, harvest_readiness) MUST be written in 100% PURE HINDI (Devanagari script).
DO NOT use English words or Romanized Hindi in the descriptive and advice fields.
Respond with ONLY a valid JSON object without markdown fences or preamble.

Required JSON structure:
{
  "crop_name": "crop name in English (e.g. Wheat, Rice, Maize, Cotton, Soybean, Mustard, Tomato)",
  "crop_name_hindi": "फसल का शुद्ध हिंदी नाम (जैसे: गेहूं, धान, मक्का, कपास, सोयाबीन, सरसों, टमाटर)",
  "estimated_age_days": "दिनों में अनुमानित आयु (उदा. 30-35)",
  "growth_stage": "वानस्पतिक बढ़वार / कल्ले फूटना / फूल खिलना / दाना भराव / परिपक्वता",
  "health_score": 85,
  "health_status": "पूर्णतः स्वस्थ / हल्का तनाव / मध्यम तनाव / गंभीर रोगग्रस्त",
  "pros": "फसल के 2-3 मजबूत व सकारात्मक बिंदु शुद्ध हिंदी में (जैसे: पत्तियों का हरा रंग उत्तम है, अच्छी बढ़वार)",
  "cons": "2-3 कमियां अथवा समस्याएं हिंदी में (जैसे: निचली पत्तियों में हल्का पीलापन, कोई गंभीर समस्या नहीं)",
  "nutrient_requirements": "इस अवस्था में आवश्यक पोषक तत्वों की आवश्यकता हिंदी में (जैसे: नाइट्रोजन 30 किग्रा, जिंक 5 किग्रा प्रति एकड़)",
  "recommended_products": "संस्तुत उर्वरक व कृषि उत्पाद हिंदी में (जैसे: नीम लेपित यूरिया 45 किग्रा, एनपीके 19:19:19)",
  "disease_detected": "रोग का नाम शुद्ध हिंदी में, अथवा 'कोई रोग नहीं मिला'",
  "disease_cause": "रोग का मुख्य कारण हिंदी में",
  "disease_prevention": "रोग से बचाव व रोकथाम के उपाय हिंदी में",
  "disease_treatment": "दवाई एवं उपचार की सटीक खुराक हिंदी में",
  "irrigation_advice": "सिंचाई की व्यावहारिक सलाह हिंदी में",
  "fertilizer_recommendation": "उर्वरक देने की संस्तुति हिंदी में",
  "growth_tips": "पैदावार व बढ़वार बढ़ाने के 3-4 व्यावहारिक सुझाव हिंदी में",
  "harvest_readiness": "फसल कटाई की सही पहचान के लक्षण हिंदी में",
  "confidence": 88
}
"""

HINDI_MONTHS = {
    1: "जनवरी", 2: "फ़रवरी", 3: "मार्च", 4: "अप्रैल",
    5: "मई", 6: "जून", 7: "जुलाई", 8: "अगस्त",
    9: "सितम्बर", 10: "अक्टूबर", 11: "नवम्बर", 12: "दिसम्बर"
}


def calculate_harvest_prediction(crop_name, estimated_age_str, is_hi=False):
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
    dt = datetime.now() + timedelta(days=days_remaining)
    if is_hi:
        m_name = HINDI_MONTHS.get(dt.month, dt.strftime("%B"))
        harvest_date = f"{dt.day} {m_name} {dt.year}"
    else:
        harvest_date = dt.strftime("%d %B %Y")

    return {
        "total_lifecycle_days": total_days,
        "estimated_current_age": avg_age,
        "days_to_harvest": days_remaining,
        "expected_harvest_date": harvest_date,
    }


def _clean_hindi_text(text: str, fallback: str) -> str:
    """Ensure non-empty Hindi string."""
    if not text or str(text).strip() in ["N/A", "None", "No data", "null", ""]:
        return fallback
    return str(text).strip()


COMMON_DISEASE_TRANSLATIONS_HI = {
    "leaf blight": "पत्ती झुलसा रोग (Leaf Blight)",
    "early blight": "अगेती झुलसा (Early Blight)",
    "late blight": "पछेती झुलसा (Late Blight)",
    "bacterial leaf blight": "जीवाणु पत्ती झुलसा (Bacterial Leaf Blight)",
    "powdery mildew": "चूर्णिल आसिता (Powdery Mildew)",
    "downy mildew": "मृदुरोमिल आसिता (Downy Mildew)",
    "rust": "गेरुआ / रतुआ रोग (Rust)",
    "brown rust": "भूरा रतुआ (Brown Rust)",
    "yellow rust": "पीला रतुआ (Yellow Rust)",
    "black rust": "काला रतुआ (Black Rust)",
    "leaf spot": "पत्ती धब्बा रोग (Leaf Spot)",
    "cercospora": "सर्कोस्पोरा पत्ती धब्बा",
    "anthracnose": "एंथ्रेक्नोज़ रोग (Anthracnose)",
    "wilt": "उकठा रोग (Wilt)",
    "fusarium wilt": "फ्यूजेरियम उकठा रोग",
    "root rot": "जड़ सड़न रोग (Root Rot)",
    "stem rot": "तना सड़न रोग (Stem Rot)",
    "collar rot": "कॉलर रॉट (तना गलना)",
    "mosaic": "मोज़ेक वायरस रोग",
    "yellow vein mosaic": "पीली नस मोज़ेक वायरस",
    "leaf curl": "पत्ती मरोड़ रोग (Leaf Curl)",
    "smut": "कंडुआ रोग (Smut)",
    "loose smut": "खुला कंडुआ (Loose Smut)",
    "blast": "झोंका / ब्लास्ट रोग (Blast)",
    "sheath blight": "शीथ ब्लाइट (Sheath Blight)",
    "damping off": "आर्द्र गलन (Damping Off)",
    "canker": "कैंकर रोग (Canker)",
    "scab": "स्कैब रोग (Scab)",
    "chlorosis": "पत्तियों का पीलापन (Chlorosis)",
    "cannot determine": "स्पष्ट निदान उपलब्ध नहीं है",
}


def _translate_crop_fields(fields: dict, target_lang='hi') -> dict:
    """Translate user-facing fields using central AI service (Gemini / Groq)."""
    try:
        from services.ai_service import call_ai
        to_trans = {k: v for k, v in fields.items() if v and isinstance(v, str) and v.strip() not in ["N/A", "None", ""]}
        if not to_trans:
            return {}

        lang_name = "Hindi (Devanagari script)" if target_lang.startswith('hi') else "English"
        prompt = f"""You are an agricultural expert and crop doctor translating diagnosis results.
Translate the following user-facing crop analysis fields into natural, farmer-friendly {lang_name}.
Preserve scientific accuracy, technical diagnosis, chemical product dosages, numeric values, and days.
Return ONLY a valid JSON object with the exact same keys:
{json.dumps(to_trans, ensure_ascii=False, indent=2)}"""

        res = call_ai(prompt, json_mode=True, language=target_lang, temperature=0.1, max_tokens=1500)
        if res.get("success") and isinstance(res.get("data"), dict):
            return res["data"]
    except Exception as e:
        print(f"[AgriShield] Crop translation warning: {e}")
    return {}


def analyze_crop_with_groq(image_path, lang='hi'):
    """
    Send crop image to Vision AI for comprehensive analysis with bilingual support.
    """
    is_hi = str(lang).lower().startswith('hi')
    prompt = ANALYSIS_PROMPT_HI if is_hi else ANALYSIS_PROMPT_EN

    result = call_groq(
        prompt,
        images=[image_path],
        temperature=0.3,
        max_tokens=1500,
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

        crop_raw = analysis.get("crop_name", "Unknown")
        harvest_info = calculate_harvest_prediction(
            crop_raw,
            analysis.get("estimated_age_days", "30-40"),
            is_hi=is_hi
        )

        crop_hindi = analysis.get("crop_name_hindi", "").strip()
        if not crop_hindi or not re.search(r'[\u0900-\u097F]', crop_hindi):
            for k, v in CROP_LIFECYCLE.items():
                if k in crop_raw.lower():
                    crop_hindi = v["hindi"]
                    break
        if not crop_hindi:
            crop_hindi = crop_raw

        # Extract fields
        stage_raw = analysis.get("growth_stage", "Vegetative" if not is_hi else "वानस्पतिक बढ़वार")
        health_raw = analysis.get("health_status", "Healthy" if not is_hi else "पूर्णतः स्वस्थ")
        disease_raw = analysis.get("disease_detected", "No disease detected" if not is_hi else "कोई रोग नहीं मिला")
        disease_cause = analysis.get("disease_cause", "N/A")
        disease_prev = analysis.get("disease_prevention", "N/A")
        treatment_val = analysis.get("disease_treatment", "No treatment needed" if not is_hi else "उपचार की आवश्यकता नहीं है")
        irrigation = analysis.get("irrigation_advice", "N/A")
        fert_rec = analysis.get("fertilizer_recommendation", "N/A")
        growth_tips = analysis.get("growth_tips", "N/A")
        harvest_readiness = analysis.get("harvest_readiness", "N/A")
        pros_val = analysis.get("pros", "Good foliage" if not is_hi else "पत्तियां हरी-भरी हैं")
        cons_val = analysis.get("cons", "No significant issues" if not is_hi else "कोई गंभीर समस्या नहीं है")
        reqs_val = analysis.get("nutrient_requirements", "N/A")
        prod_val = analysis.get("recommended_products", "N/A")

        if is_hi:
            # Stage mapping
            stage_lower = stage_raw.lower()
            stage = "वानस्पतिक बढ़वार"
            if "seedling" in stage_lower or "अंकुर" in stage_lower:
                stage = "अंकुरण / पौध अवस्था"
            elif "flowering" in stage_lower or "फूल" in stage_lower:
                stage = "फूल / बालियां आने की अवस्था"
            elif "maturity" in stage_lower or "पक" in stage_lower:
                stage = "परिपक्वता / कटाई अवस्था"
            elif "germination" in stage_lower:
                stage = "अंकुरण अवस्था"
            elif re.search(r'[\u0900-\u097F]', stage_raw):
                stage = stage_raw

            # Health status mapping
            h_lower = health_raw.lower()
            if "healthy" in h_lower or "स्वस्थ" in h_lower:
                health_status = "पूर्णतः स्वस्थ"
            elif "moderate" in h_lower or "मध्यम" in h_lower:
                health_status = "मध्यम तनाव"
            elif "severe" in h_lower or "गंभीर" in h_lower:
                health_status = "गंभीर रोगग्रस्त"
            elif "critical" in h_lower or "संकट" in h_lower:
                health_status = "अति संकटग्रस्त"
            elif re.search(r'[\u0900-\u097F]', health_raw):
                health_status = health_raw
            else:
                health_status = "मध्यम तनाव"

            # Disease mapping
            d_lower = disease_raw.lower()
            if any(k in d_lower for k in ["no disease", "healthy", "none", "n/a", "nil"]):
                disease_val = "कोई रोग नहीं मिला (फसल स्वस्थ है)"
            else:
                disease_matched = None
                for en_key, hi_val in COMMON_DISEASE_TRANSLATIONS_HI.items():
                    if en_key in d_lower:
                        disease_matched = hi_val
                        break
                disease_val = disease_matched or disease_raw

            # Treatment mapping
            t_lower = str(treatment_val).lower()
            if any(k in t_lower for k in ["no treatment", "none", "n/a", "not needed"]):
                treatment_val = "उपचार की आवश्यकता नहीं है, फसल सामान्य है।"

            # Detect if fields contain English words that need translation
            fields_to_check = {
                "disease": disease_val,
                "disease_cause": disease_cause,
                "disease_prevention": disease_prev,
                "treatment": treatment_val,
                "irrigation_advice": irrigation,
                "fertilizer_recommendation": fert_rec,
                "growth_tips": growth_tips,
                "harvest_readiness": harvest_readiness,
                "pros": pros_val,
                "cons": cons_val,
                "requirements": reqs_val,
                "growth_products": prod_val,
            }

            # Check if there are English words
            english_fields = {k: v for k, v in fields_to_check.items() if isinstance(v, str) and re.search(r'[a-zA-Z]{3,}', v) and not (k == 'disease' and '(' in v)}
            if english_fields:
                translated = _translate_crop_fields(english_fields, target_lang='hi')
                if translated:
                    disease_val = translated.get("disease", disease_val)
                    disease_cause = translated.get("disease_cause", disease_cause)
                    disease_prev = translated.get("disease_prevention", disease_prev)
                    treatment_val = translated.get("treatment", treatment_val)
                    irrigation = translated.get("irrigation_advice", irrigation)
                    fert_rec = translated.get("fertilizer_recommendation", fert_rec)
                    growth_tips = translated.get("growth_tips", growth_tips)
                    harvest_readiness = translated.get("harvest_readiness", harvest_readiness)
                    pros_val = translated.get("pros", pros_val)
                    cons_val = translated.get("cons", cons_val)
                    reqs_val = translated.get("requirements", reqs_val)
                    prod_val = translated.get("growth_products", prod_val)

            disease_cause = _clean_hindi_text(disease_cause, "उपयुक्त कृषि परिस्थितियां")
            disease_prev = _clean_hindi_text(disease_prev, "समय पर संतुलित पोषण व सिंचाई करें")
            irrigation = _clean_hindi_text(irrigation, "खेत में ओट (हल्की नमी) बनाए रखें, जलभराव न होने दें")
            fert_rec = _clean_hindi_text(fert_rec, "अनुमोदित मात्रा में यूरिया व सूक्ष्म पोषक तत्वों का प्रयोग करें")
            growth_tips = _clean_hindi_text(growth_tips, "नियमित रूप से खरपतवार निकालें और कीटों की निगरानी करते रहें")
            harvest_readiness = _clean_hindi_text(harvest_readiness, "पत्तियां व बालियां सुनहरी पीली होने पर कटाई करें")
            pros_val = _clean_hindi_text(pros_val, "पत्तियां हरी-भरी हैं और पौधों का विकास सुचारू है")
            cons_val = _clean_hindi_text(cons_val, "कोई गंभीर समस्या या कीट का प्रकोप नहीं है")
            reqs_val = _clean_hindi_text(reqs_val, "नाइट्रोजन एवं सूक्ष्म पोषक तत्वों की सामान्य आवश्यकता")
            prod_val = _clean_hindi_text(prod_val, "नीम लेपित यूरिया व घुलनशील एनपीके 19:19:19")
        else:
            stage = stage_raw
            health_status = health_raw
            disease_val = disease_raw
            # If English is requested, ensure non-Devanagari
            if re.search(r'[\u0900-\u097F]', disease_val):
                d_en = _translate_crop_fields({"disease": disease_val, "cause": disease_cause, "treatment": treatment_val}, target_lang='en')
                disease_val = d_en.get("disease", disease_val)
                disease_cause = d_en.get("cause", disease_cause)
                treatment_val = d_en.get("treatment", treatment_val)

        # Build final structured response
        final_result = {
            "crop_name": crop_raw,
            "crop_name_hindi": crop_hindi,
            "age": str(analysis.get("estimated_age_days", "30-40")),
            "stage": stage,
            "health_score": analysis.get("health_score", 85),
            "health_status": health_status,
            "pros": pros_val,
            "cons": cons_val,
            "requirements": reqs_val,
            "growth_products": prod_val,
            "disease": disease_val,
            "disease_cause": disease_cause,
            "disease_prevention": disease_prev,
            "treatment": treatment_val,
            "irrigation_advice": irrigation,
            "fertilizer_recommendation": fert_rec,
            "growth_tips": growth_tips,
            "harvest_readiness": harvest_readiness,
            "harvest_days": harvest_info["days_to_harvest"],
            "harvest_date": harvest_info["expected_harvest_date"],
            "total_lifecycle": harvest_info["total_lifecycle_days"],
            "pest_detected": "कोई कीट नहीं मिला" if is_hi else "No pest detected",
            "pest_type": "लागू नहीं" if is_hi else "N/A",
            "pest_removal_organic": "नीम का तेल (5 मिली प्रति लीटर पानी) का छिड़काव करें" if is_hi else "Apply Neem Oil 10,000 ppm (5ml per liter)",
            "pest_removal_chemical": "अनुमोदित कीटनाशक का संतुलित प्रयोग करें" if is_hi else "Use CIBRC registered insecticide as per label recommendation",
            "confidence": analysis.get("confidence", 90),
        }

        return final_result

    except json.JSONDecodeError as e:
        print(f"[AgriShield] JSON Parse Error: {e}")
        return {"error": "Failed to parse AI response", "raw_response": raw_text[:500]}
    except Exception as e:
        print(f"[AgriShield] Error: {e}")
        return {"error": str(e)}
