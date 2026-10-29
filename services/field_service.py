import os
import json
import math
import uuid
from datetime import datetime

FIELDS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "project_data", "fields.json")


def _calculate_polygon_area_acres(points):
    """
    Calculate area in acres for a list of [lat, lon] coordinates
    using the spherical Shoelace formula on Earth's surface.
    """
    if not points or len(points) < 3:
        return 0.0

    R = 6378137.0  # Earth's radius in meters (WGS84)
    area = 0.0
    n = len(points)

    for i in range(n):
        p1 = points[i]
        p2 = points[(i + 1) % n]
        lat1 = math.radians(p1[0])
        lat2 = math.radians(p2[0])
        lon1 = math.radians(p1[1])
        lon2 = math.radians(p2[1])
        area += (lon2 - lon1) * (2.0 + math.sin(lat1) + math.sin(lat2))

    area = abs(area * (R * R) / 2.0)  # square meters
    area_acres = area / 4046.8564224  # 1 acre = 4046.856 m²
    return round(area_acres, 2)


def _load_fields():
    if not os.path.exists(FIELDS_FILE):
        os.makedirs(os.path.dirname(FIELDS_FILE), exist_ok=True)
        # Create initial verified reference fields in Madhya Pradesh and Punjab
        default_fields = [
            {
                "id": "field_indore_01",
                "name": "Malwa Wheat Farm (मालवा गेहूं खेत)",
                "crop_type": "Wheat",
                "soil_type": "Black Cotton (काली मिट्टी)",
                "sowing_date": "2024-11-15",
                "area_acres": 4.5,
                "area_hectares": 1.82,
                "latitude": 22.7196,
                "longitude": 75.8577,
                "state": "Madhya Pradesh",
                "district": "Indore",
                "boundary_points": [
                    [22.7210, 75.8560],
                    [22.7215, 75.8600],
                    [22.7180, 75.8605],
                    [22.7175, 75.8565]
                ],
                "created_at": "2024-11-10T09:00:00Z",
                "updated_at": "2024-11-10T09:00:00Z"
            },
            {
                "id": "field_bhopal_02",
                "name": "Narmada Soybean Plot (सोयाबीन प्रक्षेत्र)",
                "crop_type": "Soybean",
                "soil_type": "Clay Loam (दोमट मिट्टी)",
                "sowing_date": "2024-06-25",
                "area_acres": 3.2,
                "area_hectares": 1.30,
                "latitude": 23.2599,
                "longitude": 77.4126,
                "state": "Madhya Pradesh",
                "district": "Bhopal",
                "boundary_points": [
                    [23.2610, 77.4110],
                    [23.2620, 77.4140],
                    [23.2580, 77.4145],
                    [23.2575, 77.4115]
                ],
                "created_at": "2024-06-20T10:30:00Z",
                "updated_at": "2024-06-20T10:30:00Z"
            }
        ]
        with open(FIELDS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_fields, f, indent=2, ensure_ascii=False)
        return default_fields

    try:
        with open(FIELDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[FieldService] Error loading fields: {e}")
        return []


def _save_fields(fields):
    os.makedirs(os.path.dirname(FIELDS_FILE), exist_ok=True)
    with open(FIELDS_FILE, "w", encoding="utf-8") as f:
        json.dump(fields, f, indent=2, ensure_ascii=False)


def get_all_fields():
    """Retrieve all saved fields."""
    return _load_fields()


def get_field_by_id(field_id):
    """Retrieve a single field by ID."""
    fields = _load_fields()
    for f in fields:
        if f.get("id") == field_id:
            return f
    return None


def create_field(data):
    """
    Create a new field with boundary coordinates, area calculation,
    and metadata.
    """
    fields = _load_fields()
    field_id = f"field_{uuid.uuid4().hex[:8]}"

    boundary_points = data.get("boundary_points", [])
    area_acres = data.get("area_acres")

    if (not area_acres or float(area_acres) <= 0) and boundary_points and len(boundary_points) >= 3:
        area_acres = _calculate_polygon_area_acres(boundary_points)
    else:
        try:
            area_acres = float(area_acres) if area_acres else 2.5
        except (ValueError, TypeError):
            area_acres = 2.5

    area_ha = round(area_acres * 0.404686, 2)
    lat = float(data.get("latitude", 22.7196))
    lon = float(data.get("longitude", 75.8577))

    now = datetime.now().isoformat()
    new_field = {
        "id": field_id,
        "name": data.get("name", "My Field").strip(),
        "crop_type": data.get("crop_type", "Wheat").strip(),
        "soil_type": data.get("soil_type", "Loam").strip(),
        "sowing_date": data.get("sowing_date", datetime.now().strftime("%Y-%m-%d")),
        "area_acres": area_acres,
        "area_hectares": area_ha,
        "latitude": lat,
        "longitude": lon,
        "state": data.get("state", "Madhya Pradesh").strip(),
        "district": data.get("district", "Indore").strip(),
        "boundary_points": boundary_points,
        "created_at": now,
        "updated_at": now
    }

    fields.append(new_field)
    _save_fields(fields)
    return new_field


def update_field(field_id, data):
    """Update existing field details."""
    fields = _load_fields()
    for idx, f in enumerate(fields):
        if f.get("id") == field_id:
            boundary_points = data.get("boundary_points", f.get("boundary_points", []))
            area_acres = data.get("area_acres", f.get("area_acres"))
            if boundary_points and len(boundary_points) >= 3 and not data.get("area_acres"):
                area_acres = _calculate_polygon_area_acres(boundary_points)

            try:
                area_acres = float(area_acres)
            except (ValueError, TypeError):
                area_acres = f.get("area_acres", 2.5)

            area_ha = round(area_acres * 0.404686, 2)

            f["name"] = data.get("name", f["name"])
            f["crop_type"] = data.get("crop_type", f["crop_type"])
            f["soil_type"] = data.get("soil_type", f["soil_type"])
            f["sowing_date"] = data.get("sowing_date", f["sowing_date"])
            f["area_acres"] = area_acres
            f["area_hectares"] = area_ha
            f["latitude"] = float(data.get("latitude", f["latitude"]))
            f["longitude"] = float(data.get("longitude", f["longitude"]))
            f["state"] = data.get("state", f.get("state", "Madhya Pradesh"))
            f["district"] = data.get("district", f.get("district", "Indore"))
            f["boundary_points"] = boundary_points
            f["updated_at"] = datetime.now().isoformat()

            fields[idx] = f
            _save_fields(fields)
            return f
    return None


def delete_field(field_id):
    """Delete a field by ID."""
    fields = _load_fields()
    initial_len = len(fields)
    fields = [f for f in fields if f.get("id") != field_id]
    if len(fields) < initial_len:
        _save_fields(fields)
        return True
    return False

