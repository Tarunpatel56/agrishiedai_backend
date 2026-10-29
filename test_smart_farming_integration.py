import os
import sys
import json
import unittest

# Ensure backend root is on path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import app

class TestSmartFarmingPhase2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.app.test_client()

    def test_01_field_management(self):
        print("\n[TEST 1] Testing Field Management...")
        # 1. List fields
        r1 = self.client.get('/api/smart-farming/fields')
        self.assertEqual(r1.status_code, 200)
        data1 = r1.json
        self.assertEqual(data1['status'], 'Success')
        initial_count = len(data1['fields'])
        print(f"  Initial fields count: {initial_count}")

        # 2. Create new field with polygon
        new_payload = {
            "name": "Integration Test Wheat Field",
            "crop_type": "Wheat",
            "soil_type": "Black Cotton (काली मिट्टी)",
            "sowing_date": "2024-11-20",
            "latitude": 22.720,
            "longitude": 75.858,
            "state": "Madhya Pradesh",
            "district": "Indore",
            "boundary_points": [
                [22.721, 75.856],
                [22.722, 75.861],
                [22.718, 75.862],
                [22.717, 75.857]
            ]
        }
        r2 = self.client.post('/api/smart-farming/fields', json=new_payload)
        self.assertEqual(r2.status_code, 201)
        data2 = r2.json
        self.assertEqual(data2['status'], 'Success')
        field_id = data2['field']['id']
        area = data2['field']['area_acres']
        self.assertGreater(area, 0.0)
        print(f"  Created field ID: {field_id}, Auto-calculated Area: {area} Acres")

        # 3. Get field by ID
        r3 = self.client.get(f'/api/smart-farming/fields/{field_id}')
        self.assertEqual(r3.status_code, 200)
        self.assertEqual(r3.json['field']['name'], "Integration Test Wheat Field")

        # 4. Update field
        r4 = self.client.put(f'/api/smart-farming/fields/{field_id}', json={"name": "Updated Wheat Field"})
        self.assertEqual(r4.status_code, 200)
        self.assertEqual(r4.json['field']['name'], "Updated Wheat Field")

        # 5. Clean up delete
        r5 = self.client.delete(f'/api/smart-farming/fields/{field_id}')
        self.assertEqual(r5.status_code, 200)
        print("  Field management test passed successfully!")

    def test_02_satellite_monitoring_ndvi(self):
        print("\n[TEST 2] Testing Satellite Monitoring & NDVI...")
        payload = {
            "latitude": 22.7196,
            "longitude": 75.8577,
            "crop_type": "Wheat",
            "sowing_date": "2024-11-15"
        }
        r = self.client.post('/api/smart-farming/satellite-monitoring', json=payload)
        self.assertEqual(r.status_code, 200)
        data = r.json
        self.assertEqual(data['status'], 'Success')
        self.assertIn('ndvi_stats', data)
        mean_ndvi = data['ndvi_stats']['mean_ndvi']
        self.assertGreater(mean_ndvi, 0.0)
        self.assertLess(mean_ndvi, 1.0)
        img_url = data['ndvi_image_url']
        print(f"  Sentinel-2 Scene: {data['selected_scene']['scene_id']}")
        print(f"  Mean NDVI: {mean_ndvi}, Status: {data['ndvi_stats']['health_status']}")
        print(f"  NDVI Heatmap URL: {img_url}")

        # Test serving the image
        img_resp = self.client.get(img_url)
        self.assertEqual(img_resp.status_code, 200)
        self.assertEqual(img_resp.mimetype, 'image/png')
        self.assertGreater(len(img_resp.data), 1000)
        print("  Satellite monitoring & NDVI generation passed!")

    def test_03_weather_alerts(self):
        print("\n[TEST 3] Testing Weather & Crop Alerts (Open-Meteo)...")
        r = self.client.get('/api/smart-farming/weather-alerts?lat=22.7196&lon=75.8577&crop=Wheat')
        self.assertEqual(r.status_code, 200)
        data = r.json
        self.assertEqual(data['status'], 'Success')
        cw = data['current_weather']
        print(f"  Current: {cw['temperature']}°C, {cw['condition']}, Wind: {cw['wind_speed']} km/h")
        self.assertIn('alerts', data)
        print(f"  Agricultural Alerts generated: {len(data['alerts'])}")
        self.assertEqual(len(data['daily_forecast']), 7)
        print("  Weather alerts test passed!")

    def test_04_smart_irrigation_advisor(self):
        print("\n[TEST 4] Testing Smart Irrigation Advisor (No IoT / FAO-56)...")
        payload = {
            "crop_type": "Wheat",
            "sowing_date": "2024-11-15",
            "soil_type": "Black Cotton",
            "area_acres": 4.5,
            "latitude": 22.7196,
            "longitude": 75.8577
        }
        r = self.client.post('/api/smart-farming/irrigation-advisor', json=payload)
        self.assertEqual(r.status_code, 200)
        data = r.json
        self.assertEqual(data['status'], 'Success')
        rec = data['recommendation']
        print(f"  Recommendation: {rec['urgency']}")
        print(f"  Water Volume: {rec['water_volume_m3']} m³ ({rec['water_volume_liters']} L)")
        self.assertEqual(len(data['schedule_7d']), 7)

        # Test Logging an irrigation event
        log_payload = {
            "field_id": "field_indore_01",
            "field_name": "Malwa Wheat Farm",
            "crop_type": "Wheat",
            "depth_mm": 40.0,
            "method": "Flood",
            "notes": "Automated test irrigation"
        }
        r_log = self.client.post('/api/smart-farming/irrigation-log', json=log_payload)
        self.assertEqual(r_log.status_code, 201)

        r_hist = self.client.get('/api/smart-farming/irrigation-history?field_id=field_indore_01')
        self.assertEqual(r_hist.status_code, 200)
        self.assertGreater(len(r_hist.json['logs']), 0)
        print("  Smart irrigation advisor test passed!")

    def test_05_groundwater_trends(self):
        print("\n[TEST 5] Testing CGWB Groundwater Trends...")
        for dist in ["Indore", "Bhopal", "Ujjain", "Ludhiana"]:
            r = self.client.get(f'/api/smart-farming/groundwater-trends?district={dist}')
            self.assertEqual(r.status_code, 200)
            d = r.json
            self.assertEqual(d['status'], 'Success')
            print(f"  {dist}: Depth={d['latest_depth_mbgl']} mbgl, Category={d['category_en']}")
            self.assertGreater(len(d['historical_records']), 4)
            self.assertIn("honesty_disclaimer", d)
        print("  Groundwater trend monitoring test passed!")

    def test_06_crop_health_history(self):
        print("\n[TEST 6] Testing Crop Health History...")
        r = self.client.get('/api/smart-farming/crop-health-history')
        self.assertEqual(r.status_code, 200)
        data = r.json
        self.assertEqual(data['status'], 'Success')
        self.assertGreater(len(data['records']), 0)
        first_id = data['records'][0]['id']

        # Add follow-up note
        r_fu = self.client.post('/api/smart-farming/crop-health-history/follow-up', json={
            "record_id": first_id,
            "note": "Crop has shown strong vegetative recovery after scheduled watering."
        })
        self.assertEqual(r_fu.status_code, 200)
        self.assertEqual(r_fu.json['status'], 'Success')
        print("  Crop health history test passed!")

    def test_07_crop_risk_assessment(self):
        print("\n[TEST 7] Testing AI Crop Risk Assessment...")
        payload = {
            "crop_type": "Wheat",
            "sowing_date": "2024-11-15",
            "soil_type": "Black Cotton",
            "latitude": 22.7196,
            "longitude": 75.8577
        }
        r = self.client.post('/api/smart-farming/crop-risk-assessment', json=payload)
        self.assertEqual(r.status_code, 200)
        data = r.json
        self.assertEqual(data['status'], 'Success')
        score = data['overall_risk_score']
        self.assertTrue(0 <= score <= 100)
        print(f"  Overall Risk Score: {score}/100 ({data['overall_risk_level']})")
        self.assertIn('pest_disease', data['risk_breakdown'])
        self.assertIn('drought_deficit', data['risk_breakdown'])
        self.assertIn('waterlogging', data['risk_breakdown'])
        self.assertIn('heat_stress', data['risk_breakdown'])
        self.assertIn('operational_spray', data['risk_breakdown'])
        self.assertGreater(len(data['recommended_actions']), 0)
        print("  Crop risk assessment test passed!")

    def test_08_crop_planning_calendar(self):
        print("\n[TEST 8] Testing Crop Planning Calendar...")
        payload = {
            "crop_type": "Wheat",
            "sowing_date": "2024-11-15"
        }
        r = self.client.post('/api/smart-farming/crop-calendar', json=payload)
        self.assertEqual(r.status_code, 200)
        data = r.json
        self.assertEqual(data['status'], 'Success')
        self.assertGreater(len(data['stages']), 3)
        self.assertGreater(len(data['tasks']), 4)
        task_id = data['tasks'][0]['id']
        field_id = data['field_id']

        # Test toggling task
        r_task = self.client.patch('/api/smart-farming/crop-calendar/task', json={
            "field_id": field_id,
            "task_id": task_id,
            "is_completed": True
        })
        self.assertEqual(r_task.status_code, 200)
        self.assertEqual(r_task.json['status'], 'Success')
        print("  Crop planning calendar test passed!")

    def test_09_imd_integration_status(self):
        print("\n[TEST 9] Testing IMD Official API Integration Status & Gateways...")
        r = self.client.get('/api/smart-farming/imd/status')
        self.assertEqual(r.status_code, 200)
        d = r.json
        self.assertIn(d['status'], ['Auth_Required', 'Configured'])
        self.assertEqual(d['provider'], "India Meteorological Department (IMD)")
        self.assertIn("x-api-key", d['access_requirements']['api_key_header'])
        self.assertIn("Authorization: Bearer", d['access_requirements']['auth_header'])
        print(f"  IMD Status: {d['status']}, Is Operational: {d['is_operational']}")
        print(f"  Access Requirements: {d['access_requirements']}")

        # Agromet Advisory endpoint status
        r_agro = self.client.get('/api/smart-farming/imd/agromet-advisory')
        self.assertEqual(r_agro.status_code, 200)
        self.assertEqual(r_agro.json['status'], "Endpoint_Unpublished")
        print("  IMD Agromet Advisory Status verified as Endpoint_Unpublished.")

        # Test auth protection on endpoints
        r_cf = self.client.get('/api/smart-farming/imd/city-forecast')
        self.assertEqual(r_cf.status_code, 200)
        self.assertIn(r_cf.json['status'], ['Auth_Required', 'Success'])
        print("  IMD endpoints verified with documented authentication requirements.")

    def test_10_groundwater_unverified_district_safety(self):
        print("\n[TEST 10] Testing Groundwater District Verification & Safety (No Assam for MP)...")
        # 1. Unverified district should return Data_Unavailable, NOT fake data or Assam data
        r_unv = self.client.get('/api/smart-farming/groundwater-trends?district=Guwahati')
        self.assertEqual(r_unv.status_code, 200)
        d_unv = r_unv.json
        self.assertEqual(d_unv['status'], "Data_Unavailable")
        self.assertIn("No verified CGWB hydrograph station records", d_unv['message'])
        print("  Unverified district correctly returned Data_Unavailable (No false data).")

        # 2. Verified MP districts
        for dist in ["Indore", "Bhopal", "Ujjain"]:
            r = self.client.get(f'/api/smart-farming/groundwater-trends?district={dist}')
            self.assertEqual(r.status_code, 200)
            d = r.json
            self.assertEqual(d['status'], 'Success')
            self.assertEqual(d['state'], "Madhya Pradesh")
            self.assertIn("verified_data_guarantee", d)
            print(f"  {dist} verified: State={d['state']}, Station={d['monitoring_station']}, Depth={d['latest_depth_mbgl']} mbgl")

    def test_11_open_meteo_dynamic_coordinates(self):
        print("\n[TEST 11] Testing Open-Meteo Dynamic Coordinates (Bhopal lat=23.2599, lon=77.4126)...")
        r = self.client.get('/api/smart-farming/weather-alerts?lat=23.2599&lon=77.4126&crop=Gram')
        self.assertEqual(r.status_code, 200)
        d = r.json
        self.assertEqual(d['status'], 'Success')
        self.assertEqual(d['location']['latitude'], 23.2599)
        self.assertEqual(d['location']['longitude'], 77.4126)
        self.assertEqual(d['crop_type'], 'Gram')
        self.assertIn('temperature', d['current_weather'])
        self.assertIn('humidity', d['current_weather'])
        self.assertEqual(len(d['daily_forecast']), 7)
        print(f"  Dynamic weather returned: Temp={d['current_weather']['temperature']}°C, Humidity={d['current_weather']['humidity']}%")

if __name__ == '__main__':
    unittest.main()

