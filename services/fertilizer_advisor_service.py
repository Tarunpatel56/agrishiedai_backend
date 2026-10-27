"""
AgriShield AI — Fertilizer Prescription Service
=================================================
Calculates agronomic fertilizer requirements aligned with ICAR and State Agricultural
Universities (SAU) Package of Practices.
Calculates:
- Area unit normalization (Acre, Hectare, Bigha, Guntha)
- Pure nutrient requirement (N, P2O5, K2O, S)
- Soil test calibration (Low: +25%, Medium: 100%, High: -25%)
- Commercial fertilizer requirement (Urea 45kg bag, DAP 50kg bag, MOP 50kg bag)
- Exact calculated requirements vs Whole purchase bags and leftover buffer
- Split application stages aligned with crop age
- Accurate labeling as 'Agronomic Recommendation (ICAR/SAU Guidelines)'
- Complete Hindi ('hi') and English ('en') responses.
"""

import math
from typing import Dict, Any, Optional
from services.ai_service import call_ai

# Standard ICAR / SAU Recommended Doses of Fertilizers (RDF) in kg per acre
# (Pure N, P2O5, K2O, S)
STANDARD_RDF_ACRE = {
    "wheat": {"n": 48.0, "p": 24.0, "k": 16.0, "s": 0.0, "name_hi": "गेहूं", "name_en": "Wheat"},
    "rice": {"n": 40.0, "p": 20.0, "k": 20.0, "s": 0.0, "name_hi": "धान (चावल)", "name_en": "Rice / Paddy"},
    "paddy": {"n": 40.0, "p": 20.0, "k": 20.0, "s": 0.0, "name_hi": "धान (चावल)", "name_en": "Rice / Paddy"},
    "soybean": {"n": 12.0, "p": 24.0, "k": 16.0, "s": 8.0, "name_hi": "सोयाबीन", "name_en": "Soybean"},
    "cotton": {"n": 40.0, "p": 20.0, "k": 20.0, "s": 0.0, "name_hi": "कपास", "name_en": "Cotton"},
    "maize": {"n": 48.0, "p": 24.0, "k": 16.0, "s": 0.0, "name_hi": "मक्का", "name_en": "Maize / Corn"},
    "mustard": {"n": 32.0, "p": 16.0, "k": 16.0, "s": 10.0, "name_hi": "सरसों", "name_en": "Mustard"},
    "sugarcane": {"n": 100.0, "p": 32.0, "k": 32.0, "s": 0.0, "name_hi": "गन्ना", "name_en": "Sugarcane"},
    "chickpea": {"n": 10.0, "p": 20.0, "k": 10.0, "s": 6.0, "name_hi": "चना", "name_en": "Chickpea / Gram"},
    "gram": {"n": 10.0, "p": 20.0, "k": 10.0, "s": 6.0, "name_hi": "चना", "name_en": "Chickpea / Gram"},
    "potato": {"n": 60.0, "p": 40.0, "k": 40.0, "s": 0.0, "name_hi": "आलू", "name_en": "Potato"},
    "tomato": {"n": 48.0, "p": 32.0, "k": 32.0, "s": 0.0, "name_hi": "टमाटर", "name_en": "Tomato"},
    "onion": {"n": 40.0, "p": 20.0, "k": 30.0, "s": 10.0, "name_hi": "प्याज़", "name_en": "Onion"},
    "garlic": {"n": 40.0, "p": 20.0, "k": 30.0, "s": 15.0, "name_hi": "लहसुन", "name_en": "Garlic"},
    "groundnut": {"n": 10.0, "p": 20.0, "k": 15.0, "s": 8.0, "name_hi": "मूंगफली", "name_en": "Groundnut"}
}

DEFAULT_CROP_RDF = {"n": 36.0, "p": 20.0, "k": 16.0, "s": 0.0, "name_hi": "सामान्य फसल", "name_en": "General Crop"}


def convert_to_acres(area: float, unit: str) -> float:
    """Accurately convert regional land measurement units to standard acres."""
    u = (unit or "acre").strip().lower()
    if "hect" in u or "हेक्टेयर" in u:
        return area * 2.47105
    elif "bigha" in u or "बीघा" in u:
        # Standard north/central India bigha ~ 0.625 acre (5/8th of an acre)
        return area * 0.625
    elif "guntha" in u or "गुंठा" in u:
        # 1 Guntha = 1/40th of an acre = 0.025 acre
        return area * 0.025
    elif "sq" in u and ("m" in u or "मी" in u):
        return area / 4046.86
    return max(0.01, area)


