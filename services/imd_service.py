import os
import requests
import urllib3

urllib3.disable_warnings()

IMD_BASE = "https://api.imd.gov.in/api/v1"
IMD_API_KEY = os.getenv("IMD_API_KEY")
IMD_AUTH_TOKEN = os.getenv("IMD_AUTH_TOKEN")


def get_imd_auth_status():
    """
    Checks the status and verification details for official IMD API access.
    Adheres strictly to official IMD API documentation (https://api.imd.gov.in/public/api_reference.html).
    """
    has_key = bool(IMD_API_KEY)
    has_token = bool(IMD_AUTH_TOKEN)

    return {
        "status": "Configured" if (has_key and has_token) else "Auth_Required",
        "provider": "India Meteorological Department (IMD)",
        "ministry": "Ministry of Earth Sciences, Government of India",
        "official_reference": "https://api.imd.gov.in/public/api_reference.html",
        "endpoints_documented": [
            {"id": "api-1", "name": "City Weather forecast for 7 days", "url": f"{IMD_BASE}/cityforecast?id=StationId"},
            {"id": "api-2", "name": "City Weather forecast with location", "url": f"{IMD_BASE}/cityforecastloc?id=StationId"},
            {"id": "api-5", "name": "District-wise Rainfall", "url": f"{IMD_BASE}/districtrainfall?id=DistrictId"},
            {"id": "api-6", "name": "District-wise Warnings", "url": f"{IMD_BASE}/districtwarning?id=DistrictId"}
        ],
        "access_requirements": {
            "api_key_header": "x-api-key",
            "auth_header": "Authorization: Bearer <JWT_TOKEN>",
            "registration_portal": "https://api.imd.gov.in/",
            "approval_type": "Institutional MoES registration & IP whitelisting required"
        },
        "credentials_configured": {
            "has_api_key": has_key,
            "has_auth_token": has_token
        },
        "is_operational": bool(has_key and has_token),
        "notes": (
            "IMD's official gateway (api.imd.gov.in) enforces HTTP 401 with 'API key missing' "
            "and 'Invalid or expired JWT token' on unauthenticated requests. "
            "Open-Meteo continues to serve live weather forecasting seamlessly without rate-blocks."
        )
    }


def fetch_imd_city_forecast(station_id="42182"):
    """
    Query IMD City Weather Forecast (e.g. 42182 = New Delhi, or MP station codes).
    Requires registered credentials.
    """
    if not IMD_API_KEY or not IMD_AUTH_TOKEN:
        return {
            "status": "Auth_Required",
            "provider": "India Meteorological Department (IMD)",
            "endpoint": f"{IMD_BASE}/cityforecastloc?id={station_id}",
            "message": "Official IMD access requires registered x-api-key and Bearer JWT token. Live forecasts are active via Open-Meteo.",
            "is_live_data": False
        }

    try:
        headers = {
            "x-api-key": IMD_API_KEY,
            "Authorization": f"Bearer {IMD_AUTH_TOKEN}",
            "Accept": "application/json"
        }
        resp = requests.get(f"{IMD_BASE}/cityforecastloc?id={station_id}", headers=headers, timeout=10, verify=False)
        if resp.status_code == 200:
            return {"status": "Success", "data": resp.json(), "is_live_data": True}
        return {
            "status": "IMD_API_Error",
            "http_status": resp.status_code,
            "error_body": resp.text[:300],
            "is_live_data": False
        }
    except Exception as e:
        return {"status": "Network_Error", "error": str(e), "is_live_data": False}


def fetch_imd_district_rainfall(district_id="164"):
    """
    Query IMD District-wise Rainfall. Requires registered credentials.
    """
    if not IMD_API_KEY or not IMD_AUTH_TOKEN:
        return {
            "status": "Auth_Required",
            "provider": "India Meteorological Department (IMD)",
            "endpoint": f"{IMD_BASE}/districtrainfall?id={district_id}",
            "message": "Official IMD access requires registered x-api-key and Bearer JWT token. District rainfall is currently computed from Open-Meteo.",
            "is_live_data": False
        }

    try:
        headers = {
            "x-api-key": IMD_API_KEY,
            "Authorization": f"Bearer {IMD_AUTH_TOKEN}",
            "Accept": "application/json"
        }
        resp = requests.get(f"{IMD_BASE}/districtrainfall?id={district_id}", headers=headers, timeout=10, verify=False)
        if resp.status_code == 200:
            return {"status": "Success", "data": resp.json(), "is_live_data": True}
        return {
            "status": "IMD_API_Error",
            "http_status": resp.status_code,
            "error_body": resp.text[:300],
            "is_live_data": False
        }
    except Exception as e:
        return {"status": "Network_Error", "error": str(e), "is_live_data": False}


def fetch_imd_district_warning(district_id="573"):
    """
    Query IMD District-wise Warnings. Requires registered credentials.
    """
    if not IMD_API_KEY or not IMD_AUTH_TOKEN:
        return {
            "status": "Auth_Required",
            "provider": "India Meteorological Department (IMD)",
            "endpoint": f"{IMD_BASE}/districtwarning?id={district_id}",
            "message": "Official IMD access requires registered x-api-key and Bearer JWT token. Weather alerts are currently generated using Open-Meteo 7-day model.",
            "is_live_data": False
        }

    try:
        headers = {
            "x-api-key": IMD_API_KEY,
            "Authorization": f"Bearer {IMD_AUTH_TOKEN}",
            "Accept": "application/json"
        }
        resp = requests.get(f"{IMD_BASE}/districtwarning?id={district_id}", headers=headers, timeout=10, verify=False)
        if resp.status_code == 200:
            return {"status": "Success", "data": resp.json(), "is_live_data": True}
        return {
            "status": "IMD_API_Error",
            "http_status": resp.status_code,
            "error_body": resp.text[:300],
            "is_live_data": False
        }
    except Exception as e:
        return {"status": "Network_Error", "error": str(e), "is_live_data": False}


def get_imd_agromet_advisory_status():
    """
    Status of IMD Agromet Advisory API.
    Item 28 in IMD API index, but public endpoint specification is not yet released.
    """
    return {
        "status": "Endpoint_Unpublished",
        "provider": "India Meteorological Department (IMD) - Agrimet Division, Pune",
        "api_index_item": "28) Agromet Advisory",
        "official_reference": "https://api.imd.gov.in/public/api_reference.html",
        "portal": "https://imdagrimet.gov.in/",
        "message": (
            "The Agromet Advisory API is indexed under item 28 in the IMD public index, "
            "but the official endpoint schema and parameters are not yet published in the public reference documentation. "
            "AgriShield AI will integrate this endpoint once IMD formally releases the public schema."
        ),
        "is_operational": False
    }

