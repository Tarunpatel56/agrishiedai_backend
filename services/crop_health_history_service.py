import os
import json
from datetime import datetime

RECORDS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "project_data", "crop_health_records.json"
)


def _load_records():
    if not os.path.exists(RECORDS_FILE):
        os.makedirs(os.path.dirname(RECORDS_FILE), exist_ok=True)
        # Seed initial realistic historical scan records linked to fields
        default_records = [
            {
                "id": "rec_001",
                "field_id": "field_indore_01",
                "field_name": "Malwa Wheat Farm (मालवा गेहूं खेत)",
                "crop_type": "Wheat",
                "record_type": "CROP_SCAN",
                "date": "2024-12-15",
                "diagnosis": "Yellow Rust (पीला रतुआ)",
                "confidence_pct": 92.4,
                "health_score": 68,
                "satellite_ndvi": 0.58,
                "severity": "Moderate (प्रारंभिक लक्षण)",
                "recommendation": "Propiconazole 25% EC @ 1 ml/L spray immediately. Avoid excessive urea.",
                "notes": "Farmer sprayed propiconazole on Dec 17. Leaves recovering well.",
                "follow_ups": [
                    {"date": "2024-12-20", "note": "Checked 5 days after spray: pustule spread halted."}
                ]
            },
            {
                "id": "rec_002",
                "field_id": "field_indore_01",
                "field_name": "Malwa Wheat Farm (मालवा गेहूं खेत)",
                "crop_type": "Wheat",
                "record_type": "SATELLITE_NDVI",
                "date": "2024-12-28",
                "diagnosis": "Healthy Canopy Vigor",
                "confidence_pct": 98.0,
                "health_score": 88,
                "satellite_ndvi": 0.74,
                "severity": "None (स्वस्थ)",
                "recommendation": "Maintain scheduled tillering irrigation.",
                "notes": "Vegetative canopy expanded significantly after first watering.",
                "follow_ups": []
            },
            {
                "id": "rec_003",
                "field_id": "field_bhopal_02",
                "field_name": "Narmada Soybean Plot (सोयाबीन प्रक्षेत्र)",
                "crop_type": "Soybean",
                "record_type": "SOIL_ANALYSIS",
                "date": "2024-06-22",
                "diagnosis": "Clay Loam — Low Available Nitrogen",
                "confidence_pct": 95.0,
                "health_score": 75,
                "satellite_ndvi": 0.28,
                "severity": "Mild Deficiency",
                "recommendation": "Apply 100 kg SSP + 20 kg Zinc Sulphate basal dose before monsoon sowing.",
                "notes": "Applied well-rotted FYM (2 tonnes/acre) during second plowing.",
                "follow_ups": []
            }
        ]
        with open(RECORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_records, f, indent=2, ensure_ascii=False)
        return default_records

    try:
        with open(RECORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[CropHistoryService] Error loading records: {e}")
        return []


def _save_records(records):
    os.makedirs(os.path.dirname(RECORDS_FILE), exist_ok=True)
    with open(RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def get_crop_health_history(field_id=None, crop_type=None):
    """
    Retrieve integrated historical health records with field-wise and crop-wise filtering.
    """
    records = _load_records()
    filtered = records

    if field_id and field_id != "all":
        filtered = [r for r in filtered if r.get("field_id") == field_id]

    if crop_type and crop_type != "all":
        filtered = [r for r in filtered if r.get("crop_type", "").lower() == crop_type.lower()]

    # Sort descending by date
    filtered.sort(key=lambda x: x.get("date", ""), reverse=True)

    # Compute summary stats
    total_records = len(filtered)
    avg_health = (
        round(sum([r.get("health_score", 70) for r in filtered]) / total_records, 1)
        if total_records > 0 else 75.0
    )
    disease_issues = len([
        r for r in filtered
        if "rust" in r.get("diagnosis", "").lower() or
           "blight" in r.get("diagnosis", "").lower() or
           "deficiency" in r.get("diagnosis", "").lower()
    ])

    return {
        "status": "Success",
        "total_count": total_records,
        "avg_health_score": avg_health,
        "active_issues_detected": disease_issues,
        "records": filtered
    }


def add_health_record(data):
    """Save a new crop scan, soil test, or satellite record linked to a field."""
    records = _load_records()
    rec_id = f"rec_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    new_rec = {
        "id": rec_id,
        "field_id": data.get("field_id", "unassigned"),
        "field_name": data.get("field_name", "General Field"),
        "crop_type": data.get("crop_type", "Wheat"),
        "record_type": data.get("record_type", "CROP_SCAN"),
        "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
        "diagnosis": data.get("diagnosis", "Normal Health"),
        "confidence_pct": float(data.get("confidence_pct", 90.0)),
        "health_score": int(data.get("health_score", 80)),
        "satellite_ndvi": float(data.get("satellite_ndvi", 0.60)),
        "severity": data.get("severity", "None"),
        "recommendation": data.get("recommendation", "Routine management."),
        "notes": data.get("notes", ""),
        "follow_ups": []
    }
    records.insert(0, new_rec)
    _save_records(records)
    return new_rec


def add_follow_up_note(record_id, note_text):
    """Append a follow-up observation note to an existing health record."""
    records = _load_records()
    for r in records:
        if r.get("id") == record_id:
            if "follow_ups" not in r:
                r["follow_ups"] = []
            new_note = {
                "date": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
                "note": note_text.strip()
            }
            r["follow_ups"].append(new_note)
            _save_records(records)
            return {"status": "Success", "record": r}
    return {"status": "Error", "message": "Record not found"}

