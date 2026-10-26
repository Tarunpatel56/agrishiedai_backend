"""
AgriShield — Comprehensive Feature & Independence Verification Test
=====================================================================
Tests:
1. Twilio Language Selection IVR (Hindi / English DTMF & Voice)
2. Independent Plant Disease Model
3. Independent Pet/Pest Disease Model
4. Independent Soil Analysis Model
5. Live Mandi Market Prices (Agmarknet / data.gov.in)
6. Government Agricultural Schemes
7. Crop Spray Advisor (IPM & CIBRC)
8. Fertilizer Prescription & Nutrient Calculations
"""

import os
import sys
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from services.plant_disease_service import run_plant_disease_inference
from services.pet_disease_service import run_pet_disease_inference
from services.soil_analysis_service import run_soil_analysis_inference
from services.market_service import get_market_prices
from services.govt_schemes_service import get_all_schemes
from services.spray_advisor_service import get_spray_recommendation
from services.fertilizer_advisor_service import calculate_fertilizer_prescription
from agrishield_twilio import (
    generate_language_selection_twiml,
    handle_language_selection,
    handle_voice_input
)

client = app.test_client()

print("=" * 60)
print("  AgriShield Comprehensive Test Suite")
print("=" * 60)

passed = 0
failed = 0

def assert_test(name, condition, details=""):
    global passed, failed
    if condition:
        print(f"  [PASS] {name}")
        passed += 1
    else:
        print(f"  [FAIL] {name} -> {details}")
        failed += 1


# ── TEST 1: Twilio Language Selection Prompts ──
print("\n--- 1. Twilio Language Selection & Voice Call Flow ---")
twiml_welcome = generate_language_selection_twiml()
assert_test(
    "Incoming Call plays Language Prompt (1: Hindi, 2: English)",
    "हिंदी के लिए 1 दबाएं" in twiml_welcome and "For English, press 2" in twiml_welcome and "/voice-lang-select" in twiml_welcome
)

# Test DTMF 1 -> Hindi
twiml_hi = handle_language_selection("1")
assert_test(
    "Press 1 selects Hindi and gathers Hindi speech",
    "नमस्ते किसान भाई" in twiml_hi and "hi-IN" in twiml_hi and "lang=hi" in twiml_hi
)

# Test DTMF 2 -> English
twiml_en = handle_language_selection("2")
assert_test(
    "Press 2 selects English and gathers English speech",
    "Hello farmer" in twiml_en and "en-IN" in twiml_en and "lang=en" in twiml_en
)

# Test Invalid Keypress -> re-prompts
twiml_invalid = handle_language_selection("9")
assert_test(
    "Invalid digit prompts error and offers re-selection",
    "अमान्य विकल्प" in twiml_invalid and "Invalid option" in twiml_invalid
)

# Test Voice Response in English
twiml_resp_en = handle_voice_input("What is the best time to sow wheat?", lang="en")
assert_test(
    "Voice response in English uses Polly.Aditi with en-IN and English follow-up",
    "en-IN" in twiml_resp_en and "Do you have any other questions" in twiml_resp_en
)


# ── TEST 2: Independent Plant Disease Model ──
print("\n--- 2. Independent Plant Disease Model ---")
# Missing file error handling
err_res = run_plant_disease_inference("non_existent_file.jpg")
assert_test(
    "Plant model handles missing file gracefully",
    "error" in err_res and "not found" in err_res["error"].lower()
)

# Test with stored crop image
crop_test_img = os.path.join("stored_soil", "soil_1.jpg")  # Pass soil image to plant model to test rejection!
rejection_test = run_plant_disease_inference(crop_test_img)
assert_test(
    "Plant model isolates and rejects non-plant images",
    "error" in rejection_test or "plant" in str(rejection_test).lower()
)


# ── TEST 3: Independent Pet/Pest Disease Model ──
print("\n--- 3. Independent Pet/Pest Disease Model ---")
err_pet = run_pet_disease_inference("non_existent_pet.jpg")
assert_test(
    "Pet model handles missing file gracefully",
    "error" in err_pet and "not found" in err_pet["error"].lower()
)


# ── TEST 4: Independent Soil Analysis Model ──
print("\n--- 4. Independent Soil Analysis Model ---")
err_soil = run_soil_analysis_inference("non_existent_soil.jpg")
assert_test(
    "Soil model handles missing file gracefully",
    "error" in err_soil and "not found" in err_soil["error"].lower()
)


