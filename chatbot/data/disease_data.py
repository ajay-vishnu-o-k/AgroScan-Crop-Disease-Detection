
# =========================================================
# AgroScan Disease Knowledge Database
# =========================================================

DISEASE_DATABASE = {

    # =====================================================
    # WHEAT
    # =====================================================

    "wheat": {

        "healthy": {

            "description":
            "Healthy wheat plants show strong green leaves, uniform growth, well-developed roots, and healthy grain formation. The crop grows properly under suitable temperature, irrigation, and nutrient conditions.",

            "prevention":
            "Maintain proper irrigation, balanced fertilizer application, weed management, and regular crop monitoring to keep wheat plants healthy."
        },

        # -------------------------------------------------

        "brown_rust": {

            "symptoms":
            "Brown rust appears as small circular or oval brown pustules on wheat leaves and stems. The infected leaves may gradually turn yellow and dry out. Severe infection reduces photosynthesis and weakens the plant.",

            "causes":
            "Brown rust is caused by the fungal pathogen Puccinia triticina. The disease spreads rapidly in warm and humid environmental conditions. Excess moisture and poor field ventilation increase disease development.",

            "treatment":
            "Apply fungicides such as propiconazole or tebuconazole when symptoms first appear. Remove heavily infected plant parts and avoid excessive nitrogen fertilizer. Monitor fields regularly during humid weather.",

            "prevention":
            "Use resistant wheat varieties whenever possible. Maintain proper spacing between plants for better airflow. Avoid excessive irrigation and monitor crops frequently during the growing season.",

            "weather_conditions":
            "Brown rust develops rapidly in temperatures between 15°C and 25°C with high humidity and moist conditions.",

            "affected_parts":
            "Leaves, stems, and leaf sheaths are mainly affected by brown rust disease."
        },

        # -------------------------------------------------

        "yellow_rust": {

            "symptoms":
            "Yellow rust produces long yellow or orange stripe-like pustules arranged in rows on wheat leaves. Infected leaves may dry early and reduce grain production significantly.",

            "causes":
            "Yellow rust is caused by the fungus Puccinia striiformis. Cool temperatures and humid conditions favor the spread of this disease. Wind can carry fungal spores over long distances.",

            "treatment":
            "Apply fungicides such as azoxystrobin or propiconazole during the early stages of infection. Remove severely infected leaves and maintain balanced fertilization practices.",

            "prevention":
            "Use disease-resistant wheat varieties and avoid overcrowding in fields. Monitor crops regularly during cool and humid weather conditions.",

            "weather_conditions":
            "Yellow rust commonly develops in cool temperatures between 10°C and 15°C with high humidity.",

            "affected_parts":
            "Primarily affects wheat leaves and sometimes leaf sheaths."
        }
    },

    # =====================================================
    # RICE
    # =====================================================

    "rice": {

        "healthy": {

            "description":
            "Healthy rice plants have bright green leaves, strong stems, proper tillering, and healthy grain development. Adequate irrigation and balanced nutrients support proper rice growth.",

            "prevention":
            "Use certified seeds, maintain water management, apply fertilizers properly, and regularly inspect fields for diseases and pests."
        },

        # -------------------------------------------------

        "bacterial_leaf_blight": {

            "symptoms":
            "Bacterial leaf blight causes yellowing and drying at the tips and edges of rice leaves. The affected leaves may develop white or pale yellow streaks that later turn brown and dry.",

            "causes":
            "This disease is caused by the bacterium Xanthomonas oryzae. It spreads through infected seeds, rain splash, irrigation water, and contaminated farming tools.",

            "treatment":
            "Use copper-based bactericides when symptoms appear. Remove infected plant debris and maintain proper drainage in the field. Avoid excessive nitrogen fertilizer application.",

            "prevention":
            "Use disease-resistant rice varieties and certified seeds. Ensure proper field sanitation and balanced fertilizer management.",

            "weather_conditions":
            "Warm temperatures, heavy rainfall, and strong winds favor bacterial leaf blight development.",

            "affected_parts":
            "Mainly affects rice leaves and leaf tips."
        },

        # -------------------------------------------------

        "brown_spot": {

            "symptoms":
            "Brown spot disease causes small brown circular spots on rice leaves. Severe infections may lead to leaf drying and reduced grain quality.",

            "causes":
            "Brown spot is caused by the fungus Bipolaris oryzae. Nutrient deficiency, poor soil fertility, and high humidity increase disease occurrence.",

            "treatment":
            "Apply fungicides such as mancozeb or carbendazim. Improve soil fertility and maintain proper irrigation management.",

            "prevention":
            "Use healthy seeds, balanced fertilizers, and proper field management practices to reduce disease risk.",

            "weather_conditions":
            "High humidity, warm temperatures, and continuous rainfall favor disease development.",

            "affected_parts":
            "Leaves, grains, and seedlings may be affected."
        }
    },

    # =====================================================
    # POTATO
    # =====================================================

    "potato": {

        "healthy": {

            "description":
            "Healthy potato plants have green leaves, strong stems, and properly developing tubers. Proper irrigation and soil drainage are essential for healthy potato growth.",

            "prevention":
            "Use certified seed tubers, maintain proper irrigation, ensure good soil drainage, and monitor plants regularly."
        },

        # -------------------------------------------------

        "late_blight": {

            "symptoms":
            "Late blight causes dark brown or black water-soaked spots on potato leaves and stems. White fungal growth may appear on the underside of leaves during humid conditions. Tubers may also rot under severe infection.",

            "causes":
            "Late blight is caused by the pathogen Phytophthora infestans. Cool temperatures and high humidity promote rapid disease spread. Rain and wind help spread spores quickly.",

            "treatment":
            "Remove infected leaves and plants immediately. Apply fungicides such as chlorothalonil, mancozeb, or copper-based fungicides. Avoid overhead irrigation to reduce leaf moisture.",

            "prevention":
            "Use resistant potato varieties and certified seeds. Ensure proper spacing for airflow and avoid excessive irrigation during humid weather.",

            "weather_conditions":
            "Cool temperatures between 10°C and 20°C with high humidity strongly favor late blight development.",

            "affected_parts":
            "Leaves, stems, and potato tubers are commonly affected."
        }
    },

    # =====================================================
    # TOMATO
    # =====================================================

    "tomato": {

        "healthy": {

            "description":
            "Healthy tomato plants show strong green leaves, healthy flowering, and proper fruit development. Proper sunlight, nutrients, and irrigation are important for healthy growth.",

            "prevention":
            "Maintain balanced watering, apply fertilizers properly, and regularly inspect tomato plants for diseases and pests."
        },

        # -------------------------------------------------

        "late_blight": {

            "symptoms":
            "Late blight causes dark brown or black lesions on tomato leaves, stems, and fruits. White fungal growth may develop under humid conditions. Fruits may rot rapidly.",

            "causes":
            "The disease is caused by Phytophthora infestans. Wet weather, cool temperatures, and high humidity encourage disease spread.",

            "treatment":
            "Remove infected leaves and fruits immediately. Apply fungicides such as copper fungicide or chlorothalonil. Improve air circulation around plants.",

            "prevention":
            "Avoid overhead watering and maintain proper plant spacing. Use disease-free seedlings and monitor crops regularly.",

            "weather_conditions":
            "Cool and humid weather strongly promotes late blight infection.",

            "affected_parts":
            "Leaves, stems, and tomato fruits are affected."
        },

        # -------------------------------------------------

        "early_blight": {

            "symptoms":
            "Early blight causes brown circular spots with concentric rings on tomato leaves. Older leaves usually show symptoms first. Severe infection may lead to leaf drop.",

            "causes":
            "Early blight is caused by the fungus Alternaria solani. Warm temperatures, humidity, and poor field sanitation increase disease spread.",

            "treatment":
            "Apply fungicides such as mancozeb or chlorothalonil. Remove infected leaves and maintain proper field cleanliness.",

            "prevention":
            "Practice crop rotation and avoid overhead irrigation. Use healthy seedlings and provide proper plant spacing.",

            "weather_conditions":
            "Warm temperatures between 24°C and 29°C with humid conditions favor early blight development.",

            "affected_parts":
            "Primarily affects leaves, stems, and fruits."
        }
    }
}

