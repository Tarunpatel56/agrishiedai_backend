import requests
import random
from datetime import datetime, timedelta

def get_recent_weather(lat, lon):
    """
    Fetch LIVE weather data using Open-Meteo API (free, fast, no API key).
    Provides: Temperature, Humidity, Rainfall, Wind Speed, Solar Radiation.
    Falls back to cached/estimated data if API is unavailable.
    """
    try:
        # Open-Meteo — Free, real-time, no API key needed
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,"
            f"weather_code,surface_pressure"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
            f"shortwave_radiation_sum,wind_speed_10m_max"
            f"&timezone=Asia/Kolkata&forecast_days=1"
        )

        print(f"[Weather] Fetching LIVE data for lat={lat}, lon={lon}...")
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            current = data.get('current', {})
            daily = data.get('daily', {})

            live_temp = current.get('temperature_2m', 27.0)
            humidity = current.get('relative_humidity_2m', 55)
            rain = current.get('precipitation', 0.0)
            wind = current.get('wind_speed_10m', 2.0)
            weather_code = current.get('weather_code', 0)

            temp_max = daily.get('temperature_2m_max', [live_temp + 5])[0]
            temp_min = daily.get('temperature_2m_min', [live_temp - 5])[0]
            solar = daily.get('shortwave_radiation_sum', [5.0])[0]
            daily_rain = daily.get('precipitation_sum', [rain])[0]

            # Convert solar from MJ/m² to kWh/m² (divide by 3.6)
            solar_kwh = round(solar / 3.6, 2) if solar else 0.0

            # Weather condition from weather code
            condition = decode_weather_code(weather_code)

            # Smart advisory
            current_hour = datetime.now().hour
            advisory = generate_smart_advisory(live_temp, daily_rain, humidity, solar_kwh, wind, current_hour)

            return {
                "temperature": round(live_temp, 1),
                "temp_max": round(temp_max, 1),
                "temp_min": round(temp_min, 1),
                "rainfall": round(daily_rain, 2),
                "humidity": int(humidity),
                "solar_radiation": solar_kwh,
                "wind_speed": round(wind, 1),
                "condition": condition,
                "status": "🛰️ Live Weather Data",
                "timestamp": datetime.now().strftime('%I:%M:%S %p'),
                "date": datetime.now().strftime('%d %B %Y'),
                "advisory": advisory,
                "alerts": generate_alerts(live_temp, daily_rain, humidity, wind),
                "crop_impact": get_crop_impact(live_temp, daily_rain, humidity, solar_kwh),
            }
        else:
            print(f"[Weather] API returned {response.status_code}")
            return get_fallback_weather()

    except Exception as e:
        print(f"[Weather] Error: {e}")
        return get_fallback_weather()


def decode_weather_code(code):
    """Convert WMO weather codes to readable conditions."""
    codes = {
        0: "Clear Sky ☀️",
        1: "Mostly Clear 🌤️",
        2: "Partly Cloudy ⛅",
        3: "Overcast ☁️",
        45: "Foggy 🌫️",
        48: "Fog with Frost 🌫️❄️",
        51: "Light Drizzle 🌦️",
        53: "Moderate Drizzle 🌦️",
        55: "Dense Drizzle 🌧️",
        61: "Light Rain 🌧️",
        63: "Moderate Rain 🌧️",
        65: "Heavy Rain 🌧️🌧️",
        71: "Light Snow ❄️",
        73: "Moderate Snow ❄️",
        75: "Heavy Snow ❄️❄️",
        80: "Rain Showers 🌦️",
        81: "Moderate Showers 🌧️",
        82: "Violent Showers 🌧️⚡",
        95: "Thunderstorm ⛈️",
        96: "Thunderstorm + Hail ⛈️🧊",
        99: "Severe Thunderstorm ⛈️⚡",
    }
    return codes.get(code, f"Weather Code {code} 🌤️")


