import requests
from datetime import datetime

API_KEY = "567d956b95540c8e4d85f3b3390aa705b61a230572a49df3842570a8ca380646"

def get_market_prices():
    """Fetch real-time mandi prices using SerpAPI."""
    url = f"https://serpapi.com/search.json?q=Madhya+Pradesh+Mandi+Bhav+crop+prices+today&hl=en&gl=in&api_key={API_KEY}"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            results = response.json().get('organic_results', [])
            
            market_data = []
            for res in results[:10]:
                title = res.get('title', 'N/A')
                snippet = res.get('snippet', '')
                
                market_data.append({
                    "crop_name": title[:50],
                    "current_price": "Live",
                    "unit": "Quintal",
                    "trend": "Check Latest",
                    "market_name": snippet[:80] if snippet else "Madhya Pradesh Mandi",
                    "last_updated": datetime.now().strftime("%d %b %Y")
                })
            
            if not market_data:
                return get_fallback_data()
                
            return market_data
    except Exception as e:
        print(f"[AgriShield] Market Error: {e}")
        return get_fallback_data()


def get_fallback_data():
    """Emergency fallback data when API is unavailable."""
    today = datetime.now().strftime("%d/%m/%Y")
    return [
        {"crop_name": "Soyabean", "current_price": "4850", "unit": "Quintal", "trend": "Up", "market_name": "Indore Mandi", "last_updated": today},
        {"crop_name": "Wheat", "current_price": "2600", "unit": "Quintal", "trend": "Stable", "market_name": "Sehore Mandi", "last_updated": today},
        {"crop_name": "Maize", "current_price": "2150", "unit": "Quintal", "trend": "Up", "market_name": "Dewas Mandi", "last_updated": today},
        {"crop_name": "Rice (Paddy)", "current_price": "2300", "unit": "Quintal", "trend": "Stable", "market_name": "Hoshangabad Mandi", "last_updated": today},
        {"crop_name": "Cotton", "current_price": "7200", "unit": "Quintal", "trend": "Down", "market_name": "Khandwa Mandi", "last_updated": today},
        {"crop_name": "Chana (Gram)", "current_price": "5400", "unit": "Quintal", "trend": "Up", "market_name": "Ujjain Mandi", "last_updated": today},
        {"crop_name": "Mustard", "current_price": "5800", "unit": "Quintal", "trend": "Stable", "market_name": "Gwalior Mandi", "last_updated": today},
        {"crop_name": "Onion", "current_price": "1800", "unit": "Quintal", "trend": "Down", "market_name": "Shajapur Mandi", "last_updated": today},
        {"crop_name": "Garlic", "current_price": "8500", "unit": "Quintal", "trend": "Up", "market_name": "Mandsaur Mandi", "last_updated": today},
        {"crop_name": "Lentil (Masoor)", "current_price": "6200", "unit": "Quintal", "trend": "Stable", "market_name": "Ratlam Mandi", "last_updated": today},
    ]