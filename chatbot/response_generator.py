# =========================================================
# AgroScan Response Generator (FINAL FIXED)
# =========================================================

from fuzzy_engine import fuzzy_pipeline
from agriculture_filter import agriculture_filter
from intent_classifier import smart_intent_detection
from entity_extractor import smart_entity_extractor
from context_memory import chat_memory

from data.disease_data import DISEASE_DATABASE
from data.irrigation_data import IRRIGATION_DATA
from data.crop_management_data import CROP_MANAGEMENT_DATA

from response_templates import (
    generate_greeting_response,
    generate_disease_response,
    generate_irrigation_response,
    generate_unknown_response,
    format_title
)

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

        for crop_name in possible_crops:
            if crop_name in corrected_text_lower:

                crop = crop_name
                disease = chat_memory.get_disease()
                intent = chat_memory.get_intent()

                chat_memory.set_crop(crop)
                chat_memory.set_confirmation(False)

                response = generate_disease_response(crop, disease, intent)

                chat_memory.add_to_history(user_text, response)
                return response

    # =====================================================
    # STEP 3: GENERAL DISEASE QUESTION
    # =====================================================

    GENERAL_DISEASE_KEYWORDS = [
        "disease", "crop disease", "plant disease",
        "diseases", "crop diseases"
    ]

    for keyword in GENERAL_DISEASE_KEYWORDS:
        if keyword in corrected_text_lower:

            chat_memory.set_crop(None)
            chat_memory.set_disease(None)
            chat_memory.set_intent(None)

            response = (
                "🌾 Which crop disease would you like to know about?\n\n"
                "Supported crops:\n"
                "- Wheat\n- Rice\n- Potato\n- Tomato\n\n"
                "Example questions:\n"
                "• Tomato late blight treatment\n"
                "• Symptoms of yellow rust\n"
                "• Rice bacterial leaf blight\n"
                "• Potato disease prevention"
            )

            chat_memory.add_to_history(user_text, response)
            return response

    # =====================================================
    # STEP 4: AGRICULTURE FILTER
    # =====================================================

    filter_result = agriculture_filter(corrected_text)

    if not filter_result["allowed"]:
        return filter_result["message"]

    if filter_result["category"] == "greeting":
        chat_memory.set_crop(None)
        chat_memory.set_disease(None)
        chat_memory.set_intent(None)

        response = generate_greeting_response()
        chat_memory.add_to_history(user_text, response)
        return response

    # =====================================================
    # STEP 5: INTENT DETECTION
    # =====================================================

    intent_result = smart_intent_detection(corrected_text)
    intent = intent_result["primary_intent"]

    if chat_memory.get_intent() == "cultivation":
        intent = "cultivation"

    if "crop management" in corrected_text_lower or "farm management" in corrected_text_lower:
        intent = "cultivation"
        chat_memory.set_intent("cultivation")

    # =====================================================
    # STEP 6: ENTITY EXTRACTION
    # =====================================================

    entity_result = smart_entity_extractor(corrected_text)

    crop = entity_result["crop"]
    disease = entity_result["disease"]
    print("\n===== DEBUG =====")
    print("User Text:", corrected_text)
    print("Intent:", intent)
    print("Crop:", crop)
    print("Disease:", disease)
    print("Memory Intent:", chat_memory.get_intent())
    print("=================\n")

    if not crop:
        crop = chat_memory.get_crop()

    if not disease:
        disease = chat_memory.get_disease()

    # =====================================================
    # STEP 7: CROP MANAGEMENT (FIXED – NO LOOP, NO SUB BUG)
    # =====================================================

    if intent == "cultivation":

        chat_memory.set_intent("cultivation")

        # -------------------------------
        # SUB TOPIC RESPONSE
        # -------------------------------
        sub_topics = [
            "soil", "sowing", "seed", "irrigation",
            "fertilizer", "weed", "pest", "harvest"
        ]

        response_map = {
            "soil": "Soil preparation depends on crop type, ensure proper drainage and nutrient balance.",
            "sowing": "Follow proper spacing and depth during sowing.",
            "seed": "Use certified, disease-free high-quality seeds.",
            "irrigation": "Maintain proper irrigation based on growth stage.",
            "fertilizer": "Apply balanced NPK in split doses.",
            "weed": "Control weeds early to avoid competition.",
            "pest": "Use integrated pest management techniques.",
            "harvest": "Harvest at correct maturity stage for best yield."
        }

        text = corrected_text_lower

        matched_topic = None
        for topic in sub_topics:
            if topic in text:
                matched_topic = topic
                break

            # -------------------------------
            # CASE 1: SUB TOPIC REQUEST
            # -------------------------------
            if matched_topic:

                crop_name = crop or chat_memory.get_crop()

                if not crop_name:
                    response = "Please select a crop first (Wheat, Rice, Potato, Tomato)."
                    chat_memory.add_to_history(user_text, response)
                    return response

                chat_memory.set_sub_intent(matched_topic)

                response = (
                    f"🌱 Crop Management ({matched_topic.title()}) for {crop_name.title()}:\n\n"
                    f"• {response_map[matched_topic]}"
                )

                chat_memory.add_to_history(user_text, response)
                return response

            # -------------------------------
            # CASE 2: CONTINUATION FIX
            # -------------------------------
            previous_sub = chat_memory.get_sub_intent() if hasattr(chat_memory, "get_sub_intent") else None

            if previous_sub and previous_sub in response_map:

                crop_name = crop or chat_memory.get_crop()

                response = (
                    f"🌱 Crop Management ({previous_sub.title()}) for {crop_name.title()}:\n\n"
                    f"• {response_map[previous_sub]}"
                )

                chat_memory.add_to_history(user_text, response)
                return response

            # -------------------------------
            # CASE 3: FULL CROP GUIDE
            # -------------------------------
            if crop:

                chat_memory.set_crop(crop)

                points = CROP_MANAGEMENT_DATA.get(crop.lower(), [])

                if not points:
                    points = [
                        "Soil preparation",
                        "Seed selection",
                        "Irrigation planning",
                        "Fertilizer management",
                        "Weed control",
                        "Pest control",
                        "Harvest timing"
                    ]

                response = (
                    f"🌱 Crop Management Guide for {crop.title()}:\n\n"
                    + "\n".join([f"• {p}" for p in points])
                )

                chat_memory.add_to_history(user_text, response)
                return response

            previous_crop = chat_memory.get_crop()
            if previous_crop:

                crop = previous_crop

                points = CROP_MANAGEMENT_DATA.get(crop.lower(), [])

                response = (
                    f"🌱 Crop Management Guide for {crop.title()}:\n\n"
                    + "\n".join([f"• {p}" for p in points])
                )

                chat_memory.add_to_history(user_text, response)
                return response

            # -------------------------------
            # CASE 4: ASK ONCE
            # -------------------------------
            response = (
                "🌱 Which crop management information do you need?\n\n"
                "Supported Crops:\n"
                "- Wheat\n- Rice\n- Potato\n- Tomato"
            )

            chat_memory.add_to_history(user_text, response)
            return response

    if crop and corrected_text_lower == crop:
        
        previous_intent = chat_memory.get_intent()

        # =====================================================
        # CONTINUATION OF IRRIGATION
        # =====================================================

        if previous_intent == "irrigation":

            chat_memory.set_crop(crop)

            response = generate_irrigation_response(
                crop,
                corrected_text
            )

            chat_memory.add_to_history(user_text, response)
            return response

        # =====================================================
        # CONTINUATION OF WEATHER
        # =====================================================

        if previous_intent == "weather":

            chat_memory.set_crop(crop)

            response = (
                f"🌾 Crop: {crop.title()}\n\n"
                f"🌦 Weather:\n"
                f"{IRRIGATION_DATA[crop]['temperature_effect']}"
            )

            chat_memory.add_to_history(user_text, response)
            return response

        # =====================================================
        # DEFAULT DISEASE FLOW
        # =====================================================

        chat_memory.set_crop(crop)
        chat_memory.set_disease(None)

        available_diseases = [
            d for d in DISEASE_DATABASE[crop].keys()
            if d != "healthy"
        ]

        response = (
            f"🌾 Crop: {crop.title()}\n\n"
            "Please specify the disease name.\n\n"
            "Available diseases:\n"
            + "\n".join(
                [f"- {format_title(d)}" for d in available_diseases]
            )
        )

        chat_memory.add_to_history(user_text, response)
        return response

    # =====================================================
    # STEP 9: SAVE CONTEXT
    # =====================================================

    if crop:
        chat_memory.set_crop(crop)

    if disease:
        chat_memory.set_disease(disease)

    if intent:
        chat_memory.set_intent(intent)


    # =====================================================
    # STEP 11: IRRIGATION
    # =====================================================

    if intent == "irrigation":

        if not crop:
            response = (
                "🌾 Which crop irrigation information do you need?\n"
                "- Wheat\n- Rice\n- Potato\n- Tomato"
            )
            chat_memory.add_to_history(user_text, response)
            return response

        response = generate_irrigation_response(crop, corrected_text)
        chat_memory.add_to_history(user_text, response)
        return response

    # =====================================================
    # STEP 12: WEATHER
    # =====================================================

    if intent == "weather":

        if not crop:
            response = (
                "🌦 Which crop weather information do you need?\n"
                "- Wheat\n- Rice\n- Potato\n- Tomato"
            )
            chat_memory.add_to_history(user_text, response)
            return response

        response = (
            f"🌾 Crop: {crop.title()}\n\n"
            f"🌦 Weather:\n"
            f"{IRRIGATION_DATA[crop]['temperature_effect']}"
        )

        chat_memory.add_to_history(user_text, response)
        return response
    
    # =====================================================
    # STEP 10: DISEASE RESPONSE
    # =====================================================

    if disease and crop:

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
    # STEP 13: SOIL
    # =====================================================

    if intent == "soil" and crop:

        response = (
            f"🌾 Crop: {crop.title()}\n\n"
            f"🌱 Soil Info:\n"
            f"{IRRIGATION_DATA[crop]['soil_type']}"
        )

        chat_memory.add_to_history(user_text, response)
        return response

    # =====================================================
    # STEP 14: UNKNOWN
    # =====================================================

    response = generate_unknown_response()
    chat_memory.add_to_history(user_text, response)
    return response