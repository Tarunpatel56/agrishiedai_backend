"""
Soil Analysis Service
=====================
Uses groq_client for all API calls.
"""

from services.groq_client import call_groq_json_object, call_groq_json_array


import re
import json

# =====================================================
# 1. SOIL IMAGE ANALYSIS (BILINGUAL)
# =====================================================
SOIL_PROMPT_EN = """You are an expert agricultural soil scientist. Look at this image carefully.

IMPORTANT: First determine if this image actually shows SOIL or GROUND/EARTH. 
If the image is NOT soil (e.g. a person, animal, building, food, random object, selfie, document, text etc.), you MUST respond with:
{"is_soil": false, "error": "This is not a soil image. Please upload a clear photo of soil or ground."}

If it IS a soil image, respond with ONLY this JSON:
{
  "is_soil": true,
  "soil_type": "Clay / Sandy / Loamy / Silty / Peaty / Chalky / Laterite / Black Cotton / Red / Alluvial",
  "soil_type_hindi": "Hindi name of soil type in Devanagari",
  "ph_level": "estimated pH (e.g., Neutral - 6.5-7.2)",
  "soil_texture": "Fine-grained / Medium-grained / Coarse",
  "soil_color": "observed color (e.g. Dark Brown, Reddish Brown, Grey)",
  "soil_health": "Good / Fair / Poor",
  "health_score": 78,
  "moisture_level": "Dry / Moderate / Wet",
  "organic_matter": "Low / Medium / High",
  "composition": "detailed soil composition description in English",
  "nitrogen_level": "Low / Medium / High",
  "phosphorus_level": "Low / Medium / High",
  "potassium_level": "Low / Medium / High",
  "advisory": "2-3 lines of practical improvement advice in English"
}

Respond with ONLY the JSON, no extra text."""

SOIL_PROMPT_HI = """You are an expert agricultural soil scientist. Look at this image carefully.

IMPORTANT: First determine if this image actually shows SOIL or GROUND/EARTH. 
If the image is NOT soil, you MUST respond with:
{"is_soil": false, "error": "यह मिट्टी की छवि नहीं है। कृपया मिट्टी या खेत की जमीन की स्पष्ट तस्वीर अपलोड करें।"}

CRITICAL LANGUAGE REQUIREMENT:
The user is an Indian farmer using the app in HINDI.
All text descriptions (soil_type_hindi, ph_level, soil_texture, soil_color, soil_health, moisture_level, organic_matter, composition, nitrogen_level, phosphorus_level, potassium_level, advisory) MUST be written in pure, natural HINDI (Devanagari script).
Preserve numerical values (e.g. pH 6.5-7.2, health_score 80).

If it IS a soil image, respond with ONLY this JSON:
{
  "is_soil": true,
  "soil_type": "Loamy / Alluvial / Clay / Sandy / Black Cotton / Red",
  "soil_type_hindi": "दोमट मिट्टी / जलोढ़ मिट्टी / काली मिट्टी / लाल मिट्टी / बलुई मिट्टी",
  "ph_level": "सामान्य (6.5 - 7.2 pH) - फसलों के लिए उत्तम",
  "soil_texture": "मध्यम दानेदार (Medium-grained)",
  "soil_color": "गहरा भूरा (Dark Brown)",
  "soil_health": "उत्कृष्ट / अच्छा",
  "health_score": 80,
  "moisture_level": "सामान्य नमी",
  "organic_matter": "मध्यम",
  "composition": "संतुलित उपजाऊ मिट्टी जिसमें उचित जीवांश व जल धारण क्षमता है।",
  "nitrogen_level": "मध्यम",
  "phosphorus_level": "मध्यम",
  "potassium_level": "पर्याप्त",
  "advisory": "उपजाऊ कृषि मृदा। दलहनी फसलें, गेहूं, चना अथवा मौसमी सब्जियों के लिए सर्वोत्तम। जैविक कम्पोस्ट का उपयोग जारी रखें।"
}

Respond with ONLY the JSON, no extra text."""


