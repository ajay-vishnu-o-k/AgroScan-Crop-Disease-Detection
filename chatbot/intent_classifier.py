# =========================================================
# AgroScan Intent Classifier
# =========================================================

from rapidfuzz import fuzz


# =========================================================
# Intent Keywords
# =========================================================

INTENT_KEYWORDS = {

    # -----------------------------------------------------
    # Disease Related Intents
    # -----------------------------------------------------

    "symptoms": [

        "symptom",
        "symptoms",
        "sign",
        "signs",
        "identify",
        "identification",
        "detect",
        "detection",
        "how to identify",
        "what does it look like",
        "leaf spots",
        "yellow leaves",
        "black spots",
        "disease symptoms"
    ],

    # -----------------------------------------------------

    "causes": [

        "cause",
        "causes",
        "reason",
        "reasons",
        "why",
        "what causes",
        "disease cause",
        "infection reason",
        "how it spreads",
        "spread"
    ],

    # -----------------------------------------------------

    "treatment": [

        "treat",
        "treatment",
        "medicine",
        "cure",
        "control",
        "solution",
        "fungicide",
        "how to cure",
        "how to treat",
        "how to control",
        "pesticide",
        "spray",
        "recovery"
    ],

    # -----------------------------------------------------

    "prevention": [

        "prevent",
        "prevention",
        "avoid",
        "protection",
        "protect",
        "how to prevent",
        "stop disease",
        "disease prevention",
        "avoid infection"
    ],

    # -----------------------------------------------------
    # Irrigation Intent
    # -----------------------------------------------------

    "irrigation": [

        "irrigation",
        "water",
        "watering",
        "drip irrigation",
        "sprinkler",
        "flood irrigation",
        "how much water",
        "water requirement",
        "soil moisture",
        "rainfall",
        "temperature effect",
        "watering schedule"
    ],

    # -----------------------------------------------------
    # Fertilizer Intent
    # -----------------------------------------------------

    "fertilizer": [

        "fertilizer",
        "fertiliser",
        "npk",
        "nutrient",
        "nutrients",
        "manure",
        "compost",
        "urea",
        "potassium",
        "phosphorus",
        "nitrogen",
        "best fertilizer",
        "fertilizer recommendation"
    ],

    # -----------------------------------------------------
    # Weather Intent
    # -----------------------------------------------------

    "weather": [

        "weather",
        "climate",
        "temperature",
        "humidity",
        "rain",
        "rainfall",
        "environment",
        "suitable weather",
        "best climate",
        "weather condition"
    ],

    # -----------------------------------------------------
    # Harvest Intent
    # -----------------------------------------------------

    "harvest": [

        "harvest",
        "harvesting",
        "when to harvest",
        "harvest time",
        "crop maturity",
        "ready to harvest",
        "maturity"
    ],

    # -----------------------------------------------------
    # Soil Intent
    # -----------------------------------------------------

    "soil": [

        "soil",
        "soil type",
        "best soil",
        "soil condition",
        "soil requirement",
        "clay soil",
        "sandy soil",
        "loamy soil"
    ],

    # -----------------------------------------------------
    # Cultivation Intent
    # -----------------------------------------------------

    "cultivation": [

        "cultivation",
        "growing",
        "how to grow",
        "planting",
        "farming",
        "crop management",
        "cultivate",
        "crop production"
    ],

    # -----------------------------------------------------
    # Healthy Crop Intent
    # -----------------------------------------------------

    "healthy": [

        "healthy",
        "normal plant",
        "good crop",
        "healthy crop condition"
    ],

    # -----------------------------------------------------
    # Greeting Intent
    # -----------------------------------------------------

    "greeting": [

        "hello",
        "hi",
        "hey",
        "good morning",
        "good evening"
    ],

    # -----------------------------------------------------
    # App Help Intent
    # -----------------------------------------------------

    "app_help": [

        "how to use app",
        "upload image",
        "predict disease",
        "how app works",
        "supported crops",
        "app features",
        "how to upload"
    ]
}


# =========================================================
# Detect Intent Function
# =========================================================

def detect_intent(user_text):

    user_text = user_text.lower()

    best_intent = None
    best_score = 0

    # -----------------------------------------------------
    # Exact Matching
    # -----------------------------------------------------

    for intent, keywords in INTENT_KEYWORDS.items():

        for keyword in keywords:

            if keyword in user_text:

                score = len(keyword)

                if score > best_score:

                    best_score = score
                    best_intent = intent

    # -----------------------------------------------------
    # Fuzzy Matching
    # -----------------------------------------------------

    if not best_intent:

        for intent, keywords in INTENT_KEYWORDS.items():

            for keyword in keywords:

                score = fuzz.partial_ratio(keyword, user_text)

                if score > best_score and score >= 80:

                    best_score = score
                    best_intent = intent

    # -----------------------------------------------------
    # Default Intent
    # -----------------------------------------------------

    if not best_intent:
        best_intent = "general"

    return best_intent


# =========================================================
# Get All Matching Intents
# =========================================================

def detect_multiple_intents(user_text):

    user_text = user_text.lower()

    detected_intents = []

    for intent, keywords in INTENT_KEYWORDS.items():

        for keyword in keywords:

            if keyword in user_text:

                detected_intents.append(intent)
                break

            score = fuzz.partial_ratio(keyword, user_text)

            if score >= 80:

                detected_intents.append(intent)
                break

    # Remove duplicates
    detected_intents = list(set(detected_intents))

    return detected_intents


# =========================================================
# Smart Intent Detection
# =========================================================

def smart_intent_detection(user_text):

    primary_intent = detect_intent(user_text)

    all_intents = detect_multiple_intents(user_text)

    result = {

        "primary_intent": primary_intent,

        "all_detected_intents": all_intents,

        "is_disease_related": primary_intent in [

            "symptoms",
            "causes",
            "treatment",
            "prevention"
        ],

        "is_crop_related": primary_intent in [

            "irrigation",
            "fertilizer",
            "weather",
            "harvest",
            "soil",
            "cultivation"
        ]
    }

    return result


# =========================================================
# Example Testing
# =========================================================

if __name__ == "__main__":

    test_questions = [

        "What are the symptoms of late blight?",

        "How to treat potato late blight?",

        "What causes yellow rust in wheat?",

        "How much water does rice need?",

        "Best fertilizer for tomato?",

        "What climate is suitable for potato?",

        "When should I harvest rice?",

        "Best soil for wheat?",

        "How to grow tomato plants?",

        "How to upload image in app?"
    ]

    for question in test_questions:

        print("\n================================================")
        print("Question:", question)

        result = smart_intent_detection(question)

        print("Result:", result)
