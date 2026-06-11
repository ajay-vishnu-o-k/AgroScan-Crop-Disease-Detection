# =========================================================
# AgroScan Response Templates
# =========================================================

from data.disease_data import DISEASE_DATABASE

# =========================================================
# Format Title
# =========================================================

def format_title(text):
    return text.replace("_", " ").title()


# =========================================================
# Greeting Response
# =========================================================

def generate_greeting_response():

    response = (
        "🌱 Hello! I am AgroScan Agricultural Assistant.\n\n"
        "I can help you with:\n\n"
        "✅ Crop Diseases\n"
        "✅ Disease Symptoms\n"
        "✅ Disease Treatment\n"
        "✅ Irrigation Guidance\n"
        "✅ Weather Conditions\n"
        "✅ Crop Management\n\n"
        "🌾 Supported Crops:\n\n"
        "- Wheat\n"
        "- Rice\n"
        "- Potato\n"
        "- Tomato"
    )

    return response


# =========================================================
# Generate Disease Response
# =========================================================

def generate_disease_response(crop, disease, intent):

    disease_info = DISEASE_DATABASE[crop][disease]
    disease_name = disease.replace("_", " ").title()

    def convert_to_bullets(text):

        if not text:
            return "• No information available."

        sentences = text.split(". ")
        bullet_text = ""

        for sentence in sentences:
            sentence = sentence.strip()

            if sentence:
                if not sentence.endswith("."):
                    sentence += "."
                bullet_text += f"• {sentence}\n"

        return bullet_text

    response = (
        f"🌾 Crop: {crop.title()}\n"
        f"🦠 Disease: {disease_name}\n\n"
    )

    if intent == "symptoms":
        response += f"🔍 Symptoms:\n\n{convert_to_bullets(disease_info.get('symptoms'))}"
        return response

    if intent == "causes":
        response += f"⚠ Causes:\n\n{convert_to_bullets(disease_info.get('causes'))}"
        return response

    if intent == "treatment":
        response += f"💊 Treatment:\n\n{convert_to_bullets(disease_info.get('treatment'))}"
        return response

    if intent == "prevention":
        response += f"🛡 Prevention:\n\n{convert_to_bullets(disease_info.get('prevention'))}"
        return response

    if intent == "weather":
        response += f"🌦 Weather Conditions:\n\n{convert_to_bullets(disease_info.get('weather_conditions'))}"
        return response

    response += (
        "🔍 Symptoms:\n\n"
        f"{convert_to_bullets(disease_info.get('symptoms'))}\n"
        "⚠ Causes:\n\n"
        f"{convert_to_bullets(disease_info.get('causes'))}\n"
        "💊 Treatment:\n\n"
        f"{convert_to_bullets(disease_info.get('treatment'))}\n"
        "🛡 Prevention:\n\n"
        f"{convert_to_bullets(disease_info.get('prevention'))}"
    )

    if "weather_conditions" in disease_info:
        response += (
            "\n🌦 Weather Conditions:\n\n"
            f"{convert_to_bullets(disease_info.get('weather_conditions'))}"
        )

    if "affected_parts" in disease_info:
        response += (
            "\n🌿 Affected Parts:\n\n"
            f"{convert_to_bullets(disease_info.get('affected_parts'))}"
        )

    return response


# =========================================================
# 🌱 NEW: Crop Management Response (ADDED FIX)
# =========================================================

def generate_crop_management_response(crop):

    crop = crop.lower().strip()

    management_data = {

        "wheat": [
            "Prepare well-drained loamy soil",
            "Use certified seeds for sowing",
            "Irrigate at crown root, tillering, and grain filling stages",
            "Apply balanced NPK fertilizer",
            "Control weeds early stage",
            "Monitor rust diseases regularly",
            "Harvest when grains turn golden"
        ],

        "rice": [
            "Maintain puddled soil conditions",
            "Use nursery transplanting method",
            "Keep 2–5 cm water level in field",
            "Apply nitrogen in split doses",
            "Control weeds using flooding technique",
            "Monitor bacterial leaf blight",
            "Harvest when 80–85% grains mature"
        ],

        "potato": [
            "Use well-drained sandy loam soil",
            "Plant disease-free seed tubers",
            "Avoid water stagnation",
            "Maintain moisture during tuber formation",
            "Apply potassium-rich fertilizer",
            "Control late blight using fungicides",
            "Harvest when foliage turns yellow"
        ],

        "tomato": [
            "Use nursery-raised healthy seedlings",
            "Provide staking for plant support",
            "Use drip irrigation system",
            "Avoid overhead watering",
            "Apply balanced fertilizer schedule",
            "Control early and late blight",
            "Harvest when fruits are fully colored"
        ]
    }

    if crop not in management_data:
        return f"Crop management data not available for {crop.title()}"

    return (
        f"🌱 Crop Management Guide for {crop.title()}:\n\n"
        + "\n".join([f"• {item}" for item in management_data[crop]])
    )


# =========================================================
# Irrigation Response
# =========================================================

def generate_irrigation_response(crop, user_text):

    irrigation_data = {

        "wheat": [
            "Provide irrigation during crown root initiation stage.",
            "Avoid water stagnation in the field.",
            "Critical irrigation stages are tillering and grain filling.",
            "Moderate soil moisture improves wheat yield."
        ],

        "rice": [
            "Rice requires standing water during early growth stages.",
            "Maintain 2–5 cm water level in paddy fields.",
            "Drain excess water before harvesting.",
            "Frequent irrigation is important during flowering stage."
        ],

        "potato": [
            "Potato requires regular irrigation during tuber formation.",
            "Avoid excessive watering to prevent tuber rot.",
            "Maintain moist but well-drained soil.",
            "Reduce irrigation before harvesting."
        ],

        "tomato": [
            "Tomato plants require consistent soil moisture.",
            "Use drip irrigation for better water efficiency.",
            "Avoid overhead irrigation to reduce fungal diseases.",
            "Water deeply during flowering and fruit development."
        ]
    }

    if crop not in irrigation_data:
        return f"Irrigation information is not available for {crop.title()}."

    irrigation_points = "\n".join(
        [f"• {point}" for point in irrigation_data[crop]]
    )

    return f"💧 Irrigation Information For {crop.title()}\n\n{irrigation_points}"


# =========================================================
# Unknown Response
# =========================================================

def generate_unknown_response():

    return (
        "I could not clearly understand your question.\n\n"
        "Please ask agriculture-related questions.\n\n"
        "Examples:\n\n"
        "• Potato late blight treatment\n"
        "• Wheat yellow rust symptoms\n"
        "• Rice irrigation\n"
        "• Tomato fertilizer"
    )