def _translate_soil_fields(fields: dict, target_lang='hi') -> dict:
    """Translate soil explanation fields using AI."""
    try:
        from services.ai_service import call_ai
        to_trans = {k: v for k, v in fields.items() if v and isinstance(v, str) and v.strip() not in ["N/A", "None", ""]}
        if not to_trans:
            return {}

        lang_name = "Hindi (Devanagari script)" if str(target_lang).lower().startswith('hi') else "English"
        prompt = f"""You are an agricultural soil scientist and translator.
Translate the following soil test and advisory fields into natural {lang_name} for an Indian farmer.
Preserve numbers, numeric pH ranges, percentages, and chemical elements (N, P, K).
Return ONLY a valid JSON object with the exact same keys:
{json.dumps(to_trans, ensure_ascii=False, indent=2)}"""

        res = call_ai(prompt, json_mode=True, language=target_lang, temperature=0.1, max_tokens=1000)
        if res.get("success") and isinstance(res.get("data"), dict):
            return res["data"]
    except Exception as e:
        print(f"[AgriShield] Soil translation warning: {e}")
    return {}


def analyze_soil_image(image_path, lang='hi'):
    """Analyze a soil image using Vision API with language support."""
    is_hi = str(lang).lower().startswith('hi')
    prompt = SOIL_PROMPT_HI if is_hi else SOIL_PROMPT_EN

    result = call_groq_json_object(
        prompt,
        images=[image_path],
        temperature=0.3,
        max_tokens=1024,
        timeout=60,
        tag="SoilAnalysis",
    )

    if "error" in result and "is_soil" not in result:
        return result

    # Check if image was rejected as non-soil
    if result.get("is_soil") == False:
        default_err = "यह मिट्टी की छवि नहीं है। कृपया मिट्टी की स्पष्ट तस्वीर अपलोड करें।" if is_hi else "This is not a soil image. Please upload a clear photo of soil."
        return {"error": result.get("error", default_err)}

    # Ensure Hindi translations if Hindi mode is active
    if is_hi:
        advisory_val = result.get("advisory", "")
        composition_val = result.get("composition", "")
        texture_val = result.get("soil_texture", "")

        fields_to_check = {
            "advisory": advisory_val,
            "composition": composition_val,
            "soil_texture": texture_val,
        }
        # If any of these fields have Latin characters, translate
        has_latin = any(re.search(r'[a-zA-Z]{3,}', str(v)) for v in fields_to_check.values() if v)
        if has_latin:
            translated = _translate_soil_fields(fields_to_check, target_lang='hi')
            if translated:
                result["advisory"] = translated.get("advisory", advisory_val)
                result["composition"] = translated.get("composition", composition_val)
                result["soil_texture"] = translated.get("soil_texture", texture_val)

        # Standard Hindi mappings
        if not result.get("soil_type_hindi") or not re.search(r'[\u0900-\u097F]', str(result.get("soil_type_hindi"))):
            soil_t = str(result.get("soil_type", "")).lower()
            if "loam" in soil_t:
                result["soil_type_hindi"] = "दोमट मिट्टी"
            elif "clay" in soil_t:
                result["soil_type_hindi"] = "चिकनी मिट्टी"
            elif "sand" in soil_t:
                result["soil_type_hindi"] = "बलुई मिट्टी"
            elif "alluvial" in soil_t:
                result["soil_type_hindi"] = "जलोढ़ मिट्टी"
            elif "black" in soil_t:
                result["soil_type_hindi"] = "काली मिट्टी"
            elif "red" in soil_t:
                result["soil_type_hindi"] = "लाल मिट्टी"
            else:
                result["soil_type_hindi"] = "उपजाऊ कृषि मिट्टी"

    return result


