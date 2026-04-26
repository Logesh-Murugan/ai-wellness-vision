#!/usr/bin/env python3
"""
Food Analyzer — Inference Module
=================================
Inference wrapper for the EfficientNet-B0 Food-101 classifier.
Combines visual food recognition with the Open Food Facts API and
an offline fallback dictionary to provide nutritional insights.
"""

import io
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import requests
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
import albumentations as A
from albumentations.pytorch import ToTensorV2
import timm

logger = logging.getLogger(__name__)

# ===================================================================
# Offline Fallback Nutrition Data (Top 50 Food-101 Categories)
# Values are approximate per 100g
# ===================================================================
OFFLINE_NUTRITION_DB = {
    "apple_pie": {"calories": 237, "protein": 2.4, "fat": 11.0, "carbs": 34.0, "fiber": 1.5, "sugar": 15.0},
    "baby_back_ribs": {"calories": 290, "protein": 22.0, "fat": 21.0, "carbs": 3.0, "fiber": 0.0, "sugar": 2.5},
    "baklava": {"calories": 428, "protein": 6.8, "fat": 28.0, "carbs": 38.0, "fiber": 2.0, "sugar": 17.0},
    "beef_carpaccio": {"calories": 140, "protein": 20.0, "fat": 6.0, "carbs": 1.0, "fiber": 0.0, "sugar": 0.0},
    "beef_tartare": {"calories": 160, "protein": 18.0, "fat": 9.0, "carbs": 1.5, "fiber": 0.2, "sugar": 0.5},
    "beet_salad": {"calories": 90, "protein": 2.5, "fat": 5.0, "carbs": 9.0, "fiber": 2.5, "sugar": 6.0},
    "beignets": {"calories": 360, "protein": 4.5, "fat": 18.0, "carbs": 44.0, "fiber": 1.0, "sugar": 16.0},
    "bibimbap": {"calories": 150, "protein": 5.5, "fat": 4.5, "carbs": 22.0, "fiber": 2.0, "sugar": 2.5},
    "bread_pudding": {"calories": 250, "protein": 5.0, "fat": 11.0, "carbs": 33.0, "fiber": 1.5, "sugar": 18.0},
    "breakfast_burrito": {"calories": 220, "protein": 10.0, "fat": 11.0, "carbs": 20.0, "fiber": 1.5, "sugar": 2.0},
    "bruschetta": {"calories": 180, "protein": 4.5, "fat": 8.0, "carbs": 22.0, "fiber": 2.0, "sugar": 2.0},
    "caesar_salad": {"calories": 140, "protein": 4.0, "fat": 11.0, "carbs": 6.0, "fiber": 1.5, "sugar": 1.5},
    "cannoli": {"calories": 310, "protein": 5.0, "fat": 16.0, "carbs": 36.0, "fiber": 1.0, "sugar": 14.0},
    "caprese_salad": {"calories": 150, "protein": 8.0, "fat": 11.0, "carbs": 4.0, "fiber": 1.0, "sugar": 3.0},
    "carrot_cake": {"calories": 415, "protein": 4.5, "fat": 23.0, "carbs": 50.0, "fiber": 1.5, "sugar": 30.0},
    "ceviche": {"calories": 95, "protein": 15.0, "fat": 2.0, "carbs": 4.0, "fiber": 0.5, "sugar": 1.0},
    "cheesecake": {"calories": 321, "protein": 5.5, "fat": 22.0, "carbs": 25.0, "fiber": 0.0, "sugar": 18.0},
    "cheese_plate": {"calories": 350, "protein": 21.0, "fat": 29.0, "carbs": 2.0, "fiber": 0.0, "sugar": 0.5},
    "chicken_curry": {"calories": 140, "protein": 12.0, "fat": 8.0, "carbs": 6.0, "fiber": 1.0, "sugar": 1.5},
    "chicken_quesadilla": {"calories": 280, "protein": 15.0, "fat": 14.0, "carbs": 23.0, "fiber": 2.0, "sugar": 2.0},
    "chicken_wings": {"calories": 290, "protein": 18.0, "fat": 19.0, "carbs": 11.0, "fiber": 0.5, "sugar": 1.0},
    "chocolate_cake": {"calories": 371, "protein": 5.3, "fat": 15.0, "carbs": 53.0, "fiber": 3.0, "sugar": 35.0},
    "chocolate_mousse": {"calories": 340, "protein": 4.5, "fat": 24.0, "carbs": 28.0, "fiber": 2.0, "sugar": 23.0},
    "churros": {"calories": 390, "protein": 4.5, "fat": 20.0, "carbs": 47.0, "fiber": 1.5, "sugar": 15.0},
    "clam_chowder": {"calories": 110, "protein": 4.5, "fat": 5.5, "carbs": 10.0, "fiber": 1.0, "sugar": 2.0},
    "club_sandwich": {"calories": 240, "protein": 12.0, "fat": 11.0, "carbs": 23.0, "fiber": 2.0, "sugar": 3.0},
    "crab_cakes": {"calories": 200, "protein": 13.0, "fat": 12.0, "carbs": 9.0, "fiber": 0.5, "sugar": 1.0},
    "creme_brulee": {"calories": 330, "protein": 4.0, "fat": 26.0, "carbs": 20.0, "fiber": 0.0, "sugar": 18.0},
    "croque_madame": {"calories": 280, "protein": 14.0, "fat": 16.0, "carbs": 20.0, "fiber": 1.5, "sugar": 2.5},
    "cup_cakes": {"calories": 305, "protein": 3.5, "fat": 13.0, "carbs": 44.0, "fiber": 0.5, "sugar": 28.0},
    "deviled_eggs": {"calories": 220, "protein": 11.0, "fat": 18.0, "carbs": 2.0, "fiber": 0.0, "sugar": 1.0},
    "donuts": {"calories": 420, "protein": 4.8, "fat": 22.0, "carbs": 51.0, "fiber": 1.5, "sugar": 26.0},
    "dumplings": {"calories": 180, "protein": 7.0, "fat": 8.0, "carbs": 20.0, "fiber": 1.0, "sugar": 1.0},
    "edamame": {"calories": 121, "protein": 11.9, "fat": 5.2, "carbs": 8.9, "fiber": 5.2, "sugar": 2.2},
    "eggs_benedict": {"calories": 250, "protein": 11.0, "fat": 17.0, "carbs": 13.0, "fiber": 1.0, "sugar": 1.5},
    "escargots": {"calories": 180, "protein": 12.0, "fat": 14.0, "carbs": 2.0, "fiber": 0.0, "sugar": 0.0},
    "falafel": {"calories": 333, "protein": 13.3, "fat": 17.5, "carbs": 31.8, "fiber": 8.0, "sugar": 2.0},
    "filet_mignon": {"calories": 267, "protein": 26.0, "fat": 17.0, "carbs": 0.0, "fiber": 0.0, "sugar": 0.0},
    "fish_and_chips": {"calories": 220, "protein": 10.0, "fat": 12.0, "carbs": 18.0, "fiber": 1.5, "sugar": 0.5},
    "foie_gras": {"calories": 462, "protein": 11.4, "fat": 43.8, "carbs": 4.7, "fiber": 0.0, "sugar": 0.5},
    "french_fries": {"calories": 312, "protein": 3.4, "fat": 15.0, "carbs": 41.0, "fiber": 3.8, "sugar": 0.3},
    "french_onion_soup": {"calories": 80, "protein": 3.5, "fat": 4.0, "carbs": 8.0, "fiber": 1.0, "sugar": 3.0},
    "french_toast": {"calories": 230, "protein": 7.0, "fat": 9.0, "carbs": 30.0, "fiber": 2.0, "sugar": 10.0},
    "fried_calamari": {"calories": 210, "protein": 12.0, "fat": 12.0, "carbs": 13.0, "fiber": 0.5, "sugar": 0.5},
    "fried_rice": {"calories": 160, "protein": 4.5, "fat": 5.0, "carbs": 24.0, "fiber": 1.0, "sugar": 1.0},
    "frozen_yogurt": {"calories": 130, "protein": 3.5, "fat": 2.5, "carbs": 23.0, "fiber": 0.0, "sugar": 18.0},
    "garlic_bread": {"calories": 350, "protein": 8.0, "fat": 16.0, "carbs": 42.0, "fiber": 2.5, "sugar": 2.0},
    "gnocchi": {"calories": 170, "protein": 4.0, "fat": 3.0, "carbs": 32.0, "fiber": 2.0, "sugar": 1.0},
    "greek_salad": {"calories": 110, "protein": 3.0, "fat": 9.0, "carbs": 5.0, "fiber": 1.5, "sugar": 2.5},
    "grilled_cheese_sandwich": {"calories": 320, "protein": 13.0, "fat": 18.0, "carbs": 26.0, "fiber": 1.5, "sugar": 3.0},
}


