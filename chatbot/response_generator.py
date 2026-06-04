# =========================================================
# AgroScan Final Intelligent Response Generator
# =========================================================

# =========================================================
# Import Databases
# =========================================================

from data.disease_data import DISEASE_DATABASE
from data.irrigation_data import IRRIGATION_DATA


# =========================================================
# Import NLP Modules
# =========================================================

from agriculture_filter import agriculture_filter

from entity_extractor import smart_entity_extractor

from intent_classifier import smart_intent_detection

from fuzzy_engine import fuzzy_pipeline

from context_memory import chat_memory


# =========================================================
# Format Helper
# =========================================================

def format_title(text):

    return text.replace("_", " ").title()


# =========================================================
# Greeting Response
# =========================================================

def generate_greeting_response():

    return (

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


# =========================================================
# Unknown Response
# =========================================================

def generate_unknown_response():

    return (

        "I could not clearly understand your question.\n\n"

        "Please ask questions related to:\n\n"

        "🌾 Wheat\n"
        "🌾 Rice\n"
        "🥔 Potato\n"
        "🍅 Tomato\n"
        "💧 Irrigation\n"
        "🦠 Crop Diseases\n"
        "🌦 Weather Conditions\n"
        "🌱 Agriculture"
    )


# =========================================================
# Disease Response Generator
# =========================================================

def generate_disease_response(crop, disease, intent):

    crop_data = DISEASE_DATABASE.get(crop)

    if not crop_data:

        return "Crop information not available."

    disease_data = crop_data.get(disease)

    if not disease_data:

        return (
            f"{format_title(disease)} information "
            f"is not available for {crop.title()}."
        )

    disease_name = format_title(disease)

    response = (

        f"🌾 Crop: {crop.title()}\n"
        f"🦠 Disease: {disease_name}\n\n"
    )

    # =====================================================
    # Symptoms
    # =====================================================

    if intent == "symptoms":

        response += (

            f"🔍 Symptoms:\n\n"

            f"{disease_data.get('symptoms', 'Information not available.')}"
        )

    # =====================================================
    # Causes
    # =====================================================

    elif intent == "causes":

        response += (

            f"⚠ Causes:\n\n"

            f"{disease_data.get('causes', 'Information not available.')}"
        )

    # =====================================================
    # Treatment
    # =====================================================

    elif intent == "treatment":

        response += (

            f"💊 Treatment:\n\n"

            f"{disease_data.get('treatment', 'Information not available.')}"
        )

    # =====================================================
    # Prevention
    # =====================================================

    elif intent == "prevention":

        response += (

            f"🛡 Prevention:\n\n"

            f"{disease_data.get('prevention', 'Information not available.')}"
        )

    # =====================================================
    # Weather Conditions
    # =====================================================

    elif intent == "weather":

        response += (

            f"🌦 Weather Conditions:\n\n"

            f"{disease_data.get('weather_conditions', 'Information not available.')}"
        )

    # =====================================================
    # Full Disease Information
    # =====================================================

    else:

        response += (

            f"🔍 Symptoms:\n"
            f"{disease_data.get('symptoms', 'N/A')}\n\n"

            f"⚠ Causes:\n"
            f"{disease_data.get('causes', 'N/A')}\n\n"

            f"💊 Treatment:\n"
            f"{disease_data.get('treatment', 'N/A')}\n\n"

            f"🛡 Prevention:\n"
            f"{disease_data.get('prevention', 'N/A')}"
        )

    return response


# =========================================================
# Irrigation Response Generator
# =========================================================

def generate_irrigation_response(crop, user_text):

    crop_data = IRRIGATION_DATA.get(crop)

    if not crop_data:

        return (
            f"Irrigation information for "
            f"{crop.title()} is not available."
        )

    response = f"🌾 Crop: {crop.title()}\n\n"

    user_text = user_text.lower()

    # =====================================================
    # Water Requirement
    # =====================================================

    if "water" in user_text:

        response += (

            f"💧 Water Requirement:\n\n"

            f"{crop_data['water_requirement']}"
        )

    # =====================================================
    # Irrigation Method
    # =====================================================

    elif "method" in user_text or "irrigation" in user_text:

        response += (

            f"🚿 Best Irrigation Method:\n\n"

            f"{crop_data['best_irrigation_method']}"
        )

    # =====================================================
    # Rainfall
    # =====================================================

    elif "rain" in user_text or "rainfall" in user_text:

        response += (

            f"🌧 Rainfall Effect:\n\n"

            f"{crop_data['rainfall_effect']}"
        )

    # =====================================================
    # Temperature
    # =====================================================

    elif "temperature" in user_text or "climate" in user_text:

        response += (

            f"🌡 Temperature Effect:\n\n"

            f"{crop_data['temperature_effect']}"
        )

    # =====================================================
    # Soil
    # =====================================================

    elif "soil" in user_text:

        response += (

            f"🌱 Suitable Soil:\n\n"

            f"{crop_data['soil_type']}"
        )

    # =====================================================
    # General Irrigation Information
    # =====================================================

    else:

        response += (

            f"💧 Water Requirement:\n"
            f"{crop_data['water_requirement']}\n\n"

            f"🚿 Irrigation Method:\n"
            f"{crop_data['best_irrigation_method']}\n\n"

            f"🌱 Suitable Soil:\n"
            f"{crop_data['soil_type']}\n\n"

            f"🌧 Rainfall Effect:\n"
            f"{crop_data['rainfall_effect']}\n\n"

            f"🌡 Temperature Effect:\n"
            f"{crop_data['temperature_effect']}"
        )

    return response


# =========================================================
# Main Chatbot Function
# =========================================================

def generate_chatbot_response(user_text):

    # =====================================================
    # STEP 1: FUZZY CORRECTION
    # =====================================================

    fuzzy_result = fuzzy_pipeline(user_text)

    corrected_text = fuzzy_result["corrected_text"]

    corrected_text_lower = corrected_text.lower().strip()

    # =====================================================
    # STEP 2: HANDLE CONFIRMATION REPLIES
    # =====================================================

    if chat_memory.needs_confirmation():

        possible_crops = chat_memory.get_possible_crops()

        user_text_lower = corrected_text.lower()

        for crop_name in possible_crops:

            if crop_name in user_text_lower:

                crop = crop_name

                disease = chat_memory.get_disease()

                intent = chat_memory.get_intent()

                chat_memory.set_crop(crop)

                chat_memory.set_confirmation(False)

                response = generate_disease_response(
                    crop,
                    disease,
                    intent
                )

                chat_memory.add_to_history(
                    user_text,
                    response
                )

                return response

    # =====================================================
    # STEP 3: GENERAL DISEASE QUESTION
    # =====================================================

    GENERAL_DISEASE_KEYWORDS = [

        "disease",
        "crop disease",
        "plant disease",
        "diseases",
        "crop diseases"
    ]

    for keyword in GENERAL_DISEASE_KEYWORDS:

        if keyword in corrected_text_lower:

            chat_memory.set_disease(None)

            chat_memory.set_intent(None)

            response = (

                "🌾 Which crop disease would you like to know about?\n\n"

                "Supported crops:\n\n"

                "- Wheat\n"
                "- Rice\n"
                "- Potato\n"
                "- Tomato\n\n"

                "Example questions:\n\n"

                "• Tomato late blight treatment\n"
                "• Symptoms of yellow rust\n"
                "• Rice bacterial leaf blight\n"
                "• Potato disease prevention"
            )

            chat_memory.add_to_history(
                user_text,
                response
            )

            return response

    # =====================================================
    # STEP 4: AGRICULTURE FILTER
    # =====================================================

    filter_result = agriculture_filter(corrected_text)

    if not filter_result["allowed"]:

        return filter_result["message"]

    # =====================================================
    # STEP 5: GREETING
    # =====================================================

    if filter_result["category"] == "greeting":

        response = generate_greeting_response()

        chat_memory.add_to_history(
            user_text,
            response
        )

        return response

    # =====================================================
    # STEP 6: INTENT DETECTION
    # =====================================================

    intent_result = smart_intent_detection(corrected_text)

    intent = intent_result["primary_intent"]

    # =====================================================
    # STEP 6: ENTITY EXTRACTION
    # =====================================================

    entity_result = smart_entity_extractor(corrected_text)

    crop = entity_result["crop"]

    disease = entity_result["disease"]

    # -----------------------------------------------------
    # Recover Previous Crop Memory
    # -----------------------------------------------------

    if not crop:

        previous_crop = chat_memory.get_crop()

        if previous_crop:

            crop = previous_crop

            entity_result["crop"] = previous_crop


    # =====================================================
    # FOLLOW-UP INTENTS
    # =====================================================

    FOLLOW_UP_INTENTS = [

        "symptoms",
        "causes",
        "treatment",
        "prevention",
        "weather"
    ]

    # =====================================================
    # Recover Previous Crop Only For Follow-Ups
    # =====================================================

    if not crop:

        previous_crop = chat_memory.get_crop()

        if (

            previous_crop
            and intent in FOLLOW_UP_INTENTS

        ):

            crop = previous_crop

            entity_result["crop"] = previous_crop

    # =====================================================
    # Recover Previous Disease Only For Follow-Ups
    # =====================================================

    if not disease:

        previous_disease = chat_memory.get_disease()

        if (

            previous_disease
            and intent in FOLLOW_UP_INTENTS
            and "disease" not in corrected_text_lower

        ):

            disease = previous_disease

    # =====================================================
    # STEP 8: HANDLE CROP ONLY
    # =====================================================

    crop_only_message = (

        crop
        and not disease
        and corrected_text_lower == crop
    )

    if crop_only_message:

        chat_memory.set_crop(crop)

        chat_memory.set_disease(None)

        available_diseases = list(
            DISEASE_DATABASE[crop].keys()
        )

        available_diseases = [

            d for d in available_diseases
            if d != "healthy"
        ]

        formatted_diseases = "\n".join(

            [
                f"- {format_title(d)}"
                for d in available_diseases
            ]
        )

        response = (

            f"🌾 Crop: {crop.title()}\n\n"

            f"Please specify the disease name.\n\n"

            f"Available diseases for {crop.title()}:\n\n"

            f"{formatted_diseases}"
        )

        chat_memory.add_to_history(
            user_text,
            response
        )

        return response

    # =====================================================
    # STEP 9: SAVE MEMORY
    # =====================================================

    if crop:
        chat_memory.set_crop(crop)

    if disease:
        chat_memory.set_disease(disease)

    if intent:
        chat_memory.set_intent(intent)

    # =====================================================
    # STEP 10: DISEASE AMBIGUITY
    # =====================================================

    if entity_result["needs_crop_confirmation"]:

        possible_crops = entity_result["possible_crops"]

        chat_memory.set_confirmation(
            True,
            possible_crops
        )

        crop_text = ", ".join(
            [c.title() for c in possible_crops]
        )

        response = (

            f"⚠ {format_title(disease)} can affect multiple crops.\n\n"

            f"Possible Crops:\n"
            f"{crop_text}\n\n"

            f"Please specify the crop name."
        )

        chat_memory.add_to_history(
            user_text,
            response
        )

        return response

    # =====================================================
    # STEP 11: INVALID COMBINATION
    # =====================================================

    if not entity_result["valid"]:

        response = entity_result["error"]

        chat_memory.add_to_history(
            user_text,
            response
        )

        return response

    # =====================================================
    # STEP 12: ASK FOR DISEASE NAME
    # =====================================================

    if crop and not disease:

        available_diseases = list(
            DISEASE_DATABASE[crop].keys()
        )

        available_diseases = [

            d for d in available_diseases
            if d != "healthy"
        ]

        formatted_diseases = "\n".join(

            [
                f"- {format_title(d)}"
                for d in available_diseases
            ]
        )

        response = (

            f"🌾 Crop: {crop.title()}\n\n"

            f"Please specify the disease name.\n\n"

            f"Available diseases for {crop.title()}:\n\n"

            f"{formatted_diseases}"
        )

        chat_memory.add_to_history(
            user_text,
            response
        )

        return response

    # =====================================================
    # STEP 13: DISEASE RESPONSE
    # =====================================================

    if disease:

        if not crop:

            response = (

                "Please specify the crop name.\n\n"

                "Supported Crops:\n\n"

                "- Wheat\n"
                "- Rice\n"
                "- Potato\n"
                "- Tomato"
            )

            chat_memory.add_to_history(
                user_text,
                response
            )

            return response

        chat_memory.set_crop(crop)

        chat_memory.set_disease(disease)

        response = generate_disease_response(
            crop,
            disease,
            intent
        )

        chat_memory.add_to_history(
            user_text,
            response
        )

        return response

    # =====================================================
    # STEP 14: IRRIGATION RESPONSE
    # =====================================================

    if intent == "irrigation":

        if not crop:

            response = (

                "🌾 Which crop irrigation information do you need?\n\n"

                "Supported Crops:\n\n"

                "- Wheat\n"
                "- Rice\n"
                "- Potato\n"
                "- Tomato"
            )

            return response

        response = generate_irrigation_response(
            crop,
            corrected_text
        )

        chat_memory.add_to_history(
            user_text,
            response
        )

        return response

    # =====================================================
    # STEP 15: WEATHER RESPONSE
    # =====================================================

    if intent == "weather":

        if crop and crop in IRRIGATION_DATA:

            response = (

                f"🌾 Crop: {crop.title()}\n\n"

                f"🌦 Weather Information:\n\n"

                f"{IRRIGATION_DATA[crop]['temperature_effect']}"
            )

            return response

    # =====================================================
    # STEP 16: SOIL RESPONSE
    # =====================================================

    if intent == "soil":

        if crop and crop in IRRIGATION_DATA:

            response = (

                f"🌾 Crop: {crop.title()}\n\n"

                f"🌱 Soil Information:\n\n"

                f"{IRRIGATION_DATA[crop]['soil_type']}"
            )

            return response

    # =====================================================
    # STEP 17: UNKNOWN RESPONSE
    # =====================================================

    response = generate_unknown_response()

    chat_memory.add_to_history(
        user_text,
        response
    )

    return response


# =========================================================
# Testing
# =========================================================

if __name__ == "__main__":

    print("\n🌱 AgroScan Intelligent Chatbot Ready\n")

    while True:

        user_input = input("YOU: ")

        if user_input.lower() in ["exit", "quit"]:

            print("\nChatbot stopped.")
            break

        response = generate_chatbot_response(user_input)

        print("\nBOT:\n")

        print(response)

        print("\n" + "=" * 60 + "\n")