# =====================================================
# 2. PLANT RECOMMENDATIONS (Pot / Gamla / Home Garden)
# =====================================================
def get_plant_recommendations(soil_data, lang='hi'):
    """Get pot/garden plant recommendations based on soil data with language support."""
    is_hi = str(lang).lower().startswith('hi')
    soil_info = _format_soil_info(soil_data)

    lang_instr = """CRITICAL LANGUAGE REQUIREMENT:
The user is an Indian farmer using the app in HINDI.
All text descriptions (plant_name_hindi, suitability, plant_type, plant_age_info, sunlight_needs, water_needs, fertilizer_needs, soil_preparation, planting_method, care_steps, common_diseases, harvest_info, benefits, best_season, difficulty_level, description) MUST be in 100% PURE HINDI (Devanagari script). Keep plant_name in English.""" if is_hi else "All text descriptions must be in English."

    prompt = f"""You are an expert Indian horticulture and home gardening advisor.

Based on this soil analysis, recommend 20-25 PLANTS that can be grown in POTS, CONTAINERS, GAMLA, HOME GARDEN, TERRACE GARDEN or BALCONY.

{soil_info}

{lang_instr}

CRITICAL RULES:
- IMPORTANT: List ALL FLOWER plants FIRST in the array, then other types after flowers.
- Include at least 8-10 FLOWER plants like Rose, Marigold, Jasmine, Hibiscus, Sunflower, Lily, Dahlia, Mogra, Champa, Sadabahar, Bougainvillea, Rajnigandha, Chameli, Genda, Gulmohar etc.
- Then include herbs, medicinal plants, ornamental plants, small vegetables (tomato, chili, mint, tulsi, etc.)
- ONLY recommend plants that can be grown in POTS/GAMLA/HOME GARDEN
- DO NOT recommend field crops like wheat, rice, sugarcane, cotton, soybean etc. Those belong in CROPS section.
- Rate each plant: Excellent (best match), Good (grows well), Moderate (will survive)
- All benefits from FARMER/GROWER perspective (easy to maintain, saves money, medicinal value, sells well in local market)
- Give as many plants as possible, minimum 20

Respond with ONLY a valid JSON array:
[
  {{
    "plant_name": "English Name",
    "plant_name_hindi": "हिंदी नाम (जैसे: गेंदा, गुलाब, तुलसी)",
    "suitability": "{"सर्वोत्तम / अच्छा / मध्यम" if is_hi else "Excellent / Good / Moderate"}",
    "plant_type": "{"फूल / सब्जी / औषधीय / शोभाकारी" if is_hi else "Flower / Vegetable / Herb / Medicinal / Ornamental"}",
    "growth_days": 90,
    "plant_age_info": "{"अंकुरण: 0-15 दिन, बढ़वार: 15-45 दिन, फूल: 45-75 दिन" if is_hi else "Seedling: 0-15 days, Vegetative: 15-45 days, Flowering: 45-75 days"}",
    "sunlight_needs": "{"पूर्ण धूप - 6-8 घंटे प्रतिदिन" if is_hi else "Full Sun - 6-8 hours daily"}",
    "water_needs": "{"नियमित हल्की सिंचाई" if is_hi else "Daily watering - 500ml per plant"}",
    "fertilizer_needs": "{"वर्मीकम्पोस्ट या डीएपी 15 दिन में एक बार" if is_hi else "50g DAP per plant every 15 days"}",
    "soil_preparation": "{"गमले के लिए मिट्टी तैयार करने की विधि" if is_hi else "How to prepare pot/gamla soil mix"}",
    "planting_method": "{"गमले में पौधा लगाने का तरीका" if is_hi else "Step by step planting in pot/gamla"}",
    "care_steps": ["{"देखभाल कदम 1" if is_hi else "Step 1"}", "{"देखभाल कदम 2" if is_hi else "Step 2"}"],
    "common_diseases": "{"प्रमुख रोग एवं देसी/जैविक रोकथाम" if is_hi else "Common diseases and prevention"}",
    "harvest_info": "{"कब और कैसे कटाई करें" if is_hi else "When and how to harvest"}",
    "benefits": ["{"लाभ 1" if is_hi else "Benefit 1"}", "{"लाभ 2" if is_hi else "Benefit 2"}"],
    "best_season": "{"अक्टूबर-नवंबर (रबी)" if is_hi else "October-November (Rabi)"}",
    "difficulty_level": "{"बहुत आसान / मध्यम" if is_hi else "Easy / Medium / Hard"}",
    "description": "{"गमले व बगीचे के लिए इस पौधे का 2-3 पंक्तियों में परिचय" if is_hi else "2-3 lines about this plant"}"
  }}
]

REMEMBER: Flower plants MUST come FIRST in the array. Give REALISTIC Indian home garden data. Respond with ONLY JSON array."""

    result = call_groq_json_array(
        prompt,
        temperature=0.4,
        max_tokens=8192,
        timeout=120,
        tag="PlantRecommendations",
    )

    if isinstance(result, dict) and "error" in result:
        return result
    return {"plants": result}


