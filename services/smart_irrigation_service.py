import os
import json
from datetime import datetime, timedelta
import requests

IRRIGATION_HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "project_data", "irrigation_history.json"
)

# FAO-56 Crop Coefficients (Kc) across growth stages: [Initial, Development, Mid-Season, Late]
CROP_COEFFICIENTS = {
    "Wheat": {"initial": 0.35, "dev": 0.75, "mid": 1.15, "late": 0.45, "root_depth_m": 1.0, "total_days": 125},
    "Soybean": {"initial": 0.40, "dev": 0.80, "mid": 1.15, "late": 0.50, "root_depth_m": 0.8, "total_days": 105},
    "Rice": {"initial": 1.05, "dev": 1.15, "mid": 1.20, "late": 0.90, "root_depth_m": 0.6, "total_days": 120},
    "Cotton": {"initial": 0.35, "dev": 0.75, "mid": 1.20, "late": 0.65, "root_depth_m": 1.2, "total_days": 160},
    "Maize": {"initial": 0.30, "dev": 0.75, "mid": 1.20, "late": 0.55, "root_depth_m": 1.0, "total_days": 110},
    "Mustard": {"initial": 0.35, "dev": 0.75, "mid": 1.10, "late": 0.45, "root_depth_m": 0.9, "total_days": 115},
    "Gram": {"initial": 0.40, "dev": 0.70, "mid": 1.00, "late": 0.35, "root_depth_m": 0.8, "total_days": 100},
    "Chickpea": {"initial": 0.40, "dev": 0.70, "mid": 1.00, "late": 0.35, "root_depth_m": 0.8, "total_days": 100},
    "Sugarcane": {"initial": 0.40, "dev": 0.80, "mid": 1.25, "late": 0.75, "root_depth_m": 1.2, "total_days": 330},
    "Potato": {"initial": 0.50, "dev": 0.75, "mid": 1.15, "late": 0.75, "root_depth_m": 0.6, "total_days": 95},
    "Tomato": {"initial": 0.60, "dev": 0.80, "mid": 1.15, "late": 0.80, "root_depth_m": 0.7, "total_days": 120},
    "General": {"initial": 0.40, "dev": 0.75, "mid": 1.10, "late": 0.50, "root_depth_m": 0.8, "total_days": 110}
}

# Soil Available Water Capacity (AWC in mm water per meter soil depth)
SOIL_AWC = {
    "Black Cotton (काली मिट्टी)": 200,
    "Black Cotton": 200,
    "Clay": 190,
    "Clay Loam (दोमट मिट्टी)": 165,
    "Clay Loam": 165,
    "Loam": 150,
    "Sandy Loam (बलुई दोमट)": 115,
    "Sandy Loam": 115,
    "Red Soil (लाल मिट्टी)": 125,
    "Red Soil": 125,
    "Sandy": 75,
}


def _determine_growth_stage(sowing_date_str, total_days):
    """Determine crop growth stage based on Days After Sowing (DAS)."""
    try:
        sow_dt = datetime.fromisoformat(sowing_date_str.split("T")[0])
        das = max(1, (datetime.now() - sow_dt).days)
    except Exception:
        das = 45

    p1 = int(total_days * 0.18)  # Initial stage
    p2 = int(total_days * 0.45)  # Development
    p3 = int(total_days * 0.80)  # Mid-Season
    # Remainder is late stage

    if das <= p1:
        return "Initial (प्रारंभिक अवस्था)", "initial", das
    elif das <= p2:
        return "Crop Development (वानस्पतिक विकास)", "dev", das
    elif das <= p3:
        return "Mid-Season / Flowering (पुष्पन एवं दाना भराव)", "mid", das
    else:
        return "Late / Maturation (परिपक्वता अवस्था)", "late", das


