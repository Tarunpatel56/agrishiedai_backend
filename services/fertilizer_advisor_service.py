"""
Fertilizer Prescription & Nutrient Advisor Service
===================================================
Calculates defensible, scientific fertilizer requirements based on ICAR
Recommended Dose of Fertilizers (RDF), Soil Test Crop Response (STCR) calibrations,
and conversion into standard commercial Indian fertilizers (Urea 45kg bags, DAP 50kg bags, MOP 50kg bags).

CRITICAL RULES:
- Never invents arbitrary doses or random NPK values.
- Strictly distinguishes between pure nutrient kg (N, P2O5, K2O) and commercial fertilizer product quantities.
- Explains calculation basis, area scaling, application timing, and soil testing gaps.
"""

import math

# ICAR Standard Recommended Dose of Fertilizer (RDF) in kg/acre for irrigated conditions
# (N : P2O5 : K2O in kg per acre)
ICAR_CROP_RDF = {
    "wheat": {"n": 48.0, "p": 24.0, "k": 16.0, "source": "ICAR-IIWBR Karnal", "splits": 3},
    "rice": {"n": 40.0, "p": 20.0, "k": 20.0, "source": "ICAR-NRRI Cuttack", "splits": 3},
    "paddy": {"n": 40.0, "p": 20.0, "k": 20.0, "source": "ICAR-NRRI Cuttack", "splits": 3},
    "maize": {"n": 48.0, "p": 24.0, "k": 16.0, "source": "ICAR-IIMR Ludhiana", "splits": 3},
    "soybean": {"n": 8.0, "p": 24.0, "k": 16.0, "source": "ICAR-IISR Indore (Rhizobium inoculated)", "splits": 1},
    "cotton": {"n": 48.0, "p": 24.0, "k": 24.0, "source": "ICAR-CICR Nagpur", "splits": 3},
    "mustard": {"n": 32.0, "p": 16.0, "k": 16.0, "source": "ICAR-DRMR Bharatpur", "splits": 2},
    "chickpea": {"n": 8.0, "p": 20.0, "k": 8.0, "source": "ICAR-IIPR Kanpur", "splits": 1},
    "gram": {"n": 8.0, "p": 20.0, "k": 8.0, "source": "ICAR-IIPR Kanpur", "splits": 1},
    "potato": {"n": 60.0, "p": 40.0, "k": 48.0, "source": "ICAR-CPRI Shimla", "splits": 2},
    "tomato": {"n": 48.0, "p": 32.0, "k": 24.0, "source": "ICAR-IIHR Bengaluru", "splits": 3},
    "onion": {"n": 40.0, "p": 20.0, "k": 20.0, "source": "ICAR-DOGR Pune", "splits": 3},
    "sugarcane": {"n": 100.0, "p": 40.0, "k": 48.0, "source": "ICAR-IISR Lucknow", "splits": 4},
    "general": {"n": 40.0, "p": 20.0, "k": 20.0, "source": "ICAR Standard Guidelines", "splits": 2}
}

# Unit multipliers to convert to acres
UNIT_TO_ACRE = {
    "acre": 1.0,
    "hectare": 2.47105,
    "bigha": 0.40,      # Central India standard (approx 0.40 acre)
    "guntha": 0.025,
    "sq_meter": 0.000247
}