# =====================================================
# 3. CROP RECOMMENDATIONS (Field-level farming)
# =====================================================
def get_crop_recommendations(soil_data, image_paths, season=None, lang='hi'):
    """Get field crop recommendations using soil data + field photos with language support."""
    if len(image_paths) < 3:
        return {"error": "Minimum 3 field photos required"}

    is_hi = str(lang).lower().startswith('hi')
    soil_info = _format_soil_info(soil_data)

    # Build season filter instruction
    season_filter = ""
    if season:
        season_map = {
            "winter": "ONLY recommend RABI / WINTER season crops like Wheat, Mustard, Gram (Chana), Peas, Barley, Lentil (Masoor), Chickpea, Linseed, Safflower, Fenugreek (Methi), Coriander, Cumin, Potato, Onion, Garlic, Carrot, Radish, Spinach, Cauliflower, Cabbage, Broccoli, Beetroot, Turnip, Fennel (Saunf). DO NOT include any Kharif or Zaid crops.",
            "summer": "ONLY recommend ZAID / SUMMER season crops like Watermelon, Muskmelon, Cucumber, Moong (Green Gram), Urad, Sunflower, Groundnut (Summer), Sesame, Pumpkin, Bottle Gourd, Bitter Gourd, Ridge Gourd, Sponge Gourd, Okra (Lady Finger), Tomato, Brinjal, Capsicum, Maize (Summer), Cowpea (Lobia), Cluster Bean. DO NOT include any Kharif or Rabi crops.",
            "rainy": "ONLY recommend KHARIF / RAINY season crops like Rice (Paddy), Maize, Soybean, Cotton, Sugarcane, Bajra (Pearl Millet), Jowar (Sorghum), Arhar/Tur Dal, Urad (Kharif), Moong (Kharif), Groundnut, Sesame, Castor, Jute, Turmeric, Ginger, Chilli, Sorghum, Ragi, Foxtail Millet, Barnyard Millet. DO NOT include any Rabi or Zaid crops."
        }
        season_filter = season_map.get(season.lower(), "")

    lang_instr = """CRITICAL LANGUAGE REQUIREMENT:
The user is an Indian farmer using the app in HINDI.
All text descriptions (crop_name_hindi, suitability, season, best_planting_month, crop_age_stages, seed_quantity, soil_preparation_steps, fertilizer_schedule, irrigation_schedule, pesticide_needs, weed_management, expected_yield, expected_profit, benefits, drawbacks, growth_requirements, harvest_method, market_demand, description) MUST be in 100% PURE HINDI (Devanagari script). Keep crop_name in English.""" if is_hi else "All text descriptions must be in English."

    prompt = f"""You are an expert Indian agricultural scientist advising FARMERS for FIELD-LEVEL FARMING.

Analyze these {len(image_paths)} field photos with soil data to recommend 20-25 BEST FIELD CROPS.

SOIL DATA:
{soil_info}

{lang_instr}

{f"SEASON FILTER: {season_filter}" if season_filter else ""}

CRITICAL RULES:
- ONLY recommend FIELD CROPS grown on agricultural land/farms
{f"- {season_filter}" if season_filter else "- Include crops from all seasons (Kharif, Rabi, Zaid)"}
- DO NOT recommend pot/garden plants like tulsi, mint, ornamental flowers etc. Those belong in PLANTS section.
- Rate each crop: Excellent (best match for this soil), Good (grows well), Moderate (will produce)
- All benefits/drawbacks from FARMER perspective (profit, investment, labor, water, MSP, government support)
- Give as many crops as possible, minimum 20

Respond with ONLY a valid JSON array:
[
  {{
    "crop_name": "English Name",
    "crop_name_hindi": "हिंदी नाम (जैसे: गेहूं, चना, सरसों, धान, मक्का)",
    "suitability": "{"सर्वोत्तम / अच्छा / मध्यम" if is_hi else "Excellent / Good / Moderate"}",
    "season": "{"खरीफ / रबी / जायद / सभी मौसम" if is_hi else "Kharif / Rabi / Zaid / All Season"}",
    "best_planting_month": "{"अक्टूबर-नवंबर" if is_hi else "June-July"}",
    "growth_duration_days": 120,
    "crop_age_stages": "{"अंकुरण: 0-10 दिन, कल्ले फूटना: 10-35 दिन, बढ़वार: 35-70 दिन, बालियां: 70-90 दिन, परिपक्वता: 90-120 दिन" if is_hi else "Germination: 0-10 days, Tillering: 10-35 days, Vegetative: 35-70 days, Flowering: 70-90 days, Maturity: 90-120 days"}",
    "seed_quantity": "{"40-50 किग्रा प्रति एकड़" if is_hi else "40-50 kg per acre"}",
    "soil_preparation_steps": ["{"गहरी जुताई" if is_hi else "Deep ploughing"}", "{"पाटा लगाना" if is_hi else "Leveling"}", "{"5 टन/एकड़ गोबर खाद" if is_hi else "Add FYM 5 tonnes/acre"}"],
    "fertilizer_schedule": "{"बुवाई समय: 50 किग्रा डीएपी + 25 किग्रा पोटाश प्रति एकड़, टॉप ड्रेसिंग: 25 किग्रा यूरिया" if is_hi else "Basal: 50kg DAP + 25kg MOP/acre, Top dress: 25kg Urea at 25 DAS"}",
    "irrigation_schedule": "{"पहली सिंचाई 21 दिन पर (सीआरआई अवस्था), फिर 20-25 दिन के अंतराल पर कुल 4-5 सिंचाई" if is_hi else "First at 21 DAS, then every 20-25 days, total 5-6 irrigations"}",
    "pesticide_needs": "{"प्रमुख कीट, रोग और अनुमोदित कीटनाशक की मात्रा" if is_hi else "Common pests and pesticides with dosage"}",
    "weed_management": "{"खरपतवार नाशक का नाम और छिड़काव का सही समय" if is_hi else "Herbicide names and timing"}",
    "expected_yield": "{"18-22 क्विंटल प्रति एकड़" if is_hi else "18-22 quintals per acre"}",
    "expected_profit": "{"रु 25,000 - 35,000 प्रति एकड़" if is_hi else "Rs 25,000 - Rs 35,000 per acre"}",
    "benefits": ["{"कम लागत, उत्तम मुनाफा" if is_hi else "Low input cost, high return"}", "{"सरकारी एमएसपी उपलब्ध" if is_hi else "Government MSP available"}"],
    "drawbacks": ["{"अधिक सिंचाई की आवश्यकता" if is_hi else "Needs 6+ irrigations"}"],
    "growth_requirements": ["{"पर्याप्त धूप व उचित जल निकासी" if is_hi else "Adequate sunlight and good drainage"}"],
    "harvest_method": "{"कटाई की विधि व सही पहचान" if is_hi else "How to harvest and when ready"}",
    "market_demand": "{"स्थानीय मंडी में मांग व सरकारी न्यूनतम समर्थन मूल्य" if is_hi else "Market demand and MSP if applicable"}",
    "description": "{"इस मिट्टी में इस फसल की उपयोगिता व किसान भाईयों के लिए लाभ का विवरण" if is_hi else "3-4 line description about why this crop is best for the farmer"}"
  }}
]

All data for INDIAN farming. REALISTIC yield/profit. Specific product names and dosages. ONLY JSON array."""

    result = call_groq_json_array(
        prompt,
        images=image_paths,
        temperature=0.4,
        max_tokens=2500,
        timeout=120,
        tag="CropRecommendations",
    )

    if isinstance(result, dict) and "error" in result:
        return result
    return {"crops": result}


# ── Helper ───────────────────────────────────────────
def _format_soil_info(soil_data):
    """Format soil data dict into readable string."""
    return f"""Soil Type: {soil_data.get('soil_type','Unknown')}
pH Level: {soil_data.get('ph_level','Unknown')}
Health: {soil_data.get('soil_health','Unknown')} ({soil_data.get('health_score',0)}%)
Moisture: {soil_data.get('moisture_level','Unknown')}
Organic Matter: {soil_data.get('organic_matter','Unknown')}
Nitrogen: {soil_data.get('nitrogen_level','Unknown')}
Phosphorus: {soil_data.get('phosphorus_level','Unknown')}
Potassium: {soil_data.get('potassium_level','Unknown')}"""