def calculate_irrigation_advice(field_data, last_irrigation_date=None, method="Flood"):
    """
    Computes scientific, transparent irrigation advisory adhering strictly to FAO-56.
    Zero IoT hardware or physical sensors required.
    """
    crop = field_data.get("crop_type", "Wheat")
    crop_info = CROP_COEFFICIENTS.get(crop, CROP_COEFFICIENTS["General"])

    sowing_date = field_data.get("sowing_date", (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d"))
    soil_type = field_data.get("soil_type", "Black Cotton (काली मिट्टी)")
    area_acres = float(field_data.get("area_acres", 2.5))
    lat = float(field_data.get("latitude", 22.7196))
    lon = float(field_data.get("longitude", 75.8577))

    # 1. Growth Stage & Kc
    stage_name, stage_key, das = _determine_growth_stage(sowing_date, crop_info["total_days"])
    kc = crop_info[stage_key]

    # Root depth adjusts as crop develops
    root_ratio = min(1.0, max(0.3, das / (crop_info["total_days"] * 0.6)))
    effective_root_depth = round(crop_info["root_depth_m"] * root_ratio, 2)

    # 2. Soil Water Parameters
    awc = SOIL_AWC.get(soil_type, 160)
    taw = round(awc * effective_root_depth, 1)  # Total Available Water (mm)
    mad = 0.50  # Management Allowed Depletion (50%)
    raw = round(taw * mad, 1)  # Readily Available Water (mm)

    # 3. Fetch Real Weather (ET0 and Precipitation) from Open-Meteo
    et0_7d = [4.5] * 7
    rain_7d = [0.0] * 7
    forecast_dates = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&"
            f"daily=et0_fao_evapotranspiration,precipitation_sum&"
            f"timezone=Asia/Kolkata&forecast_days=7"
        )
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            d = r.json().get("daily", {})
            et0_7d = [round(x, 1) if x is not None else 4.2 for x in d.get("et0_fao_evapotranspiration", et0_7d)]
            rain_7d = [round(x, 1) if x is not None else 0.0 for x in d.get("precipitation_sum", rain_7d)]
            forecast_dates = d.get("time", forecast_dates)
    except Exception as e:
        print(f"[IrrigationService] Weather query notice: {e}")

    # 4. Water Balance over past days since last irrigation
    if not last_irrigation_date:
        # Default assumption: irrigated 8 days ago
        days_since_last_irrigation = 8
        last_irrigation_str = (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d")
    else:
        try:
            l_dt = datetime.fromisoformat(last_irrigation_date.split("T")[0])
            days_since_last_irrigation = max(0, (datetime.now() - l_dt).days)
            last_irrigation_str = l_dt.strftime("%Y-%m-%d")
        except Exception:
            days_since_last_irrigation = 7
            last_irrigation_str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    # Daily crop water need: ETc = Kc * ET0
    today_et0 = et0_7d[0] if et0_7d else 4.5
    daily_etc = round(kc * today_et0, 2)

    # Estimate accumulated moisture deficit (mm)
    # Average past daily deficit approx daily_etc
    accumulated_deficit = round(min(taw, days_since_last_irrigation * daily_etc), 1)

    # Effective Rainfall in next 3 days
    rain_next_3d = sum(rain_7d[:3])
    rain_next_7d = sum(rain_7d)

    # 5. Recommendation Decision Logic
    is_rain_sufficient = (rain_next_3d >= accumulated_deficit * 0.7 and rain_next_3d >= 15.0)

    if is_rain_sufficient:
        urgency = "Hold Irrigation (वर्षा की संभावना - रोकें)"
        urgency_code = "HOLD_RAIN"
        color = "#1565C0"
        advice_en = f"Rainfall of ~{round(rain_next_3d, 1)} mm is forecasted within 72 hours. Postpone irrigation to avoid waterlogging and conserve water."
        advice_hi = f"अगले 72 घंटों में लगभग {round(rain_next_3d, 1)} मिमी वर्षा का अनुमान है। जलभराव से बचने और पानी बचाने हेतु सिंचाई रोकें।"
        recommended_depth_mm = 0.0
    elif accumulated_deficit >= raw * 0.85:
        urgency = "Irrigate Within 24-48 Hours (तुरंत/शीघ्र सिंचाई करें)"
        urgency_code = "IRRIGATE_SOON"
        color = "#D32F2F"
        recommended_depth_mm = round(min(55.0, max(30.0, accumulated_deficit)), 1)
        advice_en = f"Soil moisture depletion has reached ~{accumulated_deficit} mm ({round(accumulated_deficit/taw*100)}% of capacity). Critical root zone needs moisture."
        advice_hi = f"मिट्टी में नमी की कमी {accumulated_deficit} मिमी तक पहुंच गई है। फसल को तनाव से बचाने हेतु 24-48 घंटों में सिंचाई दें।"
    elif accumulated_deficit >= raw * 0.50:
        urgency = "Moderate Moisture — Plan in 3-5 Days (3-5 दिनों में सिंचाई करें)"
        urgency_code = "PLAN_SOON"
        color = "#F57C00"
        recommended_depth_mm = round(accumulated_deficit, 1)
        advice_en = f"Soil retains adequate moisture for ~3-4 days. Plan next watering cycle before vegetative stress begins."
        advice_hi = f"खेत में अभी 3-4 दिन पर्याप्त नमी है। फसल में तनाव आने से पहले अगले चक्र की तैयारी रखें।"
    else:
        urgency = "Adequate Moisture (पर्याप्त नमी मौजूद है)"
        urgency_code = "SUFFICIENT"
        color = "#2E7D32"
        recommended_depth_mm = 0.0
        advice_en = f"Root zone moisture is sufficient. No irrigation required today."
        advice_hi = f"जड़ क्षेत्र में अभी पर्याप्त नमी है। आज सिंचाई की आवश्यकता नहीं है।"

    # 6. Water Volume Calculations for Field Area
    # Area in square meters = acres * 4046.856
    area_sqm = area_acres * 4046.856
    # 1 mm depth over 1 sq meter = 1 Liter = 0.001 m³
    volume_liters = round(area_sqm * recommended_depth_mm)
    volume_m3 = round(volume_liters / 1000.0, 1)

    # Estimate pump running hours for 5 HP electric pump (~36,000 L/hour)
    pump_hours = round(volume_liters / 36000.0, 1) if volume_liters > 0 else 0.0

    # 7. Next 7-Day Irrigation Schedule Table
    daily_schedule = []
    running_deficit = accumulated_deficit
    for i in range(len(forecast_dates)):
        day_date = forecast_dates[i]
        d_et0 = et0_7d[i] if i < len(et0_7d) else 4.2
        d_etc = round(kc * d_et0, 2)
        d_rain = rain_7d[i] if i < len(rain_7d) else 0.0
        # USDA effective rain formula approximation
        d_peff = round(d_rain * 0.8, 1) if d_rain < 25 else round(d_rain * 0.65, 1)

        running_deficit = round(max(0.0, min(taw, running_deficit + d_etc - d_peff)), 1)
        action = "Wait / Monitor"
        action_hi = "निगरानी रखें"
        if d_rain >= 10.0:
            action = f"Rain ({d_rain} mm) - No Water"
            action_hi = f"वर्षा ({d_rain} मिमी) - सिंचाई न करें"
        elif running_deficit >= raw * 0.85:
            action = "Recommended Irrigation Window"
            action_hi = "अनुकूल सिंचाई समय"

        daily_schedule.append({
            "date": day_date,
            "day_name": datetime.fromisoformat(day_date).strftime("%a"),
            "et0_mm": d_et0,
            "etc_mm": d_etc,
            "forecast_rain_mm": d_rain,
            "projected_deficit_mm": running_deficit,
            "action": action,
            "action_hi": action_hi
        })

    return {
        "status": "Success",
        "field_id": field_data.get("id"),
        "field_name": field_data.get("name"),
        "crop_type": crop,
        "sowing_date": sowing_date,
        "soil_type": soil_type,
        "area_acres": area_acres,
        "growth_stage": {
            "stage_name": stage_name,
            "stage_key": stage_key,
            "days_after_sowing": das,
            "crop_coefficient_kc": kc,
            "effective_root_depth_m": effective_root_depth
        },
        "soil_moisture_balance": {
            "soil_awc_mm_per_m": awc,
            "total_available_water_taw_mm": taw,
            "readily_available_water_raw_mm": raw,
            "estimated_accumulated_deficit_mm": accumulated_deficit,
            "days_since_last_irrigation": days_since_last_irrigation,
            "last_irrigation_date": last_irrigation_str
        },
        "recommendation": {
            "urgency": urgency,
            "urgency_code": urgency_code,
            "status_color": color,
            "advice_en": advice_en,
            "advice_hi": advice_hi,
            "recommended_depth_mm": recommended_depth_mm,
            "water_volume_liters": volume_liters,
            "water_volume_m3": volume_m3,
            "estimated_pump_hours_5hp": pump_hours,
            "application_method": method
        },
        "schedule_7d": daily_schedule,
        "scientific_basis": {
            "standard": "FAO Irrigation and Drainage Paper No. 56 (FAO-56 Penman-Monteith)",
            "calculation_formula": "ETc = Kc * ET0; Net Irrigation Requirement = ETc - Peff",
            "no_iot_notice": "Calculated entirely using public agro-meteorological data, soil physics, and crop coefficients without physical IoT probes."
        }
    }


def get_irrigation_logs(field_id=None):
    """Retrieve logged irrigation events."""
    if not os.path.exists(IRRIGATION_HISTORY_FILE):
        return []
    try:
        with open(IRRIGATION_HISTORY_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
            if field_id:
                logs = [l for l in logs if l.get("field_id") == field_id]
            return logs
    except Exception as e:
        print(f"[IrrigationService] Error loading logs: {e}")
        return []


def log_irrigation_event(data):
    """Save an actual irrigation event performed by the farmer."""
    os.makedirs(os.path.dirname(IRRIGATION_HISTORY_FILE), exist_ok=True)
    logs = get_irrigation_logs()
    new_log = {
        "id": f"irrig_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "field_id": data.get("field_id", ""),
        "field_name": data.get("field_name", ""),
        "crop_type": data.get("crop_type", ""),
        "irrigation_date": data.get("irrigation_date", datetime.now().strftime("%Y-%m-%d")),
        "depth_mm": float(data.get("depth_mm", 40.0)),
        "method": data.get("method", "Flood (नाली द्वारा)"),
        "notes": data.get("notes", ""),
        "created_at": datetime.now().isoformat()
    }
    logs.insert(0, new_log)
    with open(IRRIGATION_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(logs[:50], f, indent=2, ensure_ascii=False)
    return new_log

