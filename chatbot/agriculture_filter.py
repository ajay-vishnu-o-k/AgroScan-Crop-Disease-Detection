# =========================================================
# AgroScan Agriculture Domain Filter
# =========================================================

from rapidfuzz import fuzz
from rapidfuzz import process


# =========================================================
# Agriculture Keywords
# =========================================================

AGRICULTURE_KEYWORDS = [

    # Crops
    "wheat",
    "rice",
    "potato",
    "tomato",
    "paddy",

    # Disease Keywords
    "disease",
    "crop disease",
    "crop diseases",
    "plant disease",
    "leaf disease",
    "blight",
    "rust",
    "spot",
    "fungus",
    "fungal",
    "bacterial",
    "infection",

    # Disease Names
    "late blight",
    "early blight",
    "brown rust",
    "yellow rust",
    "brown spot",
    "bacterial leaf blight",

    # Treatment
    "symptom",
    "symptoms",
    "cause",
    "causes",
    "treatment",
    "prevent",
    "prevention",
    "fungicide",
    "pesticide",
    "medicine",
    "cure",
    "control",

    # Irrigation
    "irrigation",
    "water",
    "watering",
    "rainfall",
    "drip irrigation",
    "sprinkler",
    "soil moisture",

    # Fertilizer
    "fertilizer",
    "fertiliser",
    "npk",
    "nutrient",
    "nutrients",
    "compost",
    "manure",
    "urea",
    "nitrogen",
    "potassium",
    "phosphorus",

    # Weather
    "weather",
    "temperature",
    "humidity",
    "climate",
    "rain",

    # Soil
    "soil",
    "soil type",
    "clay soil",
    "sandy soil",
    "loamy soil",

    # Harvest
    "harvest",
    "harvesting",
    "crop maturity",

    # General
    "crop",
    "cultivation",
    "farming",
    "plant",
    "seed",
    "field",
    "agriculture",

    # App
    "upload image",
    "predict disease",
    "prediction",
    "app",
    "model",
    "scan crop"
]


# =========================================================
# Greeting Keywords
# =========================================================

GREETING_KEYWORDS = [

    "hello",
    "hi",
    "hey",
    "good morning",
    "good evening",
    "good afternoon"
]


# =========================================================
# Non Agriculture Keywords
# =========================================================

NON_AGRICULTURE_KEYWORDS = [

    "football",
    "cricket",
    "movie",
    "cinema",
    "actor",
    "actress",
    "music",
    "song",
    "programming",
    "python language",
    "java",
    "politics",
    "prime minister",
    "president",
    "youtube",
    "instagram",
    "facebook",
    "gaming",
    "pubg",
    "free fire",
    "bitcoin",
    "stock market"
]


# =========================================================
# Clean Text
# =========================================================

def clean_text(text):

    return text.lower().strip()


# =========================================================
# Detect Greeting
# =========================================================

def is_greeting(text):

    text = clean_text(text)

    for word in GREETING_KEYWORDS:

        if word in text:
            return True

    return False


# =========================================================
# Smart Agriculture Match
# =========================================================

def smart_agriculture_match(text):

    text = clean_text(text)

    # -----------------------------------------------------
    # Full Sentence Match
    # -----------------------------------------------------

    result = process.extractOne(

        text,
        AGRICULTURE_KEYWORDS,
        scorer=fuzz.partial_ratio
    )

    if result:

        keyword, score, _ = result

        if score >= 70:

            return keyword

    # -----------------------------------------------------
    # Word Level Match
    # -----------------------------------------------------

    words = text.split()

    for word in words:

        result = process.extractOne(

            word,
            AGRICULTURE_KEYWORDS,
            scorer=fuzz.ratio
        )

        if result:

            keyword, score, _ = result

            if score >= 75:

                return keyword

    return None


# =========================================================
# Detect Agriculture Related
# =========================================================

def is_agriculture_related(text):

    text = clean_text(text)

    # -----------------------------------------------------
    # Exact Match
    # -----------------------------------------------------

    for keyword in AGRICULTURE_KEYWORDS:

        if keyword in text:

            return True

    # -----------------------------------------------------
    # Smart Fuzzy Match
    # -----------------------------------------------------

    fuzzy_match = smart_agriculture_match(text)

    if fuzzy_match:

        return True

    return False


# =========================================================
# Detect Non Agriculture Related
# =========================================================

def is_non_agriculture_related(text):

    text = clean_text(text)

    for keyword in NON_AGRICULTURE_KEYWORDS:

        if keyword in text:

            return True

    return False


# =========================================================
# Main Filter Function
# =========================================================

def agriculture_filter(user_text):

    user_text = clean_text(user_text)

    result = {

        "allowed": False,
        "category": None,
        "message": None
    }

    # -----------------------------------------------------
    # Greeting
    # -----------------------------------------------------

    if is_greeting(user_text):

        result["allowed"] = True

        result["category"] = "greeting"

        result["message"] = (

            "Hello! I am AgroScan Agricultural Assistant. "
            "I can help you with crop diseases, irrigation, "
            "fertilizers, weather conditions, and agriculture "
            "questions related to wheat, rice, potato, and tomato."
        )

        return result

    # -----------------------------------------------------
    # Non Agriculture
    # -----------------------------------------------------

    if is_non_agriculture_related(user_text):

        result["allowed"] = False

        result["category"] = "non_agriculture"

        result["message"] = (

            "This question is not related to agriculture "
            "or AgroScan features. "
            "Please ask questions related to crops, diseases, "
            "irrigation, fertilizers, weather, or farming."
        )

        return result

    # -----------------------------------------------------
    # Agriculture Detection
    # -----------------------------------------------------

    if is_agriculture_related(user_text):

        result["allowed"] = True

        result["category"] = "agriculture"

        result["message"] = (

            "Agriculture related question detected."
        )

        return result

    # -----------------------------------------------------
    # Unknown
    # -----------------------------------------------------

    result["allowed"] = False

    result["category"] = "unknown"

    result["message"] = (

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

    return result


# =========================================================
# Testing
# =========================================================

if __name__ == "__main__":

    test_questions = [

        "Hello",
        "crop diseas",
        "croop diseas",
        "brwn rest",
        "late blite",
        "yelow rust",
        "Potato late blight treatment",
        "Weather for wheat",
        "Best fertilizer for rice"
    ]

    for question in test_questions:

        print("\n================================================")
        print("Question:", question)

        result = agriculture_filter(question)

        print("Result:")
        print(result)