# ===================================================================
# Helper Functions
# ===================================================================
def estimate_portion_g(food_name: str) -> float:
    """Provides a rough estimate of a standard portion size in grams."""
    food = food_name.lower()
    if any(x in food for x in ["soup", "stew", "curry"]):
        return 300.0
    elif any(x in food for x in ["cake", "dessert", "pie", "ice_cream", "mousse"]):
        return 120.0
    elif any(x in food for x in ["salad"]):
        return 150.0
    elif any(x in food for x in ["steak", "ribs", "chicken"]):
        return 220.0
    elif any(x in food for x in ["snack", "chips", "fries"]):
        return 100.0
    return 200.0


def calculate_health_score(nutrition: Dict) -> Tuple[int, str, List[str]]:
    """Calculates a health score (0-10) and provides recommendations."""
    score = 10.0
    recs = []
    
    cal = float(nutrition.get("calories") or 0)
    pro = float(nutrition.get("protein") or 0)
    fat = float(nutrition.get("fat") or 0)
    sug = float(nutrition.get("sugar") or 0)
    fib = float(nutrition.get("fiber") or 0)

    # Penalties
    if cal > 300:
        score -= 2
        recs.append("High in calories. Consider eating a smaller portion.")
    if fat > 15:
        score -= 1.5
        recs.append("High fat content. Enjoy in moderation.")
    if sug > 15:
        score -= 2
        recs.append("High sugar content. Not recommended for daily consumption.")
    
    # Bonuses
    if pro > 15:
        score += 1
        recs.append("Great source of protein.")
    if fib > 4:
        score += 1
        recs.append("High in fiber, good for digestion.")
    
    score = max(1, min(10, round(score)))
    
    if score >= 8:
        label = "Healthy"
    elif score >= 5:
        label = "Moderate"
    else:
        label = "Indulgent"

    if not recs:
        recs.append("A balanced choice as part of a varied diet.")

    return score, label, recs


