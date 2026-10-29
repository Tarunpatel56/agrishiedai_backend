import os
import json
from datetime import datetime, timedelta

TASKS_STORE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "project_data", "crop_calendar_tasks.json"
)

# Standard ICAR Agronomic Crop Schedules (Days After Sowing — DAS)
CROP_AGRONOMIC_SCHEDULES = {
    "Wheat": {
        "duration_days": 125,
        "stages": [
            {"name": "Germination & Emergence", "name_hi": "अंकुरण अवस्था", "start_das": 0, "end_das": 10},
            {"name": "Crown Root Initiation (CRI)", "name_hi": "ताज जड़ निकलना (CRI)", "start_das": 20, "end_das": 25, "critical": True},
            {"name": "Tillering & Vegetative", "name_hi": "कल्ले फूटना (टिलरिंग)", "start_das": 35, "end_das": 45},
            {"name": "Jointing & Late Tillering", "name_hi": "गांठ बनना (ज्वाइंटिंग)", "start_das": 55, "end_das": 65},
            {"name": "Flowering & Anthesis", "name_hi": "पुष्पन एवं बाली निकलना", "start_das": 75, "end_das": 85, "critical": True},
            {"name": "Milking & Grain Filling", "name_hi": "दुग्धावस्था एवं दाना भराव", "start_das": 90, "end_das": 105},
            {"name": "Maturity & Harvesting", "name_hi": "परिपक्वता एवं कटाई", "start_das": 115, "end_das": 125}
        ],
        "tasks": [
            {"id": "w_01", "das": 0, "title": "Field Prep & Basal Fertilizer", "title_hi": "खेत की तैयारी एवं बेसल खाद", "desc": "Apply DAP (50 kg/acre) + MOP (20 kg/acre) + Zinc Sulphate (10 kg/acre) at sowing.", "category": "Fertilizer"},
            {"id": "w_02", "das": 21, "title": "1st Critical Irrigation (CRI Stage)", "title_hi": "प्रथम महत्वपूर्ण सिंचाई (CRI अवस्था)", "desc": "Crown roots develop at 20-25 DAS. Most critical watering to prevent yield penalty.", "category": "Irrigation"},
            {"id": "w_03", "das": 30, "title": "1st Top Dressing & Weeding", "title_hi": "प्रथम यूरिया टॉप ड्रेसिंग व खरपतवार नियंत्रण", "desc": "Broadcast Urea (35-40 kg/acre) after 1st irrigation once soil is workable.", "category": "Fertilizer"},
            {"id": "w_04", "das": 45, "title": "2nd Irrigation & Pest Scouting", "title_hi": "द्वितीय सिंचाई एवं कीट निगरानी", "desc": "Water at late tillering. Scout for early signs of yellow/brown rust.", "category": "Irrigation"},
            {"id": "w_05", "das": 60, "title": "2nd Top Dressing (Urea)", "title_hi": "द्वितीय यूरिया टॉप ड्रेसिंग", "desc": "Broadcast second split dose of Urea (30 kg/acre) before jointing.", "category": "Fertilizer"},
            {"id": "w_06", "das": 75, "title": "Flowering Irrigation & NPK Spray", "title_hi": "पुष्पन सिंचाई एवं 0:52:34 स्प्रे", "desc": "Maintain moisture. Foliar spray of NPK 00:52:34 (1 kg/acre) to boost grain size.", "category": "Nutrient"},
            {"id": "w_07", "das": 95, "title": "Grain Filling Light Irrigation", "title_hi": "दाना भराव हल्की सिंचाई", "desc": "Apply light irrigation on a calm day (avoid high wind to prevent lodging).", "category": "Irrigation"},
            {"id": "w_08", "das": 110, "title": "Stop All Irrigation", "title_hi": "सिंचाई पूर्णतः बंद करें", "desc": "Cease irrigation 10-14 days prior to harvest to allow grains to harden naturally.", "category": "Harvest"},
            {"id": "w_09", "das": 120, "title": "Harvesting & Threshing", "title_hi": "फसल कटाई एवं गहाई", "desc": "Harvest when grain moisture drops below 14% and spikes turn golden yellow.", "category": "Harvest"}
        ]
    },
    "Soybean": {
        "duration_days": 105,
        "stages": [
            {"name": "Germination & Seedling", "name_hi": "अंकुरण एवं नवोद्भिद", "start_das": 0, "end_das": 12},
            {"name": "Vegetative & Branching", "name_hi": "शाखाएं निकलना", "start_das": 20, "end_das": 35},
            {"name": "Flowering Stage", "name_hi": "फूल आने की अवस्था", "start_das": 40, "end_das": 55, "critical": True},
            {"name": "Pod Formation", "name_hi": "फलियां बनना (पॉड फॉर्मेशन)", "start_das": 60, "end_das": 75, "critical": True},
            {"name": "Pod Filling & Maturity", "name_hi": "दाना भराव व पकना", "start_das": 80, "end_das": 105}
        ],
        "tasks": [
            {"id": "s_01", "das": 0, "title": "Seed Treatment & Basal Dose", "title_hi": "बीजोपचार एवं बेसल खाद", "desc": "Inoculate seeds with Rhizobium culture. Apply SSP (100 kg/acre) at sowing.", "category": "Sowing"},
            {"id": "s_02", "das": 20, "title": "Weed Management & Interculture", "title_hi": "निंदाई-गुड़ाई व खरपतवार नियंत्रण", "desc": "First mechanical weeding or recommended pre/early post-emergent herbicide.", "category": "Weeding"},
            {"id": "s_03", "das": 45, "title": "Girdle Beetle / Semilooper Scouting", "title_hi": "गर्डल बीटल एवं इल्ली निगरानी", "desc": "Scout for defoliating caterpillars during flowering; use yellow sticky traps.", "category": "Protection"},
            {"id": "s_04", "das": 65, "title": "Pod Stage Moisture Check", "title_hi": "फली बनते समय नमी जांच", "desc": "If monsoon withdraws early, provide protective irrigation to ensure seed fill.", "category": "Irrigation"},
            {"id": "s_05", "das": 100, "title": "Harvesting", "title_hi": "फसल कटाई", "desc": "Harvest when 90% leaves shed and pods turn brownish grey.", "category": "Harvest"}
        ]
    },
    "General": {
        "duration_days": 110,
        "stages": [
            {"name": "Establishment", "name_hi": "जमाव अवस्था", "start_das": 0, "end_das": 15},
            {"name": "Vegetative Growth", "name_hi": "वानस्पतिक विकास", "start_das": 20, "end_das": 45},
            {"name": "Reproductive & Flowering", "name_hi": "पुष्पन अवस्था", "start_das": 50, "end_das": 75, "critical": True},
            {"name": "Maturity", "name_hi": "परिपक्वता", "start_das": 80, "end_das": 110}
        ],
        "tasks": [
            {"id": "g_01", "das": 0, "title": "Land Preparation & Sowing", "title_hi": "खेत तैयारी एवं बुवाई", "desc": "Deep plowing and balanced basal fertilization.", "category": "Sowing"},
            {"id": "g_02", "das": 25, "title": "First Irrigation & Weeding", "title_hi": "प्रथम सिंचाई व खरपतवार नियंत्रण", "desc": "Check root moisture and manage weeds.", "category": "Irrigation"},
            {"id": "g_03", "das": 55, "title": "Flower Initiation Care", "title_hi": "पुष्पन पोषण", "desc": "Ensure adequate soil moisture and monitor pest population.", "category": "Protection"},
            {"id": "g_04", "das": 105, "title": "Harvesting", "title_hi": "कटाई", "desc": "Harvest crop at physiological maturity.", "category": "Harvest"}
        ]
    }
}


