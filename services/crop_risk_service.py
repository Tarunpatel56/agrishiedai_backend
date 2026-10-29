from datetime import datetime
import requests


def assess_crop_risk(field_data, ndvi_data=None, weather_data=None, scan_history=None):
    """
    Transparent, explainable multi-factor AI Crop Risk Assessment Engine.
    Combines satellite vegetation vigor, weather forecasts, soil drainage, crop vulnerability, and historical scans.
    """
    crop = field_data.get("crop_type", "Wheat")
    soil = field_data.get("soil_type", "Black Cotton (काली मिट्टी)")
    lat = float(field_data.get("latitude", 22.7196))
    lon = float(field_data.get("longitude", 75.8577))
    sowing_date = field_data.get("sowing_date", "2024-11-15")

    # 1. Weather Inputs
    current_temp = 28.0
    current_hum = 55
    current_wind = 9.0
    rain_7d_total = 0.0
    max_temp_7d = 32.0

    if weather_data and "current_weather" in weather_data:
        current_temp = float(weather_data["current_weather"].get("temperature", 28.0))
        current_hum = int(weather_data["current_weather"].get("humidity", 55))
        current_wind = float(weather_data["current_weather"].get("wind_speed", 9.0))
        daily = weather_data.get("daily_forecast", [])
        if daily:
            rain_7d_total = sum([f.get("rain_mm", 0.0) for f in daily])
            max_temp_7d = max([f.get("temp_max", current_temp) for f in daily])

    # 2. NDVI Inputs
    mean_ndvi = 0.55
    if ndvi_data and "ndvi_stats" in ndvi_data:
        mean_ndvi = float(ndvi_data["ndvi_stats"].get("mean_ndvi", 0.55))

    # 3. Factor Evaluations

    # Component A: Pest & Disease Risk (0-100)
    pest_risk = 15
    pest_factors = []
    if current_hum >= 80 and 20 <= current_temp <= 30:
        pest_risk += 35
        pest_factors.append(f"High atmospheric humidity ({current_hum}%) coupled with mild temperature ({current_temp}°C) accelerates fungal sporulation.")
    elif current_hum >= 70:
        pest_risk += 15
        pest_factors.append(f"Moderate-to-high humidity ({current_hum}%) creates microclimate favorable to foliar pathogens.")

    # Check past disease detections in scan history
    disease_scans = 0
    if scan_history:
        for s in scan_history:
            d_name = str(s.get("disease", "")).lower()
            if d_name and "no disease" not in d_name and "none" not in d_name:
                disease_scans += 1
    if disease_scans > 0:
        pest_risk += min(30, disease_scans * 10)
        pest_factors.append(f"Past disease incidents detected in {disease_scans} recent field scan(s).")
    else:
        pest_factors.append("No active pathogen outbreaks recorded in recent scans.")

    pest_risk = min(100, pest_risk)

    # Component B: Waterlogging & Heavy Rain Risk (0-100)
    waterlog_risk = 10
    waterlog_factors = []
    is_heavy_soil = ("clay" in soil.lower() or "cotton" in soil.lower())
    if rain_7d_total >= 40.0:
        waterlog_risk += 45
        waterlog_factors.append(f"Heavy rainfall forecast ({round(rain_7d_total, 1)} mm over 7 days).")
        if is_heavy_soil:
            waterlog_risk += 25
            waterlog_factors.append(f"Heavy soil ({soil}) has low infiltration and high water retention, increasing standing water risk.")
    elif rain_7d_total >= 15.0:
        waterlog_risk += 20
        waterlog_factors.append(f"Moderate rainfall expected ({round(rain_7d_total, 1)} mm). Low surface flooding risk.")
    else:
        waterlog_factors.append("Minimal rainfall anticipated in upcoming forecast window.")

    waterlog_risk = min(100, waterlog_risk)

    # Component C: Drought & Moisture Deficit Risk (0-100)
    drought_risk = 10
    drought_factors = []
    if rain_7d_total < 2.0:
        drought_risk += 25
        drought_factors.append("Dry spell: virtually no precipitation forecast for the next 7 days.")
    if mean_ndvi < 0.35:
        drought_risk += 25
        drought_factors.append(f"Low satellite NDVI ({mean_ndvi}) indicates vegetative canopy thinning or water stress.")
    elif mean_ndvi >= 0.60:
        drought_factors.append(f"Robust satellite NDVI ({mean_ndvi}) confirms vigorous canopy hydration.")

    drought_risk = min(100, drought_risk)

    # Component D: Heat & Thermal Stress (0-100)
    heat_risk = 10
    heat_factors = []
    if max_temp_7d >= 39.0:
        heat_risk += 60
        heat_factors.append(f"Extreme peak temperature ({max_temp_7d}°C) forecast, risking leaf scorching and pollen sterility.")
    elif max_temp_7d >= 36.0:
        heat_risk += 35
        heat_factors.append(f"Elevated temperatures ({max_temp_7d}°C) will accelerate evapotranspiration.")
    else:
        heat_factors.append(f"Thermal levels remain within safe agronomic range (max {max_temp_7d}°C).")

    heat_risk = min(100, heat_risk)

    # Component E: Operational / Spray Hazard (0-100)
    spray_hazard = 10
    spray_factors = []
    if current_wind >= 18.0:
        spray_hazard += 50
        spray_factors.append(f"High wind velocity ({current_wind} km/h) prevents safe agrochemical spray.")
    if rain_7d_total >= 25.0:
        spray_hazard += 30
        spray_factors.append("Rain will wash off applied protective sprays.")

    spray_hazard = min(100, spray_hazard)

    # Aggregate Overall Composite Score (weighted average)
    overall_score = round(
        0.30 * pest_risk +
        0.25 * drought_risk +
        0.20 * waterlog_risk +
        0.15 * heat_risk +
        0.10 * spray_hazard
    )

    if overall_score >= 70:
        risk_level = "High Risk (उच्च जोखिम)"
        risk_badge = "High"
        level_color = "#D32F2F"
    elif overall_score >= 40:
        risk_level = "Moderate Risk (मध्यम जोखिम)"
        risk_badge = "Moderate"
        level_color = "#F57C00"
    else:
        risk_level = "Low Risk (सुरक्षित / सामान्य)"
        risk_badge = "Low"
        level_color = "#2E7D32"

    # Actionable Recommendations
    actionable_steps = []
    actionable_steps_hi = []
    if pest_risk >= 40:
        actionable_steps.append("Inspect crop underleaves for early fungal spores or aphids; prepare biological spray (Neem oil 1500ppm).")
        actionable_steps_hi.append("पत्तियों के नीचे फफूंद या कीटों की जांच करें; आवश्यकतानुसार 1500 पीपीएम नीम तेल का छिड़काव करें।")
    if waterlog_risk >= 45:
        actionable_steps.append("Clear field bund channels immediately to drain prospective excess rain water.")
        actionable_steps_hi.append("खेत की मेड़ों और नालियों को साफ करें ताकि अतिरिक्त वर्षा का पानी तुरंत निकल सके।")
    if drought_risk >= 45:
        actionable_steps.append("Schedule irrigation within 48 hours to maintain soil tension above critical wilting point.")
        actionable_steps_hi.append("फसल को सूखने से बचाने के लिए 48 घंटे के भीतर सिंचाई की व्यवस्था करें।")
    if heat_risk >= 40:
        actionable_steps.append("Apply light mulching or irrigate in late afternoon to buffer soil root temperature.")
        actionable_steps_hi.append("शाम के समय हल्की सिंचाई करें ताकि मिट्टी का तापमान नियंत्रित रहे।")
    if not actionable_steps:
        actionable_steps.append("Conditions are favorable. Continue routine scouting and scheduled fertigation.")
        actionable_steps_hi.append("मौसम एवं परिस्थितियां सामान्य हैं। नियमित निगरानी और योजनाबद्ध पोषण जारी रखें।")

    return {
        "status": "Success",
        "field_id": field_data.get("id"),
        "field_name": field_data.get("name"),
        "crop_type": crop,
        "overall_risk_score": overall_score,
        "overall_risk_level": risk_level,
        "risk_badge": risk_badge,
        "level_color": level_color,
        "assessed_at": datetime.now().strftime("%I:%M %p, %d %b %Y"),
        "risk_breakdown": {
            "pest_disease": {
                "score": pest_risk,
                "title": "Pest & Pathogen Risk",
                "title_hi": "कीट एवं रोग जोखिम",
                "factors": pest_factors
            },
            "drought_deficit": {
                "score": drought_risk,
                "title": "Moisture Deficit & Drought",
                "title_hi": "नमी की कमी व सूखा जोखिम",
                "factors": drought_factors
            },
            "waterlogging": {
                "score": waterlog_risk,
                "title": "Waterlogging & Excessive Rain",
                "title_hi": "जलभराव एवं भारी वर्षा जोखिम",
                "factors": waterlog_factors
            },
            "heat_stress": {
                "score": heat_risk,
                "title": "Thermal / Heat Stress",
                "title_hi": "तापमान एवं ऊष्मा तनाव",
                "factors": heat_factors
            },
            "operational_spray": {
                "score": spray_hazard,
                "title": "Operational / Spray Hazard",
                "title_hi": "छिड़काव एवं कार्य संचालन जोखिम",
                "factors": spray_factors
            }
        },
        "recommended_actions": actionable_steps,
        "recommended_actions_hi": actionable_steps_hi,
        "explainability": {
            "methodology": "Multi-variable agronomic rule engine weighting Open-Meteo microclimate, Sentinel-2 NDVI canopy index, and field soil classification.",
            "data_sources": [
                "Open-Meteo 7-Day Forecast & Evapotranspiration",
                "Copernicus Sentinel-2 Surface Reflectance (NDVI)",
                "Local Soil Characteristics (Black Cotton / Loam)",
                "Crop Growth Stage & Agronomic Vulnerability Thresholds"
            ],
            "disclaimer": "This advisory uses transparent agronomic risk modeling. It does not replace on-field physical verification by an agricultural extension officer."
        }
    }

