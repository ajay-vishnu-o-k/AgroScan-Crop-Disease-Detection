# =========================================================
# AgroScan Irrigation Knowledge Database
# =========================================================

IRRIGATION_DATA = {

    # =====================================================
    # WHEAT
    # =====================================================

    "wheat": {

        "water_requirement":
        "Wheat requires moderate irrigation throughout its growth stages. "
        "Generally, wheat needs about 450 to 650 mm of water during the "
        "entire growing season depending on soil and climate conditions.",

        "best_irrigation_method":
        "Sprinkler irrigation and furrow irrigation are commonly used for "
        "wheat cultivation. Sprinkler systems help distribute water evenly.",

        "critical_growth_stages":
        "The most important irrigation stages for wheat are crown root "
        "initiation, tillering, flowering, and grain filling stages.",

        "soil_type":
        "Loamy and well-drained soils are best for wheat irrigation. "
        "Heavy waterlogging should be avoided because it can damage roots.",

        "rainfall_effect":
        "Moderate rainfall supports wheat growth, but excessive rainfall "
        "can increase fungal diseases such as rust infections.",

        "temperature_effect":
        "Cool temperatures between 15°C and 25°C are ideal for wheat growth "
        "and efficient irrigation management.",

        "over_irrigation_effect":
        "Over-irrigation may cause root diseases, nutrient loss, and "
        "waterlogging in wheat fields.",

        "under_irrigation_effect":
        "Insufficient irrigation can reduce grain development, "
        "crop growth, and overall yield.",

        "recommended_soil_moisture":
        "Wheat fields should maintain moderate soil moisture without "
        "excess standing water."
    },

    # =====================================================
    # RICE
    # =====================================================

    "rice": {

        "water_requirement":
        "Rice requires large amounts of water compared to other crops. "
        "Rice cultivation generally needs about 1200 to 1500 mm of water "
        "throughout the growing season.",

        "best_irrigation_method":
        "Flood irrigation is the most commonly used irrigation method "
        "for rice cultivation. Controlled flooding helps suppress weeds "
        "and supports proper rice growth.",

        "critical_growth_stages":
        "Tillering, panicle initiation, flowering, and grain filling "
        "are critical stages that require proper irrigation.",

        "soil_type":
        "Clayey and clay-loam soils are preferred for rice because "
        "they retain water effectively.",

        "rainfall_effect":
        "Adequate rainfall reduces irrigation requirements, but heavy "
        "continuous rainfall can increase disease spread and flooding risks.",

        "temperature_effect":
        "Rice grows best in warm temperatures between 20°C and 35°C "
        "with sufficient water availability.",

        "over_irrigation_effect":
        "Excessive standing water for long periods may reduce oxygen "
        "availability to roots and increase disease problems.",

        "under_irrigation_effect":
        "Water shortage during flowering and grain filling can severely "
        "reduce rice yield.",

        "recommended_soil_moisture":
        "Rice fields should maintain moist or shallow flooded conditions "
        "during most growth stages."
    },

    # =====================================================
    # POTATO
    # =====================================================

    "potato": {

        "water_requirement":
        "Potato requires regular but controlled irrigation. "
        "The crop generally needs about 500 to 700 mm of water "
        "throughout the growing season.",

        "best_irrigation_method":
        "Drip irrigation is highly recommended for potato cultivation "
        "because it provides efficient water management and reduces "
        "disease risk.",

        "critical_growth_stages":
        "Tuber initiation and tuber bulking are the most critical "
        "stages requiring proper irrigation.",

        "soil_type":
        "Well-drained sandy loam soils are ideal for potato cultivation. "
        "Poor drainage can increase tuber rot diseases.",

        "rainfall_effect":
        "Excess rainfall increases the risk of late blight and tuber rot. "
        "Proper drainage is essential during rainy periods.",

        "temperature_effect":
        "Cool temperatures between 15°C and 20°C are ideal for potato growth "
        "and irrigation management.",

        "over_irrigation_effect":
        "Over-irrigation may cause fungal diseases, root damage, "
        "and poor tuber quality.",

        "under_irrigation_effect":
        "Insufficient irrigation reduces tuber size, quality, "
        "and crop yield.",

        "recommended_soil_moisture":
        "Potato fields should maintain consistent soil moisture "
        "without waterlogging."
    },

    # =====================================================
    # TOMATO
    # =====================================================

    "tomato": {

        "water_requirement":
        "Tomato plants require regular irrigation for healthy fruit "
        "development. Tomatoes generally need about 400 to 600 mm "
        "of water during the growing season.",

        "best_irrigation_method":
        "Drip irrigation is the best method for tomato cultivation "
        "because it reduces leaf wetness and minimizes disease spread.",

        "critical_growth_stages":
        "Flowering and fruit development stages require proper "
        "irrigation for high-quality tomato production.",

        "soil_type":
        "Well-drained loamy soil is ideal for tomato irrigation. "
        "Good drainage prevents root diseases.",

        "rainfall_effect":
        "Excess rainfall and high humidity increase the risk of "
        "late blight and early blight diseases in tomatoes.",

        "temperature_effect":
        "Tomatoes grow best between 20°C and 30°C with balanced "
        "soil moisture conditions.",

        "over_irrigation_effect":
        "Over-irrigation may cause root rot, nutrient loss, "
        "and fungal disease development.",

        "under_irrigation_effect":
        "Insufficient irrigation can cause flower drop, fruit cracking, "
        "and reduced fruit size.",

        "recommended_soil_moisture":
        "Tomato plants require evenly moist soil but should not "
        "remain waterlogged."
    }
}


# =========================================================
# Irrigation Helper Functions
# =========================================================

def get_irrigation_info(crop):

    crop = crop.lower()

    return IRRIGATION_DATA.get(crop, None)


# =========================================================

def get_irrigation_field(crop, field):

    crop = crop.lower()

    if crop not in IRRIGATION_DATA:
        return None

    return IRRIGATION_DATA[crop].get(field, None)


# =========================================================
# Example Testing
# =========================================================

if __name__ == "__main__":

    crops = [

        "wheat",
        "rice",
        "potato",
        "tomato"
    ]

    for crop in crops:

        print("\n================================================")
        print("Crop:", crop.title())

        data = get_irrigation_info(crop)

        print("\nWater Requirement:")
        print(data["water_requirement"])

        print("\nBest Irrigation Method:")
        print(data["best_irrigation_method"])

        print("\nTemperature Effect:")
        print(data["temperature_effect"])
