import os
import random
from datetime import datetime, timedelta

CROP_DATABASE = {
    "Wheat": {"total_days": 120, "stages": {"Seedling": 20, "Vegetative": 45, "Flowering": 85, "Maturity": 115}},
    "Rice": {"total_days": 150, "stages": {"Seedling": 25, "Vegetative": 60, "Flowering": 105, "Maturity": 140}},
    "Maize": {"total_days": 100, "stages": {"Seedling": 15, "Vegetative": 40, "Flowering": 75, "Maturity": 95}}
}

def analyze_crop_logic(file_path):
    crop = random.choice(list(CROP_DATABASE.keys()))
    stage = random.choice(["Seedling", "Vegetative", "Flowering", "Maturity"])
    
    lifecycle = CROP_DATABASE[crop]
    estimated_age = lifecycle["stages"][stage]
    days_left = lifecycle["total_days"] - estimated_age
    
    return {
        "crop_type": crop,
        "health_score": random.randint(75, 98),
        "growth_stage": stage,
        "estimated_age": estimated_age,
        "days_to_harvest": days_left,
        "expected_harvest": (datetime.now() + timedelta(days=days_left)).strftime("%d %b %Y"),
        "risk_percent": random.randint(2, 15),
        "advisory": f"Optimal nutrient management required for {stage} stage."
    }