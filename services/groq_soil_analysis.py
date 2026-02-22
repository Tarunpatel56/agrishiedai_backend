"""
Soil Analysis Service
=====================
Uses groq_client for all API calls.
"""

from services.groq_client import call_groq_json_object, call_groq_json_array


# =====================================================
# 1. SOIL IMAGE ANALYSIS
# =====================================================
SOIL_PROMPT = """You are an expert agricultural soil scientist. Look at this image carefully.

IMPORTANT: First determine if this image actually shows SOIL or GROUND/EARTH. 
If the image is NOT soil (e.g. a person, animal, building, food, random object, selfie, document, text etc.), you MUST respond with:
{"is_soil": false, "error": "This is not a soil image. Please upload a clear photo of soil or ground."}

If it IS a soil image, respond with ONLY this JSON:
{
  "is_soil": true,
  "soil_type": "Clay / Sandy / Loamy / Silty / Peaty / Chalky / Laterite / Black Cotton / Red / Alluvial",
  "soil_type_hindi": "Hindi name of soil type",
  "ph_level": "estimated pH (e.g., Slightly Acidic - 6.0-6.5)",
  "soil_texture": "Fine-grained / Medium-grained / Coarse",
  "soil_color": "observed color",
  "soil_health": "Good / Fair / Poor",
  "health_score": 75,
  "moisture_level": "Dry / Moderate / Wet",
  "organic_matter": "Low / Medium / High",
  "composition": "detailed soil composition",
  "nitrogen_level": "Low / Medium / High",
  "phosphorus_level": "Low / Medium / High",
  "potassium_level": "Low / Medium / High",
  "advisory": "2-3 lines of practical improvement advice in English"
}

Respond with ONLY the JSON, no extra text."""


def analyze_soil_image(image_path):
    """Analyze a soil image using Groq Vision API."""
    result = call_groq_json_object(
        SOIL_PROMPT,
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
        return {"error": result.get("error", "This is not a soil image. Please upload a clear photo of soil.")}

    return result


# =====================================================
# 2. PLANT RECOMMENDATIONS (Pot / Gamla / Home Garden)
# =====================================================
def get_plant_recommendations(soil_data):
    """Get pot/garden plant recommendations based on soil data."""
    soil_info = _format_soil_info(soil_data)

    prompt = f"""You are an expert Indian horticulture and home gardening advisor.

Based on this soil analysis, recommend 20-25 PLANTS that can be grown in POTS, CONTAINERS, GAMLA, HOME GARDEN, TERRACE GARDEN or BALCONY.

{soil_info}

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
    "plant_name_hindi": "Hindi Name",
    "suitability": "Excellent / Good / Moderate",
    "plant_type": "Flower / Vegetable / Herb / Medicinal / Ornamental / Fruit",
    "growth_days": 90,
    "plant_age_info": "Seedling: 0-15 days, Vegetative: 15-45 days, Flowering: 45-75 days, Fruiting: 75-90 days",
    "sunlight_needs": "Full Sun - 6-8 hours daily",
    "water_needs": "Daily watering - 500ml per plant",
    "fertilizer_needs": "50g DAP per plant every 15 days",
    "soil_preparation": "How to prepare pot/gamla soil mix",
    "planting_method": "Step by step planting in pot/gamla",
    "care_steps": ["Step 1", "Step 2", "Step 3", "Step 4"],
    "common_diseases": "Common diseases and prevention",
    "harvest_info": "When and how to harvest or enjoy",
    "benefits": ["Easy to grow in gamla", "Saves money on vegetables", "Good for health"],
    "best_season": "October-November (Rabi)",
    "difficulty_level": "Easy / Medium / Hard",
    "description": "2-3 lines about this plant for home/pot growing"
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
def get_crop_recommendations(soil_data, image_paths, season=None):
    """Get field crop recommendations using soil data + field photos."""
    if len(image_paths) < 3:
        return {"error": "Minimum 3 field photos required"}

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

    prompt = f"""You are an expert Indian agricultural scientist advising FARMERS for FIELD-LEVEL FARMING.

Analyze these {len(image_paths)} field photos with soil data to recommend 20-25 BEST FIELD CROPS.

SOIL DATA:
{soil_info}

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
    "crop_name_hindi": "Hindi Name",
    "suitability": "Excellent / Good / Moderate",
    "season": "Kharif / Rabi / Zaid / All Season",
    "best_planting_month": "June-July",
    "growth_duration_days": 120,
    "crop_age_stages": "Germination: 0-10 days, Tillering: 10-35 days, Vegetative: 35-70 days, Flowering: 70-90 days, Maturity: 90-120 days",
    "seed_quantity": "40-50 kg per acre",
    "soil_preparation_steps": ["Deep ploughing", "Leveling", "Add FYM 5 tonnes/acre"],
    "fertilizer_schedule": "Basal: 50kg DAP + 25kg MOP/acre, Top dress: 25kg Urea at 25 DAS",
    "irrigation_schedule": "First at 21 DAS, then every 20-25 days, total 5-6 irrigations",
    "pesticide_needs": "Common pests and pesticides with dosage",
    "weed_management": "Herbicide names and timing",
    "expected_yield": "18-22 quintals per acre",
    "expected_profit": "Rs 25,000 - Rs 35,000 per acre",
    "benefits": ["Farmer advantage - e.g. Low input cost, high return", "Government MSP available", "Improves soil nitrogen"],
    "drawbacks": ["Farmer disadvantage - e.g. Needs 6+ irrigations", "Pest prone in monsoon"],
    "growth_requirements": ["Requirement 1", "Requirement 2", "Requirement 3"],
    "harvest_method": "How to harvest and when ready",
    "market_demand": "Market demand and MSP if applicable",
    "description": "3-4 line description about why this crop is best for the farmer"
  }}
]

All data for INDIAN farming. REALISTIC yield/profit. Specific product names and dosages. ONLY JSON array."""

    result = call_groq_json_array(
        prompt,
        images=image_paths,
        temperature=0.4,
        max_tokens=8192,
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