class FoodAnalyzer:
    """
    Production-ready food recognition and nutrition analysis module.
    """
    def __init__(
        self,
        model_path: str = "models/food_model.pth",
        device: Optional[str] = None
    ):
        self.model_path = Path(model_path)
        self.device = torch.device(device if device else ("cuda" if torch.cuda.is_available() else "cpu"))
        
        self.model = None
        self.class_names = []
        
        self._load_model()
        self.transform = A.Compose([
            A.Resize(256, 256),
            A.CenterCrop(224, 224),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2(),
        ])

    def _load_model(self):
        if not self.model_path.exists():
            logger.warning(f"Food model checkpoint not found at {self.model_path}.")
            return
            
        logger.info(f"Loading food model from {self.model_path}")
        checkpoint = torch.load(self.model_path, map_location=self.device, weights_only=False)
        
        self.class_names = checkpoint.get("class_names", [])
        num_classes = len(self.class_names) if self.class_names else 101
        
        # Load backbone
        self.model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=num_classes)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(self.device)
        self.model.eval()
        
        logger.info("✅ Food analyzer loaded successfully.")

    def is_ready(self) -> bool:
        return self.model is not None

    def _preprocess(self, image_bytes: bytes) -> torch.Tensor:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_np = np.array(image)
        augmented = self.transform(image=image_np)
        return augmented["image"].unsqueeze(0)

    def _get_nutrition(self, food_name: str) -> Dict:
        """Fetches nutritional data from Open Food Facts or fallback."""
        clean_name = food_name.replace("_", " ")
        url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={clean_name}&json=1&page_size=1"
        
        try:
            response = requests.get(url, timeout=3.0)
            if response.status_code == 200:
                data = response.json()
                if data.get("products") and len(data["products"]) > 0:
                    nutriments = data["products"][0].get("nutriments", {})
                    
                    return {
                        "calories": nutriments.get("energy-kcal_100g", 0),
                        "protein": nutriments.get("proteins_100g", 0),
                        "fat": nutriments.get("fat_100g", 0),
                        "carbs": nutriments.get("carbohydrates_100g", 0),
                        "fiber": nutriments.get("fiber_100g", 0),
                        "sugar": nutriments.get("sugars_100g", 0),
                    }
        except Exception as e:
            logger.warning(f"Open Food Facts API failed: {e}. Using offline fallback.")

        # Fallback
        if food_name in OFFLINE_NUTRITION_DB:
            return OFFLINE_NUTRITION_DB[food_name]
            
        # Default safe fallback
        return {"calories": 150, "protein": 5, "fat": 5, "carbs": 20, "fiber": 2, "sugar": 5}

    @torch.no_grad()
    def analyze(self, image_bytes: bytes) -> Dict:
        if not self.is_ready():
            return {"food_code": "error", "error": "Model not loaded."}

        try:
            tensor = self._preprocess(image_bytes).to(self.device)
            logits = self.model(tensor)
            probs = F.softmax(logits, dim=1)[0].cpu().numpy()
            
            top_idx = np.argmax(probs)
            confidence = float(probs[top_idx])
            
            food_code = self.class_names[top_idx] if self.class_names else str(top_idx)
            food_identified = food_code.replace("_", " ").title()

            # Nutritional Analysis
            nutrition_100g = self._get_nutrition(food_code)
            portion_g = estimate_portion_g(food_code)
            
            # Scale calories to portion
            cals_100g = nutrition_100g.get("calories") or 0
            est_calories = round((cals_100g / 100.0) * portion_g)
            
            # Health Score
            score, label, recs = calculate_health_score(nutrition_100g)

            return {
                "food_code": food_code,
                "food_identified": food_identified,
                "confidence": confidence,
                "nutrition_per_100g": nutrition_100g,
                "estimated_portion_g": portion_g,
                "estimated_calories": est_calories,
                "health_score": score,
                "health_label": label,
                "recommendations": recs
            }

        except Exception as e:
            logger.error(f"Food analysis failed: {e}")
            return {"food_code": "error", "error": str(e)}

if __name__ == "__main__":
    # Smoke test
    print("Food Analyzer script is ready.")