def generate_smart_advisory(temp, rain, humidity, solar, wind, hour):
    """Generate intelligent farming advisory based on weather conditions."""
    advisories = []

    if temp > 38:
        advisories.append("⚠️ Extreme heat! Increase irrigation. Avoid fieldwork 11AM-3PM.")
    elif temp > 34:
        advisories.append("🌡️ High temperature. Ensure crop hydration. Use mulching for soil moisture.")
    elif temp < 10:
        advisories.append("❄️ Cold conditions. Protect sensitive crops. Delay morning irrigation.")

    if rain > 10:
        advisories.append("🌧️ Heavy rainfall. Check drainage. Watch for waterlogging.")
    elif rain > 3:
        advisories.append("🌦️ Moderate rain. Reduce irrigation. Good time for post-rain fertilizer.")
    elif rain == 0 and humidity < 40:
        advisories.append("☀️ Dry conditions. Schedule regular irrigation. Monitor soil moisture.")

    if humidity > 85:
        advisories.append("🍃 High humidity = disease risk. Monitor for fungal infections.")
    elif humidity < 30:
        advisories.append("💨 Low humidity. Crops may face water stress. Increase watering.")

    if wind > 20:
        advisories.append("🌬️ Strong winds! Avoid spraying. Secure young plants.")

    if not advisories:
        advisories.append("✅ Weather is favorable for farming. Normal activities can continue.")

    return " | ".join(advisories)


def generate_alerts(temp, rain, humidity, wind):
    """Generate weather alert list."""
    alerts = []
    if temp > 38:
        alerts.append({"type": "danger", "message": "Heat Wave Warning"})
    elif temp > 34:
        alerts.append({"type": "warning", "message": "High Temperature Alert"})
    if rain > 10:
        alerts.append({"type": "danger", "message": "Heavy Rainfall Alert"})
    if humidity > 85:
        alerts.append({"type": "warning", "message": "High Humidity - Disease Risk"})
    if wind > 20:
        alerts.append({"type": "warning", "message": "Strong Wind Advisory"})
    if temp < 5:
        alerts.append({"type": "danger", "message": "Frost Warning"})
    if not alerts:
        alerts.append({"type": "safe", "message": "No weather alerts"})
    return alerts


def get_crop_impact(temp, rain, humidity, solar):
    """Assess how weather affects crops."""
    if 20 <= temp <= 30 and rain > 0 and 50 <= humidity <= 75:
        growth = "Optimal"
    elif 15 <= temp <= 35 and humidity >= 40:
        growth = "Good"
    elif temp > 38 or temp < 10:
        growth = "Stressed"
    else:
        growth = "Moderate"

    if humidity > 80 and rain > 2:
        disease_risk = "High"
    elif humidity > 70:
        disease_risk = "Moderate"
    else:
        disease_risk = "Low"

    if rain > 5:
        irrigation = "Not Needed"
    elif rain > 1:
        irrigation = "Reduced"
    elif temp > 32:
        irrigation = "High Priority"
    else:
        irrigation = "Normal Schedule"

    return {
        "growth_speed": growth,
        "disease_risk": disease_risk,
        "irrigation_need": irrigation,
    }


def get_fallback_weather():
    """Fallback when API unavailable."""
    hour = datetime.now().hour
    base = 26 if 6 <= hour <= 18 else 22
    return {
        "temperature": round(base + random.uniform(-1, 2), 1),
        "temp_max": base + 6,
        "temp_min": base - 4,
        "rainfall": 0.0,
        "humidity": 55,
        "solar_radiation": 5.0 if 6 <= hour <= 18 else 0.0,
        "wind_speed": 2.0,
        "condition": "Data Sync Pending 🔄",
        "status": "⚡ Offline Mode",
        "timestamp": datetime.now().strftime('%I:%M:%S %p'),
        "date": datetime.now().strftime('%d %B %Y'),
        "advisory": "📡 Weather sync in progress. Showing estimated data.",
        "alerts": [{"type": "info", "message": "Using cached data"}],
        "crop_impact": {"growth_speed": "Normal", "disease_risk": "Low", "irrigation_need": "Normal Schedule"},
    }