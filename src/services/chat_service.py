"""
Chat / Conversational AI service for AI WellnessVision.

Generates health-focused AI responses using Gemini as primary,
with a comprehensive rule-based fallback when the API is unavailable.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Optional Gemini import
# ──────────────────────────────────────────────
try:
    import google.generativeai as genai

    _api_key = os.environ.get("GEMINI_API_KEY")
    if _api_key:
        genai.configure(api_key=_api_key)
        _GEMINI_AVAILABLE = True
    else:
        _GEMINI_AVAILABLE = False
except ImportError:
    _GEMINI_AVAILABLE = False
    genai = None  # type: ignore[assignment]


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

async def generate_health_response(user_message: str) -> str:
    """Generate an intelligent health/wellness response.

    Strategy: Gemini AI → enhanced rule-based fallback.
    """
    if _GEMINI_AVAILABLE:
        try:
            return await _gemini_response(user_message)
        except Exception as exc:
            logger.warning("Gemini AI error (%s), using rule-based fallback", exc)

    return generate_enhanced_response(user_message)


# ──────────────────────────────────────────────
# Gemini path
# ──────────────────────────────────────────────

async def _gemini_response(user_message: str) -> str:
    """Call Gemini generative model with a health-focused system prompt."""
    model = genai.GenerativeModel("models/gemini-2.5-flash")

    health_prompt = (
        "You are a helpful AI health and wellness assistant. "
        "Provide accurate, helpful, and safe health information. "
        "Always remind users to consult healthcare professionals for serious concerns.\n\n"
        f"User question: {user_message}\n\n"
        "Please provide a helpful response about health and wellness. "
        "Keep it informative but not too long (2-3 paragraphs max). "
        "Always include a disclaimer to consult healthcare professionals when appropriate."
    )

    response = model.generate_content(health_prompt)
    if response and response.text:
        return response.text.strip()

    raise ValueError("Empty Gemini response")


# ──────────────────────────────────────────────
# Rule-based fallback
# ──────────────────────────────────────────────

def generate_enhanced_response(user_message: str) -> str:
    """Generate smart health responses using enhanced keyword matching."""
    msg = user_message.lower()

    # ── Sleep / rest ──
    if _matches(msg, ["sleep", "tired", "insomnia", "rest", "fatigue", "exhausted"]):
        responses = [
            (
                "I understand you're having sleep concerns. Here are some evidence-based strategies:\n\n"
                "**Sleep Hygiene Fundamentals:**\n"
                "• Maintain a consistent sleep schedule — same bedtime and wake time daily\n"
                "• Create an optimal sleep environment: cool (65-68°F), dark, and quiet\n"
                "• Develop a relaxing bedtime routine without screens for 1 hour before sleep\n\n"
                "**Daytime Habits That Improve Sleep:**\n"
                "• Get natural sunlight exposure in the morning\n"
                "• Avoid caffeine after 2 PM and large meals before bedtime\n"
                "• Regular exercise helps, but not within 3 hours of sleep\n\n"
                "If sleep issues persist despite good habits, consider consulting a healthcare provider."
            ),
            (
                "Sleep quality significantly impacts your overall health. Practical tips:\n\n"
                "**Creating Better Sleep:**\n"
                "• Stick to a regular sleep-wake cycle, even on weekends\n"
                "• Make your bedroom a sleep sanctuary — cool, dark, comfortable\n"
                "• Try relaxation techniques like deep breathing or gentle stretching\n\n"
                "**Common Sleep Disruptors to Avoid:**\n"
                "• Blue light from devices (use blue light filters if needed)\n"
                "• Caffeine late in the day (affects sleep even 6 hours later)\n"
                "• Irregular sleep patterns that confuse your body's natural rhythm\n\n"
                "Remember, quality sleep is as important as diet and exercise."
            ),
        ]
        return responses[hash(user_message) % len(responses)]

    # ── Nutrition / diet ──
    if _matches(msg, ["diet", "food", "nutrition", "eat", "meal", "hungry", "weight"]):
        responses = [
            (
                "Great question about nutrition! Current research for optimal health:\n\n"
                "**Building Balanced Meals:**\n"
                "• Fill half your plate with colorful vegetables and fruits\n"
                "• Include lean proteins like fish, poultry, beans, or tofu\n"
                "• Choose whole grains over refined ones for sustained energy\n"
                "• Add healthy fats from nuts, seeds, avocado, or olive oil\n\n"
                "**Smart Eating Habits:**\n"
                "• Stay hydrated with 8-10 glasses of water daily\n"
                "• Eat mindfully — chew slowly and pay attention to hunger cues\n"
                "• Plan regular meals to maintain stable blood sugar\n\n"
                "A registered dietitian can provide personalised guidance."
            ),
            (
                "Nutrition plays a crucial role in how you feel daily:\n\n"
                "**The Foundation of Good Nutrition:**\n"
                "• Variety is key — eat different colours and types of foods\n"
                "• Focus on whole, minimally processed foods when possible\n"
                "• Balance macronutrients: carbs for energy, protein for muscle, healthy fats for brain\n\n"
                "**Practical Tips:**\n"
                "• Meal prep helps you make healthier choices when busy\n"
                "• Listen to your body's hunger and fullness signals\n"
                "• Stay consistent rather than aiming for perfection\n\n"
                "Sustainable changes work better than drastic diets."
            ),
        ]
        return responses[hash(user_message) % len(responses)]

    # ── Exercise / fitness ──
    if _matches(msg, ["exercise", "workout", "fitness", "gym", "muscle", "strength", "cardio"]):
        return (
            "For effective fitness and exercise:\n\n"
            "• **Start Gradually**: Begin with 150 minutes of moderate activity weekly\n"
            "• **Strength Training**: Include resistance exercises 2-3 times per week\n"
            "• **Variety**: Mix cardio, strength, and flexibility exercises\n"
            "• **Recovery**: Allow rest days between intense workouts and prioritise sleep\n\n"
            "Always consult your doctor before starting a new exercise programme."
        )

    # ── Mental health / stress ──
    if _matches(msg, ["stress", "anxiety", "mental", "mood", "depression", "worried", "overwhelmed"]):
        return (
            "For mental wellness and stress management:\n\n"
            "• **Mindfulness**: Practice deep breathing or meditation for 10-15 minutes daily\n"
            "• **Social Connection**: Maintain relationships, seek support when needed\n"
            "• **Physical Activity**: Regular exercise significantly reduces stress\n"
            "• **Professional Help**: Don't hesitate to speak with a counsellor or therapist\n\n"
            "If you're experiencing persistent mental health concerns, please reach out to a professional."
        )

    # ── Skin ──
    if _matches(msg, ["skin", "acne", "skincare", "face", "dry", "oily"]):
        return (
            "For healthy skin care:\n\n"
            "• **Gentle Cleansing**: Use a mild cleanser twice daily\n"
            "• **Moisturise**: Apply moisturiser daily, even for oily skin\n"
            "• **Sun Protection**: Use SPF 30+ sunscreen daily\n"
            "• **Hydration**: Drink plenty of water and eat antioxidant-rich foods\n\n"
            "For persistent issues, consult a dermatologist."
        )

    # ── Heart health ──
    if _matches(msg, ["heart", "blood pressure", "cholesterol", "cardio", "chest"]):
        return (
            "For heart health:\n\n"
            "• **Regular Exercise**: Aim for 150 minutes of moderate aerobic activity weekly\n"
            "• **Heart-Healthy Diet**: Focus on fruits, vegetables, whole grains\n"
            "• **Limit Sodium**: Keep under 2,300 mg daily\n"
            "• **Manage Stress**: Practice relaxation techniques\n\n"
            "Always follow your doctor's recommendations for heart health."
        )

    # ── Catch-all ──
    responses = [
        (
            f'Thank you for your question about "{user_message}". '
            "I'm here to help with health and wellness guidance!\n\n"
            "**I can assist you with:**\n"
            "• Sleep optimisation and energy management\n"
            "• Nutrition and healthy eating strategies\n"
            "• Exercise and fitness recommendations\n"
            "• Stress management and mental wellness\n\n"
            "Could you tell me more about what specific aspect of health you're interested in?\n\n"
            "Remember, I provide general wellness information. "
            "For medical concerns, always consult qualified healthcare professionals."
        ),
        (
            f'I appreciate you reaching out about "{user_message}". '
            "Health and wellness are important!\n\n"
            "**Here's how I can help:**\n"
            "• Evidence-based wellness information\n"
            "• Practical tips for healthy living\n"
            "• Guidance on nutrition, sleep, exercise, and mental health\n\n"
            "Could you share a bit more detail? The more specific, the better I can help.\n\n"
            "I always recommend consulting healthcare professionals for personalised advice."
        ),
    ]
    return responses[hash(user_message) % len(responses)]


# ──────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────

def _matches(text: str, keywords: list[str]) -> bool:
    """Return True if *text* contains any of the *keywords*."""
    return any(kw in text for kw in keywords)
