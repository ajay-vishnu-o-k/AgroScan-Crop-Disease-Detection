from rapidfuzz import fuzz

# =========================================================
# Intent Keywords
# =========================================================

INTENT_KEYWORDS = {
    "symptoms": [
        "symptom","symptoms","sign","signs","identify","identification",
        "detect","detection","how to identify","what does it look like",
        "leaf spots","yellow leaves","black spots","disease symptoms"
    ],
    "causes": [
        "cause","causes","reason","reasons","why","what causes",
        "disease cause","infection reason","how it spreads","spread"
    ],
    "treatment": [
        "treat","treatment","medicine","cure","control","solution",
        "fungicide","how to cure","how to treat","how to control",
        "pesticide","spray","recovery"
    ],
    "prevention": [
        "prevent","prevention","avoid","protection","protect",
        "how to prevent","stop disease","disease prevention","avoid infection"
    ],
    "irrigation": [
        "irrigation","water","watering","drip irrigation","sprinkler",
        "flood irrigation","how much water","water requirement",
        "soil moisture","rainfall","temperature effect","watering schedule"
    ],
    "fertilizer": [
        "fertilizer","fertiliser","npk","nutrient","nutrients","manure",
        "compost","urea","potassium","phosphorus","nitrogen",
        "best fertilizer","fertilizer recommendation"
    ],
    "weather": [
        "weather","weather condition","weather conditions","climate",
        "temperature","humidity","rain","rainfall","forecast",
        "hot weather","cold weather","environment","suitable weather",
        "best climate","climate condition","crop weather","weather guidance"
    ],
    "harvest": [
        "harvest","harvesting","when to harvest","harvest time",
        "crop maturity","ready to harvest","maturity"
    ],
    "soil": [
        "soil","soil type","best soil","soil condition",
        "soil requirement","clay soil","sandy soil","loamy soil"
    ],
    "cultivation": [
        "crop management","farm management","field management",
        "crop care","agriculture management","how to manage crops",
        "crop planning"
    ],
    "healthy": [
        "healthy","normal plant","good crop","healthy crop condition"
    ],
    "greeting": [
        "hello","hi","hey","good morning","good evening"
    ],
    "app_help": [
        "how to use app","upload image","predict disease",
        "how app works","supported crops","app features","how to upload"
    ]
}

def detect_intent(user_text):
    user_text = user_text.lower().strip()

    if ("symptoms of" in user_text or "symptom of" in user_text
            or "what are the symptoms" in user_text):
        return "symptoms"

    if ("causes of" in user_text or "cause of" in user_text
            or "what causes" in user_text):
        return "causes"

    if ("treatment for" in user_text or "how to treat" in user_text
            or "treat" in user_text):
        return "treatment"

    if ("prevention of" in user_text or "how to prevent" in user_text
            or "prevent" in user_text):
        return "prevention"

    best_intent = None
    best_score = 0

    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in user_text:
                score = len(keyword)
                if score > best_score:
                    best_score = score
                    best_intent = intent

    if not best_intent:
        for intent, keywords in INTENT_KEYWORDS.items():
            for keyword in keywords:
                score = fuzz.token_set_ratio(keyword, user_text)
                if score >= 80 and score > best_score:
                    best_score = score
                    best_intent = intent

    if not best_intent:
        best_intent = "general"

    return best_intent

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

    return list(set(detected_intents))

def smart_intent_detection(user_text):
    primary_intent = detect_intent(user_text)
    all_intents = detect_multiple_intents(user_text)

    return {
        "primary_intent": primary_intent,
        "all_detected_intents": all_intents,
        "is_disease_related": primary_intent in [
            "symptoms", "causes", "treatment", "prevention"
        ],
        "is_crop_related": primary_intent in [
            "irrigation", "fertilizer", "weather",
            "harvest", "soil", "cultivation"
        ]
    }

if __name__ == "__main__":
    test_questions = [
        "Symptoms of wheat yellow rust",
        "Causes of wheat yellow rust",
        "Treatment for wheat yellow rust"
    ]

    for question in test_questions:
        print("\\n================================================")
        print("Question:", question)
        print("Result:", smart_intent_detection(question))