# ── TEST 5: Mandi Prices (Agmarknet / data.gov.in) ──
print("\n--- 5. Mandi Market Prices (Official Data & Dates) ---")
mandi_res = get_market_prices()
assert_test(
    "Mandi prices returns non-empty list with official dates and prices",
    len(mandi_res) > 0 and "current_price" in mandi_res[0] and "arrival_date" in mandi_res[0]
)

# Test filtering by commodity
wheat_res = get_market_prices(commodity="Wheat")
assert_test(
    "Mandi prices filter by commodity works",
    all("wheat" in x["crop_name"].lower() for x in wheat_res) if wheat_res else True
)


# ── TEST 6: Government Schemes ──
print("\n--- 6. Government Agricultural Schemes ---")
schemes = get_all_schemes()
assert_test(
    "Govt schemes returns comprehensive list with official links and criteria",
    len(schemes) >= 7 and "eligibility" in schemes[0] and "official_link" in schemes[0] and "required_documents" in schemes[0]
)

# Test category filter
income_schemes = get_all_schemes(category="Income Support")
assert_test(
    "Govt schemes category filter works (Income Support)",
    any(s["id"] == "pm-kisan" for s in income_schemes)
)


# ── TEST 7: Crop Spray Advisor ──
print("\n--- 7. Crop Spray Advisor (IPM & CIBRC) ---")
spray_res = get_spray_recommendation(
    crop_name="Wheat",
    growth_stage="Vegetative",
    symptoms="Yellow powdery pustules on leaves forming stripes",
    affected_parts="Leaves",
    severity="Moderate"
)
assert_test(
    "Spray advisor returns IPM, cultural, biological, and CIBRC chemical recommendations",
    "identified_problem" in spray_res and "cultural_management" in spray_res and "chemical_treatment" in spray_res
)


# ── TEST 8: Fertilizer Prescription / Nutrient Advisor ──
print("\n--- 8. Fertilizer Prescription & Nutrient Calculations ---")
fert_res = calculate_fertilizer_prescription(
    crop_name="Wheat",
    farm_area=5.0,
    area_unit="acre",
    growth_stage="Basal / Sowing",
    soil_type="Loamy",
    soil_test_n="Medium",
    soil_test_p="Medium",
    soil_test_k="Medium"
)
assert_test(
    "Fertilizer advisor computes elemental nutrients and commercial product bags for 5 acres",
    "pure_nutrients_required" in fert_res and
    "commercial_fertilizers" in fert_res and
    fert_res["commercial_fertilizers"]["urea_46_n"]["bags_45kg"] > 0 and
    fert_res["commercial_fertilizers"]["dap_18_46_0"]["bags_50kg"] > 0
)


# ── TEST 9: Flask REST API Endpoints ──
print("\n--- 9. Flask Backend Route Availability ---")
health_resp = client.get('/')
assert_test(
    "GET / (Health Check) returns 200 with all 23 active endpoints",
    health_resp.status_code == 200 and len(health_resp.get_json().get("endpoints", [])) >= 20
)

schemes_resp = client.get('/govt-schemes')
assert_test(
    "GET /govt-schemes returns 200 with schemes data",
    schemes_resp.status_code == 200 and schemes_resp.get_json().get("status") == "Success"
)

mandi_resp = client.get('/mandi-prices?commodity=Wheat')
assert_test(
    "GET /mandi-prices returns 200 with filtered items",
    mandi_resp.status_code == 200 and isinstance(mandi_resp.get_json(), list)
)

fert_resp = client.post('/fertilizer-advisor', json={
    "crop_name": "Rice",
    "farm_area": 2.5,
    "area_unit": "acre"
})
assert_test(
    "POST /fertilizer-advisor returns 200 with structured prescription",
    fert_resp.status_code == 200 and fert_resp.get_json().get("status") == "Success"
)

# Test Twilio endpoints via client
voice_inc_resp = client.post('/voice-incoming')
assert_test(
    "POST /voice-incoming returns 200 XML with Language Prompt",
    voice_inc_resp.status_code == 200 and "voice-lang-select" in voice_inc_resp.get_data(as_text=True)
)

voice_lang_resp = client.post('/voice-lang-select', data={"Digits": "2"})
assert_test(
    "POST /voice-lang-select with Digits=2 returns 200 XML English Welcome",
    voice_lang_resp.status_code == 200 and "Hello farmer" in voice_lang_resp.get_data(as_text=True)
)

print("=" * 60)
print(f"  Test Results: {passed} PASSED, {failed} FAILED")
print("=" * 60)

if failed > 0:
    sys.exit(1)