def calculate_fertilizer_prescription(
    crop_name: str,
    farm_area: float,
    area_unit: str = "acre",
    growth_stage: str = "Basal / Sowing",
    soil_type: str = "Loamy",
    soil_test_n: str = None,   # "Low", "Medium", "High"
    soil_test_p: str = None,
    soil_test_k: str = None,
    irrigation_type: str = "Irrigated",
    language: str = "en"
) -> dict:
    """
    Computes precise, defensible nutrient requirements and translates into
    commercial fertilizer products (Urea, DAP, MOP) with timing and splits.
    """
    if farm_area <= 0:
        return {"error": "Farm area must be greater than zero."}

    crop_key = crop_name.lower().strip()
    rdf = ICAR_CROP_RDF.get(crop_key, ICAR_CROP_RDF["general"])

    # Convert area to acres
    multiplier = UNIT_TO_ACRE.get(area_unit.lower().strip(), 1.0)
    area_in_acres = farm_area * multiplier

    base_n = rdf["n"] * area_in_acres
    base_p = rdf["p"] * area_in_acres
    base_k = rdf["k"] * area_in_acres

    # Adjust for Rainfed conditions (-25% nutrient dose)
    if "rainfed" in irrigation_type.lower():
        base_n *= 0.75
        base_p *= 0.75
        base_k *= 0.75

    # STCR (Soil Test Crop Response) adjustment factors:
    # Low: +25%, Medium: 0%, High: -25%
    def _adjust(factor_str):
        if not factor_str:
            return 1.0
        f = factor_str.lower()
        if "low" in f:
            return 1.25
        elif "high" in f:
            return 0.75
        return 1.0

    adj_n = base_n * _adjust(soil_test_n)
    adj_p = base_p * _adjust(soil_test_p)
    adj_k = base_k * _adjust(soil_test_k)

    # ── Product Conversions ──
    # Commercial Fertilizer Composition in India:
    # DAP: 18% N, 46% P2O5 (50 kg bag)
    # Urea: 46% N (45 kg bag as per Govt of India neem-coated standard)
    # MOP: 60% K2O (50 kg bag)
    dap_kg = adj_p / 0.46
    dap_n_supplied = dap_kg * 0.18
    remaining_n = max(0.0, adj_n - dap_n_supplied)
    urea_kg = remaining_n / 0.46
    mop_kg = adj_k / 0.60

    # Bag calculations
    dap_bags = round(dap_kg / 50.0, 1)
    urea_bags = round(urea_kg / 45.0, 1)
    mop_bags = round(mop_kg / 50.0, 1)

    has_soil_test = bool(soil_test_n or soil_test_p or soil_test_k)

    # Split Application Schedules based on ICAR recommendations
    splits = rdf.get("splits", 2)
    if splits == 1:
        # Legumes / Soybean: 100% at basal
        schedule = [
            {
                "stage": "Basal Dose (At Sowing)",
                "stage_hi": "बुवाई के समय (बेसल डोज)",
                "timing": "Apply at the time of seed sowing in furrows",
                "timing_hi": "बुवाई के समय कूड़ों में बीज से नीचे दें",
                "urea_kg": round(urea_kg, 1),
                "dap_kg": round(dap_kg, 1),
                "mop_kg": round(mop_kg, 1),
                "notes": "Legume crop fixes atmospheric nitrogen through rhizobium nodules."
            }
        ]
    elif splits == 2:
        # Mustard / Potato
        schedule = [
            {
                "stage": "Basal Dose (At Sowing / Planting)",
                "stage_hi": "बुवाई / रोपाई के समय (बेसल डोज)",
                "timing": "At final land preparation or sowing",
                "timing_hi": "खेत की अंतिम जुताई या बुवाई के समय",
                "urea_kg": round(urea_kg * 0.5, 1),
                "dap_kg": round(dap_kg, 1),
                "mop_kg": round(mop_kg, 1),
                "notes": "Full DAP and MOP with 50% of Urea."
            },
            {
                "stage": "Top Dressing (Vegetative / 30-35 days)",
                "stage_hi": "पहली टॉप ड्रेसिंग (30-35 दिन बाद)",
                "timing": "After 1st irrigation / weeding",
                "timing_hi": "पहली सिंचाई या निराई-गुड़ाई के बाद",
                "urea_kg": round(urea_kg * 0.5, 1),
                "dap_kg": 0.0,
                "mop_kg": 0.0,
                "notes": "Broadcast remaining 50% Urea when soil is moist."
            }
        ]
    else:
        # Wheat / Rice / Maize / Cotton / Tomato
        schedule = [
            {
                "stage": "Basal Application (At Sowing / Transplanting)",
                "stage_hi": "बुवाई / रोपाई के समय (बेसल डोज)",
                "timing": "Before sowing, broadcast and incorporate into soil",
                "timing_hi": "बुवाई से ठीक पूर्व मिट्टी में अच्छी तरह मिलाएं",
                "urea_kg": round(urea_kg * 0.33, 1),
                "dap_kg": round(dap_kg, 1),
                "mop_kg": round(mop_kg, 1),
                "notes": "Full P (DAP), Full K (MOP), and 1/3rd of total Urea."
            },
            {
                "stage": "1st Top Dressing (Crown Root / Tillering Stage - 20-25 days)",
                "stage_hi": "पहली टॉप ड्रेसिंग (कल्ले फूटते समय - 20-25 दिन)",
                "timing": "Immediately after 1st irrigation",
                "timing_hi": "पहली सिंचाई (सीआरआई अवस्था) के बाद नमी में",
                "urea_kg": round(urea_kg * 0.33, 1),
                "dap_kg": 0.0,
                "mop_kg": 0.0,
                "notes": "Broadcast 1/3rd Urea in field."
            },
            {
                "stage": "2nd Top Dressing (Jointing / Panicle Stage - 45-55 days)",
                "stage_hi": "दूसरी टॉप ड्रेसिंग (गाभा / बाली बनते समय - 45-55 दिन)",
                "timing": "Before flowering / booting irrigation",
                "timing_hi": "बालियां निकलने से पूर्व सिंचाई के साथ",
                "urea_kg": round(urea_kg * 0.34, 1),
                "dap_kg": 0.0,
                "mop_kg": 0.0,
                "notes": "Broadcast remaining 1/3rd Urea."
            }
        ]

    return {
        "crop_name": crop_name,
        "farm_area": farm_area,
        "area_unit": area_unit,
        "area_in_acres": round(area_in_acres, 2),
        "soil_type": soil_type,
        "irrigation_type": irrigation_type,
        "has_soil_test": has_soil_test,
        "pure_nutrients_required": {
            "nitrogen_kg": round(adj_n, 1),
            "phosphate_p2o5_kg": round(adj_p, 1),
            "potash_k2o_kg": round(adj_k, 1),
            "unit": "kg"
        },
        "commercial_fertilizers": {
            "urea_46_n": {
                "quantity_kg": round(urea_kg, 1),
                "bags_45kg": urea_bags,
                "product_name": "Neem Coated Urea (46% N)",
                "product_name_hi": "नीम लेपित यूरिया (46% N)"
            },
            "dap_18_46_0": {
                "quantity_kg": round(dap_kg, 1),
                "bags_50kg": dap_bags,
                "product_name": "Di-Ammonium Phosphate / DAP (18% N, 46% P₂O₅)",
                "product_name_hi": "डीएपी (18% N, 46% P₂O₅)"
            },
            "mop_0_0_60": {
                "quantity_kg": round(mop_kg, 1),
                "bags_50kg": mop_bags,
                "product_name": "Muriate of Potash / MOP (60% K₂O)",
                "product_name_hi": "म्यूरेट ऑफ पोटाश (60% K₂O)"
            }
        },
        "application_schedule": schedule,
        "micronutrient_advice": "For cereals and oilseeds, apply Zinc Sulphate 21% @ 10 kg/acre or 33% @ 6 kg/acre as basal for optimal zinc nutrition.",
        "micronutrient_advice_hi": "जिंक की कमी से बचाव हेतु जिंक सल्फेट 21% (10 किग्रा/एकड़) या 33% (6 किग्रा/एकड़) बेसल डोज के साथ दें।",
        "calculation_basis": f"Calculated using {rdf['source']} Recommended Dose of Fertilizers (RDF) scaled to {farm_area} {area_unit}.",
        "calculation_basis_hi": f"{rdf['source']} की मानक संस्तुति के आधार पर {farm_area} {area_unit} के लिए वैज्ञानिक गणना।",
        "laboratory_soil_test_needed": not has_soil_test,
        "soil_test_recommendation": (
            "No chemical laboratory soil test values were provided. This prescription uses regional benchmark RDF. "
            "Farmers are strongly advised to obtain an official Soil Health Card test for precision dosage."
            if not has_soil_test else
            "Prescription customized with farmer's soil fertility test ratings."
        ),
        "soil_test_recommendation_hi": (
            "कोई रासायनिक मिट्टी जांच रिपोर्ट नहीं दी गई है। यह संस्तुति मानक आईसीएआर पैकेज पर आधारित है। "
            "सटीक बचत हेतु नजदीकी प्रयोगशाला से मृदा स्वास्थ्य कार्ड (Soil Health Card) अवश्य बनवाएं।"
            if not has_soil_test else
            "किसान की मिट्टी परीक्षण रिपोर्ट के आधार पर समायोजित संस्तुति।"
        )
    }