def _load_task_states():
    if not os.path.exists(TASKS_STORE):
        return {}
    try:
        with open(TASKS_STORE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_task_states(states):
    os.makedirs(os.path.dirname(TASKS_STORE), exist_ok=True)
    with open(TASKS_STORE, "w", encoding="utf-8") as f:
        json.dump(states, f, indent=2, ensure_ascii=False)


def generate_crop_calendar(field_data):
    """
    Generate agronomic calendar with timeline, milestones, and tracked tasks.
    """
    crop = field_data.get("crop_type", "Wheat")
    schedule = CROP_AGRONOMIC_SCHEDULES.get(crop, CROP_AGRONOMIC_SCHEDULES["General"])

    sowing_date_str = field_data.get("sowing_date", (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
    try:
        sow_dt = datetime.fromisoformat(sowing_date_str.split("T")[0])
    except Exception:
        sow_dt = datetime.now() - timedelta(days=30)

    current_das = max(0, (datetime.now() - sow_dt).days)
    field_id = field_data.get("id", "default_field")

    # Load task completion states
    all_states = _load_task_states()
    field_task_states = all_states.get(field_id, {})

    # Calculate stages with dates
    stages_timeline = []
    current_stage_name = ""
    current_stage_name_hi = ""

    for st in schedule["stages"]:
        st_start_dt = sow_dt + timedelta(days=st["start_das"])
        st_end_dt = sow_dt + timedelta(days=st["end_das"])
        is_active = (st["start_das"] <= current_das <= st["end_das"])
        is_passed = (current_das > st["end_das"])

        if is_active:
            current_stage_name = st["name"]
            current_stage_name_hi = st["name_hi"]

        stages_timeline.append({
            "name": st["name"],
            "name_hi": st["name_hi"],
            "start_das": st["start_das"],
            "end_das": st["end_das"],
            "start_date": st_start_dt.strftime("%d %b %Y"),
            "end_date": st_end_dt.strftime("%d %b %Y"),
            "is_critical": st.get("critical", False),
            "is_active": is_active,
            "is_passed": is_passed
        })

    # Calculate tasks with dates
    tasks_list = []
    for t in schedule["tasks"]:
        task_dt = sow_dt + timedelta(days=t["das"])
        is_completed = bool(field_task_states.get(t["id"], False))
        is_overdue = (not is_completed and current_das > t["das"] + 3)
        is_upcoming = (t["das"] >= current_das)

        tasks_list.append({
            "id": t["id"],
            "das": t["das"],
            "title": t["title"],
            "title_hi": t["title_hi"],
            "description": t["desc"],
            "category": t["category"],
            "scheduled_date": task_dt.strftime("%d %b %Y"),
            "scheduled_iso": task_dt.strftime("%Y-%m-%d"),
            "is_completed": is_completed,
            "is_overdue": is_overdue,
            "is_upcoming": is_upcoming
        })

    # Estimated Harvest Window
    harvest_start_dt = sow_dt + timedelta(days=int(schedule["duration_days"] * 0.95))
    harvest_end_dt = sow_dt + timedelta(days=int(schedule["duration_days"] * 1.05))

    return {
        "status": "Success",
        "field_id": field_id,
        "field_name": field_data.get("name"),
        "crop_type": crop,
        "sowing_date": sow_dt.strftime("%d %B %Y"),
        "current_das": current_das,
        "total_crop_duration_days": schedule["duration_days"],
        "current_stage": {
            "name": current_stage_name or "Active Growth",
            "name_hi": current_stage_name_hi or "फसल विकास"
        },
        "estimated_harvest_window": {
            "start_date": harvest_start_dt.strftime("%d %b %Y"),
            "end_date": harvest_end_dt.strftime("%d %b %Y"),
            "note_en": "Estimated window based on standard thermal units and sowing date. Subject to weather conditions.",
            "note_hi": "मानक तापमान इकाइयों और बुवाई की तिथि पर आधारित अनुमानित अवधि। मौसम अनुसार परिवर्तन संभव।"
        },
        "stages": stages_timeline,
        "tasks": tasks_list,
        "attribution": {
            "reference": "ICAR Package of Practices & State Agricultural University Agronomy Manual",
            "compliance": "Standard Crop Phenology Guidelines"
        }
    }


def update_task_completion(field_id, task_id, is_completed):
    """Update checkbox state for a specific task in a field's calendar."""
    all_states = _load_task_states()
    if field_id not in all_states:
        all_states[field_id] = {}
    all_states[field_id][task_id] = bool(is_completed)
    _save_task_states(all_states)
    return True