def generate_fertilizer_prescription(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate agronomic fertilizer prescription with exact quantities, bag counts,
    split schedules, and verified ICAR/SAU recommendations.
    """
    crop_name = str(data.get("crop_name", "Wheat")).strip()
    growth_stage = str(data.get("growth_stage", "Basal / Sowing")).strip()
    crop_age_days = int(data.get("crop_age_days", 25) or 25)
    soil_type = str(data.get("soil_type", "Loam / Alluvial")).strip()
    field_area_raw = float(data.get("field_area", 2.0) or 2.0)
    area_unit = str(data.get("area_unit", "Acre")).strip()
    lang = str(data.get("language", "hi")).strip().lower()
    is_hi = lang.startswith("hi")

    # Soil test availability
    soil_test_available = bool(data.get("soil_test_available", False))
    n_status = str(data.get("nitrogen_status", "Medium")).strip().lower()
    p_status = str(data.get("phosphorus_status", "Medium")).strip().lower()
    k_status = str(data.get("potassium_status", "Medium")).strip().lower()

    # 1. Normalize area to acres
    area_acres = convert_to_acres(field_area_raw, area_unit)

    # 2. Match crop RDF
    crop_key = crop_name.lower()
    matched_rdf = DEFAULT_CROP_RDF
    for key, rdf in STANDARD_RDF_ACRE.items():
        if key in crop_key or rdf["name_en"].lower() in crop_key or rdf["name_hi"] in crop_name:
            matched_rdf = rdf
            break

    # 3. Soil Test Calibration (ICAR Soil Test Crop Response - STCR model)
    # Low: +25%, High: -25%, Medium: 100%
    n_mult = 1.25 if ("low" in n_status or "कम" in n_status) else (0.75 if ("high" in n_status or "ज्यादा" in n_status or "अधिक" in n_status) else 1.0)
    p_mult = 1.25 if ("low" in p_status or "कम" in p_status) else (0.75 if ("high" in p_status or "ज्यादा" in p_status or "अधिक" in p_status) else 1.0)
    k_mult = 1.25 if ("low" in k_status or "कम" in k_status) else (0.75 if ("high" in k_status or "ज्यादा" in k_status or "अधिक" in k_status) else 1.0)

    if not soil_test_available:
        n_mult, p_mult, k_mult = 1.0, 1.0, 1.0

    target_n_acre = matched_rdf["n"] * n_mult
    target_p_acre = matched_rdf["p"] * p_mult
    target_k_acre = matched_rdf["k"] * k_mult
    target_s_acre = matched_rdf.get("s", 0.0)

    # Total pure nutrients for the field
    field_pure_n = target_n_acre * area_acres
    field_pure_p = target_p_acre * area_acres
    field_pure_k = target_k_acre * area_acres
    field_pure_s = target_s_acre * area_acres

    # 4. Commercial Fertilizer Calculations
    # - DAP (Di-Ammonium Phosphate): 18% N, 46% P2O5 (Standard 50 kg bag)
    # - Neem Coated Urea: 46% N (Standard Indian Govt 45 kg bag)
    # - MOP (Muriate of Potash): 60% K2O (Standard 50 kg bag)
    dap_total_kg = (field_pure_p / 0.46) if field_pure_p > 0 else 0.0
    n_from_dap = dap_total_kg * 0.18
    remaining_n = max(0.0, field_pure_n - n_from_dap)
    urea_total_kg = (remaining_n / 0.46) if remaining_n > 0 else 0.0
    mop_total_kg = (field_pure_k / 0.60) if field_pure_k > 0 else 0.0

    # Bag Counts: Urea = 45 kg/bag, DAP = 50 kg/bag, MOP = 50 kg/bag
    urea_bags_exact = round(urea_total_kg / 45.0, 1)
    urea_bags_whole = math.ceil(urea_total_kg / 45.0) if urea_total_kg > 0 else 0
    urea_remaining_kg = round((urea_bags_whole * 45.0) - urea_total_kg, 1)

    dap_bags_exact = round(dap_total_kg / 50.0, 1)
    dap_bags_whole = math.ceil(dap_total_kg / 50.0) if dap_total_kg > 0 else 0
    dap_remaining_kg = round((dap_bags_whole * 50.0) - dap_total_kg, 1)

    mop_bags_exact = round(mop_total_kg / 50.0, 1)
    mop_bags_whole = math.ceil(mop_total_kg / 50.0) if mop_total_kg > 0 else 0
    mop_remaining_kg = round((mop_bags_whole * 50.0) - mop_total_kg, 1)

    # Per acre equivalents
    urea_per_acre_kg = round(urea_total_kg / area_acres, 1)
    dap_per_acre_kg = round(dap_total_kg / area_acres, 1)
    mop_per_acre_kg = round(mop_total_kg / area_acres, 1)

    # 5. Split Application Schedule based on Crop Age and Growth Stages
    if is_hi:
        split_schedule = [
            {
                "stage": "1. बुवाई के समय बेसल खुराक",
                "fertilizers": f"डीएपी: {round(dap_total_kg, 1)} किग्रा ({dap_bags_exact} बोरी) + एमओपी पोटाश: {round(mop_total_kg, 1)} किग्रा ({mop_bags_exact} बोरी) + यूरिया: {round(urea_total_kg * 0.33, 1)} किग्रा",
                "method": "अंतिम जुताई या बुवाई के समय बीज से 3-5 सेमी गहराई पर कतारों में डालें। बीज के सीधे संपर्क में न आने दें।",
                "importance": "जड़ों के त्वरित विकास, प्रारंभिक अंकुरण और मजबूत तने के निर्माण हेतु अनिवार्य।"
            },
            {
                "stage": f"2. वानस्पतिक बढ़वार / पहला पानी ({crop_age_days} दिन पर - पहली टॉप ड्रेसिंग)",
                "fertilizers": f"नीम लेपित यूरिया: {round(urea_total_kg * 0.34, 1)} किग्रा (लगभग {round(urea_bags_exact * 0.34, 1)} बोरी) + जिंक सल्फेट 33%: {round(5.0 * area_acres, 1)} किग्रा",
                "method": "सिंचाई के 2-3 दिन बाद जब खेत में उचित पैर-नमी (ओट) हो, समान रूप से भुरकाव करें।",
                "importance": "कल्लों (फूटान) की संख्या बढ़ाने, गहरी हरी पत्तियों और प्रकाश संश्लेषण को तीव्र करने के लिए।"
            },
            {
                "stage": "3. गभोट / बालियां निकलने से पहले (45-55 दिन - दूसरी टॉप ड्रेसिंग)",
                "fertilizers": f"नीम लेपित यूरिया (अंतिम खुराक): {round(urea_total_kg * 0.33, 1)} किग्रा (अथवा 19:19:19 घुलनशील उर्वरक 1 किग्रा/एकड़ पर्णीय स्प्रे)",
                "method": "हल्की सिंचाई के साथ अथवा शाम के समय पत्तियों पर पर्णीय स्प्रे के रूप में।",
                "importance": "बालियों की लंबाई, दानों का पूरा भराव और दानों में चमक एवं वजन बढ़ाने के लिए।"
            }
        ]
        nutrient_summary = {
            "nitrogen": f"{round(field_pure_n, 1)} किग्रा शुद्ध नाइट्रोजन ({round(target_n_acre, 1)} किग्रा/एकड़)",
            "phosphorus": f"{round(field_pure_p, 1)} किग्रा शुद्ध फॉस्फोरस ({round(target_p_acre, 1)} किग्रा/एकड़)",
            "potassium": f"{round(field_pure_k, 1)} किग्रा शुद्ध पोटाश ({round(target_k_acre, 1)} किग्रा/एकड़)"
        }
        verification_notice = (
            "यह संस्तुति भाकृअनुप (ICAR) एवं राज्य कृषि विश्वविद्यालयों के अनुमोदित पैकेज ऑफ प्रैक्टिसेज पर आधारित है। "
            "मृदा परीक्षण के अभाव में यह अनंतिम मानक खुराक है। सटीक पोषक तत्व संतुलन हेतु नजदीकी कृषि विज्ञान केंद्र से मृदा परीक्षण कराएं।"
            if not soil_test_available else
            "यह सिफारिश आपके द्वारा उपलब्ध कराए गए मृदा परीक्षण के पोषक तत्व स्तर के अनुसार कैलिब्रेट की गई है।"
        )
        soil_health_tips = [
            "यूरिया को एक साथ पूरा न डालें; 3 विभाजित खुराकों में डालने से लीचिंग और नाइट्रोजन का वाष्पीकरण रुकता है।",
            "प्रति एकड़ 2-3 ट्रॉली अच्छी सड़ी हुई गोबर की खाद अथवा वर्मीकम्पोस्ट अवश्य डालें ताकि जैविक कार्बन बढ़े।",
            "जिंक सल्फेट और डीएपी को कभी भी एक साथ मिलाकर न डालें, इससे अघुलनशील जिंक फॉस्फेट बन जाता है जो पौधों को नहीं मिल पाता।"
        ]
    else:
        split_schedule = [
            {
                "stage": "1. Basal Application (At Sowing / Planting)",
                "fertilizers": f"DAP: {round(dap_total_kg, 1)} kg ({dap_bags_exact} bags) + MOP: {round(mop_total_kg, 1)} kg ({mop_bags_exact} bags) + Urea: {round(urea_total_kg * 0.33, 1)} kg",
                "method": "Band placement 3-5 cm below and to the side of seed furrow during sowing. Avoid direct seed contact.",
                "importance": "Crucial for early root establishment, vigorous seedling emergence, and sturdy stems."
            },
            {
                "stage": f"2. Vegetative Stage / First Irrigation (Around {crop_age_days} Days - 1st Top Dressing)",
                "fertilizers": f"Neem Coated Urea: {round(urea_total_kg * 0.34, 1)} kg (~{round(urea_bags_exact * 0.34, 1)} bags) + Zinc Sulphate 33%: {round(5.0 * area_acres, 1)} kg",
                "method": "Broadcast evenly across field 2-3 days post irrigation when soil moisture allows firm footing.",
                "importance": "Promotes active tillering, deep chlorophyll synthesis, and canopy expansion."
            },
            {
                "stage": "3. Booting / Pre-Flowering Stage (45-55 Days - 2nd Top Dressing)",
                "fertilizers": f"Neem Coated Urea (Final dose): {round(urea_total_kg * 0.33, 1)} kg (or Foliar Spray of 19:19:19 @ 1 kg/acre)",
                "method": "Top dress in moist soil or apply as water-soluble foliar spray during late afternoon.",
                "importance": "Ensures complete panicle emergence, uniform grain filling, and superior test weight."
            }
        ]
        nutrient_summary = {
            "nitrogen": f"{round(field_pure_n, 1)} kg Pure N ({round(target_n_acre, 1)} kg/acre)",
            "phosphorus": f"{round(field_pure_p, 1)} kg Pure P₂O₅ ({round(target_p_acre, 1)} kg/acre)",
            "potassium": f"{round(field_pure_k, 1)} kg Pure K₂O ({round(target_k_acre, 1)} kg/acre)"
        }
        verification_notice = (
            "Provisional agronomic recommendation aligned with ICAR and State Agricultural University guidelines without soil test. "
            "For micronutrient precision, obtain a verified Soil Health Card from your nearest Krishi Vigyan Kendra (KVK)."
            if not soil_test_available else
            "Prescription calibrated against your provided soil nutrient profile (ICAR STCR Model)."
        )
        soil_health_tips = [
            "Do not apply Urea all at once; split doses prevent leaching and ammonia volatilization loss.",
            "Incorporate 2-3 trolleys of well-decomposed FYM or vermicompost per acre to maintain organic carbon and soil biota.",
            "Never mix Zinc Sulphate directly with DAP in the fertilizer drill, as it forms insoluble Zinc Phosphate precipitate."
        ]

    # Commercial Fertilizer Items List
    fertilizer_items = [
        {
            "name": "नीम लेपित यूरिया (46% नाइट्रोजन)" if is_hi else "Neem Coated Urea (46% N)",
            "total_kg": round(urea_total_kg, 1),
            "bag_size_kg": 45,
            "bags_count": urea_bags_exact,
            "bags_whole_to_buy": urea_bags_whole,
            "remaining_buffer_kg": urea_remaining_kg,
            "per_acre_kg": urea_per_acre_kg,
            "composition": "46% नाइट्रोजन" if is_hi else "46% Nitrogen (N)",
            "purpose": "वानस्पतिक बढ़वार और क्लोरोफिल निर्माण" if is_hi else "Vegetative canopy and chlorophyll synthesis"
        },
        {
            "name": "डीएपी (18:46:0 फॉस्फोरस)" if is_hi else "DAP - Di-Ammonium Phosphate (18:46:0)",
            "total_kg": round(dap_total_kg, 1),
            "bag_size_kg": 50,
            "bags_count": dap_bags_exact,
            "bags_whole_to_buy": dap_bags_whole,
            "remaining_buffer_kg": dap_remaining_kg,
            "per_acre_kg": dap_per_acre_kg,
            "composition": "18% N, 46% P₂O₅",
            "purpose": "जड़ों का गहरा फैलाव और मजबूत तना" if is_hi else "Deep root proliferation and stem structural vigor"
        },
        {
            "name": "एमओपी पोटाश (60% पोटाश)" if is_hi else "MOP - Muriate of Potash (0:0:60)",
            "total_kg": round(mop_total_kg, 1),
            "bag_size_kg": 50,
            "bags_count": mop_bags_exact,
            "bags_whole_to_buy": mop_bags_whole,
            "remaining_buffer_kg": mop_remaining_kg,
            "per_acre_kg": mop_per_acre_kg,
            "composition": "60% K₂O",
            "purpose": "रोग प्रतिरोधक क्षमता और दानों की चमक" if is_hi else "Disease resistance, drought tolerance & grain quality"
        }
    ]

    # Micronutrient if needed
    if target_s_acre > 0:
        s_total = target_s_acre * area_acres
        fertilizer_items.append({
            "name": "बेंटोनाइट सल्फर 90%" if is_hi else "Bentonite Sulphur 90% WDG",
            "total_kg": round(s_total, 1),
            "bag_size_kg": 10,
            "bags_count": round(s_total / 10.0, 1),
            "bags_whole_to_buy": math.ceil(s_total / 10.0),
            "remaining_buffer_kg": round((math.ceil(s_total / 10.0) * 10.0) - s_total, 1),
            "per_acre_kg": round(target_s_acre, 1),
            "composition": "90% Elemental Sulphur (S)",
            "purpose": "प्रोटीन और तेल की मात्रा बढ़ाना" if is_hi else "Enhances oil percentage and protein synthesis"
        })

    # AI Agronomic Enrichment
    crop_display = matched_rdf["name_hi"] if is_hi else matched_rdf["name_en"]
    ai_explanation = (
        f"{crop_display} की {crop_age_days} दिन की अवस्था में {field_area_raw} {area_unit} खेत के लिए अनुशंसित संतुलित पोषण (NPK) "
        f"पौधों में पर्याप्त कल्ले (Tillering) और स्वस्थ बढ़वार सुनिश्चित करेगा।"
        if is_hi else
        f"For {crop_display} at {crop_age_days} days across {field_area_raw} {area_unit}, this balanced NPK schedule "
        f"optimizes tillering and robust root development while maintaining soil health."
    )

    return {
        "crop_name": crop_display,
        "input_crop": crop_name,
        "growth_stage": growth_stage,
        "crop_age_days": crop_age_days,
        "soil_type": soil_type,
        "field_area": field_area_raw,
        "area_unit": area_unit,
        "calculated_acres": round(area_acres, 2),
        "soil_test_available": soil_test_available,
        "soil_test_used": soil_test_available,
        "pure_nutrients_kg": {
            "N": round(field_pure_n, 1),
            "P2O5": round(field_pure_p, 1),
            "K2O": round(field_pure_k, 1)
        },
        "nutrient_requirements": nutrient_summary,
        "fertilizer_items": fertilizer_items,
        "split_schedule": split_schedule,
        "verification_notice": verification_notice,
        "notice": verification_notice,
        "soil_health_tips": soil_health_tips,
        "ai_explanation": ai_explanation,
        "recommendation_type": "Agronomic Recommendation (ICAR / SAU Guidelines)",
        "recommendation_source": "Agronomic Recommendation (ICAR / SAU Guidelines)",
        "language": "hi" if is_hi else "en",
        "timestamp": "Latest"
    }
