import requests
from datetime import datetime
import os

SERP_API_KEY = os.getenv("SERP_API_KEY", "567d956b95540c8e4d85f3b3390aa705b61a230572a49df3842570a8ca380646")


def get_government_schemes():
    """Fetch latest government agricultural schemes using SerpAPI + comprehensive fallback."""

    # Always return comprehensive known schemes + any fresh results from SerpAPI
    schemes = get_known_schemes()

    # Try to add fresh results from SerpAPI
    try:
        url = "https://serpapi.com/search.json"
        params = {
            "q": "latest government agriculture scheme India farmer 2025 2026",
            "hl": "en",
            "gl": "in",
            "num": 10,
            "api_key": SERP_API_KEY,
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get("organic_results", [])

            existing_titles = {s["title"].lower() for s in schemes}

            for res in results[:8]:
                title = res.get("title", "")
                if not title or title.lower() in existing_titles:
                    continue
                schemes.append({
                    "title": title,
                    "description": res.get("snippet", ""),
                    "link": res.get("link", ""),
                    "source": res.get("source", ""),
                    "date": res.get("date", datetime.now().strftime("%d %b %Y")),
                    "category": "Latest",
                    "benefit": "Check details on website",
                })
    except Exception as e:
        print(f"[AgriShield] SerpAPI fetch error: {e}")

    return schemes


def get_known_schemes():
    """Comprehensive list of major Indian government schemes for farmers."""
    return [
        {
            "title": "PM-KISAN Samman Nidhi Yojana",
            "description": "Har saal ₹6,000 seedha bank mein — 3 installments of ₹2,000 each. Sabhi small & marginal farmers ke liye. 12+ crore farmers already benefited.",
            "link": "https://pmkisan.gov.in/",
            "source": "pmkisan.gov.in",
            "date": "Active",
            "category": "Income Support",
            "benefit": "₹6,000/year",
        },
        {
            "title": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            "description": "Crop insurance scheme — baarish, drought, cyclone ya kisi bhi natural disaster se crop kharab ho toh pura compensation milega. Premium bahut kam — Kharif 2%, Rabi 1.5%.",
            "link": "https://pmfby.gov.in/",
            "source": "pmfby.gov.in",
            "date": "Active",
            "category": "Crop Insurance",
            "benefit": "Low premium crop insurance",
        },
        {
            "title": "Kisan Credit Card (KCC) Scheme",
            "description": "₹3 lakh tak ka loan sirf 4% interest rate pe. Animal husbandry aur fisheries farmers bhi eligible. Koi bhi bank se apply kar sakte ho.",
            "link": "https://www.pmkisan.gov.in/",
            "source": "india.gov.in",
            "date": "Active",
            "category": "Credit",
            "benefit": "Loan at 4% interest",
        },
        {
            "title": "Soil Health Card Scheme",
            "description": "Free soil testing — pata chalega ki soil mein kya kami hai, konsa fertilizer use karna hai. 12 nutrients ki testing hoti hai. Har 2 saal mein update hota hai.",
            "link": "https://soilhealth.dac.gov.in/",
            "source": "soilhealth.dac.gov.in",
            "date": "Active",
            "category": "Soil & Input",
            "benefit": "Free soil testing",
        },
        {
            "title": "PM Krishi Sinchai Yojana (PMKSY)",
            "description": "Har Khet Ko Pani — drip irrigation, sprinkler system pe 55-75% subsidy. Micro irrigation se 30-50% pani bachta hai aur yield 20-50% badhti hai.",
            "link": "https://pmksy.gov.in/",
            "source": "pmksy.gov.in",
            "date": "Active",
            "category": "Irrigation",
            "benefit": "55-75% subsidy on irrigation",
        },
        {
            "title": "E-NAM (National Agriculture Market)",
            "description": "Online mandi — apni fasal ka best price milega. 1,361 mandis connected. Seedha apne phone se sell kar sakte ho. No middleman required.",
            "link": "https://enam.gov.in/",
            "source": "enam.gov.in",
            "date": "Active",
            "category": "Market",
            "benefit": "Best price for your crops",
        },
        {
            "title": "Paramparagat Krishi Vikas Yojana (PKVY)",
            "description": "Organic farming ke liye ₹50,000/hectare for 3 years. Cluster mein 50 ya zyada farmer milke apply karte hain. Training + certification free.",
            "link": "https://pgsindia-ncof.gov.in/",
            "source": "pgsindia-ncof.gov.in",
            "date": "Active",
            "category": "Organic Farming",
            "benefit": "₹50,000/hectare for 3 years",
        },
        {
            "title": "Agriculture Infrastructure Fund (AIF)",
            "description": "₹1 lakh crore ka fund — cold storage, warehouse, processing unit banane ke liye 3% interest subsidy + ₹2 crore tak ka loan. 15 saal repayment.",
            "link": "https://agriinfra.dac.gov.in/",
            "source": "agriinfra.dac.gov.in",
            "date": "Active",
            "category": "Infrastructure",
            "benefit": "3% interest subsidy, ₹2Cr loan",
        },
        {
            "title": "PM Kisan Maandhan Yojana",
            "description": "Pension scheme for farmers — 60 saal ke baad ₹3,000/month pension. 18-40 age ke beech join kar sakte ho. ₹55-200/month contribution.",
            "link": "https://maandhan.in/",
            "source": "maandhan.in",
            "date": "Active",
            "category": "Pension",
            "benefit": "₹3,000/month pension after 60",
        },
        {
            "title": "Sub Mission on Agricultural Mechanization (SMAM)",
            "description": "Tractor, harvester, thresher aur baaki farm machines pe 40-50% subsidy. Custom Hiring Centre se machines rent pe bhi mil sakti hain.",
            "link": "https://agrimachinery.nic.in/",
            "source": "agrimachinery.nic.in",
            "date": "Active",
            "category": "Mechanization",
            "benefit": "40-50% subsidy on farm machines",
        },
        {
            "title": "National Mission on Sustainable Agriculture (NMSA)",
            "description": "Climate change se bachne ke liye smart farming techniques. Rain water harvesting, crop diversification, aur resource conservation pe focus.",
            "link": "https://nmsa.dac.gov.in/",
            "source": "nmsa.dac.gov.in",
            "date": "Active",
            "category": "Sustainability",
            "benefit": "Climate-smart farming support",
        },
        {
            "title": "Rashtriya Krishi Vikas Yojana (RKVY)",
            "description": "States ko agriculture development ke liye funding. New technology, agri-startups, aur farmer training programmes ke liye grants available.",
            "link": "https://rkvy.nic.in/",
            "source": "rkvy.nic.in",
            "date": "Active",
            "category": "Development",
            "benefit": "Agri development funding",
        },
    ]
