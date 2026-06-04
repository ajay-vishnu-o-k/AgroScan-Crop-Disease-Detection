def irrigation_recommendation(
    crop_type,
    rainfall,
    temperature,
    soil_type
):

    # Convert inputs to lowercase
    crop_type = crop_type.lower()
    soil_type = soil_type.lower()

    # Store all recommendations
    recommendations = []

    # ==========================================
    # RAINFALL ANALYSIS
    # ==========================================

    if rainfall > 120:
        recommendations.append(
            "Heavy rainfall has been detected, so irrigation should be reduced to prevent waterlogging."
        )

    elif rainfall >= 60:
        recommendations.append(
            "Moderate rainfall is available, so maintain balanced irrigation."
        )

    else:
        recommendations.append(
            "Low rainfall detected, so additional irrigation is necessary."
        )

    # ==========================================
    # TEMPERATURE ANALYSIS
    # ==========================================

    if temperature > 38:
        recommendations.append(
            "Very high temperature increases water evaporation, so frequent irrigation is recommended."
        )

    elif temperature >= 25:
        recommendations.append(
            "Temperature conditions are normal for healthy crop growth."
        )

    else:
        recommendations.append(
            "Low temperature reduces evaporation, so irrigation frequency can be reduced."
        )

    # ==========================================
    # SOIL TYPE ANALYSIS
    # Common Indian soils
    # ==========================================

    if soil_type == "sandy":
        recommendations.append(
            "Sandy soil loses water quickly, so light irrigation every 2 days is recommended."
        )

    elif soil_type == "clay":
        recommendations.append(
            "Clay soil retains water for longer periods, so irrigation should be less frequent."
        )

    elif soil_type == "loamy":
        recommendations.append(
            "Loamy soil has balanced moisture retention and supports regular irrigation schedules."
        )

    elif soil_type == "red":
        recommendations.append(
            "Red soil dries quickly, so moderate and regular irrigation is required."
        )

    elif soil_type == "black":
        recommendations.append(
            "Black soil retains moisture efficiently, so avoid excessive irrigation."
        )

    elif soil_type == "alluvial":
        recommendations.append(
            "Alluvial soil supports good water retention and fertility for crop growth."
        )

    else:
        recommendations.append(
            "Unknown soil type detected, so monitor soil moisture manually."
        )

    # ==========================================
    # CROP SPECIFIC ANALYSIS
    # ==========================================

    if crop_type == "tomato":
        recommendations.append(
            "Tomato crops require moderate and consistent irrigation, especially during fruit development."
        )

    elif crop_type == "potato":
        recommendations.append(
            "Potato crops require uniform soil moisture for healthy tuber formation."
        )

    elif crop_type == "wheat":
        recommendations.append(
            "Wheat crops require moderate irrigation during early growth stages."
        )

    elif crop_type == "rice":
        recommendations.append(
            "Rice crops require high water availability and perform well in flooded conditions."
        )

    else:
        recommendations.append(
            "Crop-specific irrigation information is unavailable."
        )

    # ==========================================
    # FINAL IRRIGATION DECISION
    # ==========================================

    # Smart combined recommendation

    if rainfall < 50 and temperature > 35 and soil_type == "sandy":
        final_decision = (
            "Final Recommendation: Irrigate frequently because the weather is hot, rainfall is low, and sandy soil loses moisture rapidly."
        )

    elif rainfall > 120 and soil_type == "clay":
        final_decision = (
            "Final Recommendation: Avoid additional irrigation because heavy rainfall and clay soil may cause waterlogging."
        )

    elif soil_type == "loamy":
        final_decision = (
            "Final Recommendation: Maintain a regular irrigation schedule every 3 days for balanced soil moisture."
        )

    else:
        final_decision = (
            "Final Recommendation: Monitor field moisture regularly and irrigate according to crop conditions."
        )

    recommendations.append(final_decision)

    # ==========================================
    # RETURN COMPLETE RESULT
    # ==========================================

    return "\n\n".join(recommendations)