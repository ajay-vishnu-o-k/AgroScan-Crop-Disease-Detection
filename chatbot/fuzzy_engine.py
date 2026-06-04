# =========================================================
# AgroScan Advanced Fuzzy Engine
# =========================================================

from rapidfuzz import fuzz
from rapidfuzz import process

# =========================================================
# Master Vocabulary
# =========================================================

MASTER_VOCABULARY = [
    # -----------------------------------------------------
    # Disease
    # -----------------------------------------------------
    
    "crop disease",
    "crop diseases",
    "disease",
    "diseases",
    "plant disease",

    # -----------------------------------------------------
    # Crops
    # -----------------------------------------------------

    "wheat",
    "rice",
    "potato",
    "tomato",

    # -----------------------------------------------------
    # Diseases
    # -----------------------------------------------------

    "late blight",
    "early blight",
    "brown rust",
    "yellow rust",
    "brown spot",
    "bacterial leaf blight",

    # -----------------------------------------------------
    # Agriculture Terms
    # -----------------------------------------------------

    "irrigation",
    "fertilizer",
    "fertiliser",
    "watering",
    "harvest",
    "weather",
    "temperature",
    "rainfall",
    "soil",
    "fungicide",
    "pesticide",
    "symptoms",
    "causes",
    "treatment",
    "prevention",
    "cultivation",

    # -----------------------------------------------------
    # App Related
    # -----------------------------------------------------

    "upload image",
    "predict disease",
    "scan crop",
    "crop disease"
]


# =========================================================
# Text Cleaning
# =========================================================

def clean_text(text):

    text = text.lower()

    text = text.strip()

    return text


# =========================================================
# Word Level Fuzzy Correction
# =========================================================

def correct_word(word):

    result = process.extractOne(
        word,
        MASTER_VOCABULARY,
        scorer=fuzz.ratio
    )

    if result:

        matched_word = result[0]
        score = result[1]

        if score >= 80:

            return matched_word

    return word


# =========================================================
# Sentence Level Correction
# =========================================================

def fuzzy_correct_text(user_text):

    user_text = clean_text(user_text)

    words = user_text.split()

    corrected_words = []

    for word in words:

        corrected_word = correct_word(word)

        corrected_words.append(corrected_word)

    corrected_sentence = " ".join(corrected_words)

    return corrected_sentence


# =========================================================
# Smart Phrase Correction
# =========================================================

def smart_phrase_correction(user_text):

    user_text = clean_text(user_text)

    best_match = process.extractOne(
        user_text,
        MASTER_VOCABULARY,
        scorer=fuzz.partial_ratio
    )

    if best_match:

        matched_phrase = best_match[0]
        score = best_match[1]

        if score >= 85:

            return matched_phrase

    return user_text


# =========================================================
# Full Fuzzy Processing Pipeline
# =========================================================

def fuzzy_pipeline(user_text):

    # -----------------------------------------------------
    # Step 1: Clean Text
    # -----------------------------------------------------

    cleaned_text = clean_text(user_text)

    # -----------------------------------------------------
    # Step 2: Word Correction
    # -----------------------------------------------------

    corrected_text = fuzzy_correct_text(cleaned_text)

    # -----------------------------------------------------
    # Step 3: Phrase Correction
    # -----------------------------------------------------

    final_text = smart_phrase_correction(corrected_text)

    result = {

        "original_text": user_text,

        "cleaned_text": cleaned_text,

        "corrected_text": corrected_text,

        "final_text": final_text
    }

    return result


# =========================================================
# Example Testing
# =========================================================

if __name__ == "__main__":

    test_inputs = [

        "potatto blite treatment",

        "tomoto early blite",

        "wheet rust symptoms",

        "bactrial blight in rice",

        "irrigtion for potato",

        "fertiliser for wheat",

        "harvst time for rice",

        "weathr for tomato",

        "uplod image",

        "predict diseese"
    ]

    for text in test_inputs:

        print("\n================================================")
        print("USER INPUT:", text)

        result = fuzzy_pipeline(text)

        print("\nRESULT:")

        for key, value in result.items():

            print(f"{key}: {value}")

