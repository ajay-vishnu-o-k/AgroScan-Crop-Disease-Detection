# =========================================================
# AgroScan Entity Extractor
# =========================================================

from rapidfuzz import fuzz
from rapidfuzz import process

from synonym_matcher import (
    CROP_SYNONYMS,
    DISEASE_SYNONYMS,
    DISEASE_CROP_MAPPING
)

from data.disease_data import DISEASE_DATABASE


# =========================================================
# Detect Crop
# =========================================================

def detect_crop(user_text):

    user_text = user_text.lower()

    best_crop = None
    best_score = 0

    # -----------------------------------------------------
    # Exact Matching
    # -----------------------------------------------------

    for crop, synonyms in CROP_SYNONYMS.items():

        for synonym in synonyms:

            if synonym in user_text:

                score = len(synonym)

                if score > best_score:

                    best_score = score
                    best_crop = crop

    # -----------------------------------------------------
    # Fuzzy Matching
    # -----------------------------------------------------

    if not best_crop:

        for crop, synonyms in CROP_SYNONYMS.items():

            for synonym in synonyms:

                score = fuzz.partial_ratio(
                    synonym,
                    user_text
                )

                if score >= 80 and score > best_score:

                    best_score = score
                    best_crop = crop

    return best_crop


# =========================================================
# Detect Disease
# =========================================================

def detect_disease(user_text):

    user_text = user_text.lower()

    best_disease = None
    best_score = 0

    # -----------------------------------------------------
    # Exact Matching
    # -----------------------------------------------------

    for disease, synonyms in DISEASE_SYNONYMS.items():

        for synonym in synonyms:

            if synonym in user_text:

                score = len(synonym)

                if score > best_score:

                    best_score = score
                    best_disease = disease

    # -----------------------------------------------------
    # Smart Fuzzy Matching
    # -----------------------------------------------------

    if not best_disease:

        for disease, synonyms in DISEASE_SYNONYMS.items():

            for synonym in synonyms:

                # Full text fuzzy

                score = fuzz.partial_ratio(
                    synonym,
                    user_text
                )

                if score > best_score:

                    best_score = score
                    best_disease = disease

                # Word level fuzzy

                words = user_text.split()

                for word in words:

                    word_score = fuzz.partial_ratio(
                        word,
                        synonym
                    )

                    if word_score > best_score:

                        best_score = word_score
                        best_disease = disease

    # -----------------------------------------------------
    # Threshold
    # -----------------------------------------------------

    if best_score >= 60:

        return best_disease

    return None


# =========================================================
# Get Crop From Disease
# =========================================================

def get_crop_from_disease(disease):

    if disease in DISEASE_CROP_MAPPING:

        possible_crops = DISEASE_CROP_MAPPING[disease]

        if len(possible_crops) == 1:

            return possible_crops[0]

    return None


# =========================================================
# Validate Crop Disease Combination
# =========================================================

def validate_crop_and_disease(crop, disease):

    if disease not in DISEASE_CROP_MAPPING:

        return False

    valid_crops = DISEASE_CROP_MAPPING[disease]

    return crop in valid_crops


# =========================================================
# Extract Entities
# =========================================================

def extract_entities(user_text):

    crop = detect_crop(user_text)

    disease = detect_disease(user_text)

    result = {

        "crop": crop,

        "disease": disease,

        "crop_detected": crop is not None,

        "disease_detected": disease is not None,

        "needs_crop_confirmation": False,

        "possible_crops": [],

        "is_valid_combination": True,

        "error_message": None
    }

    # -----------------------------------------------------
    # If Disease Exists But Crop Missing
    # -----------------------------------------------------

    if disease and not crop:

        possible_crops = DISEASE_CROP_MAPPING.get(
            disease,
            []
        )

        # Multiple crops possible

        if len(possible_crops) > 1:

            result["needs_crop_confirmation"] = True

            result["possible_crops"] = possible_crops

        # Single crop possible

        elif len(possible_crops) == 1:

            result["crop"] = possible_crops[0]

            result["crop_detected"] = True

    # -----------------------------------------------------
    # Validate Crop + Disease
    # -----------------------------------------------------

    if crop and disease:

        is_valid = validate_crop_and_disease(
            crop,
            disease
        )

        result["is_valid_combination"] = is_valid

        if not is_valid:

            result["error_message"] = (

                f"{disease.replace('_', ' ').title()} "
                f"is not found in "
                f"{crop.title()} crop."
            )

    return result


# =========================================================
# AgroScan Smart Entity Extractor
# =========================================================

VALID_CROPS = [

    "wheat",
    "rice",
    "potato",
    "tomato"
]


# =========================================================
# Disease Mapping
# =========================================================

DISEASE_TO_CROPS = {}

for crop, diseases in DISEASE_DATABASE.items():

    for disease in diseases.keys():

        if disease == "healthy":
            continue

        if disease not in DISEASE_TO_CROPS:

            DISEASE_TO_CROPS[disease] = []

        DISEASE_TO_CROPS[disease].append(crop)


# =========================================================
# All Diseases List
# =========================================================

ALL_DISEASES = list(DISEASE_TO_CROPS.keys())


# =========================================================
# Format Helper
# =========================================================

def clean_text(text):

    return text.lower().strip()


# =========================================================
# Fuzzy Match Helper
# =========================================================

def fuzzy_match(text, choices, threshold=70):

    result = process.extractOne(
        text,
        choices,
        scorer=fuzz.ratio
    )

    if result:

        match, score, _ = result

        if score >= threshold:

            return match

    return None


# =========================================================
# Smart Entity Extractor
# =========================================================

def smart_entity_extractor(user_text):

    text = clean_text(user_text)

    detected_crop = None
    detected_disease = None

    # =====================================================
    # Detect Crop
    # =====================================================

    for crop in VALID_CROPS:

        if crop in text:

            detected_crop = crop
            break

    # =====================================================
    # Fuzzy Crop Match
    # =====================================================

    if not detected_crop:

        fuzzy_crop = fuzzy_match(
            text,
            VALID_CROPS,
            threshold=75
        )

        if fuzzy_crop:

            detected_crop = fuzzy_crop

    # =====================================================
    # Detect Disease Directly
    # =====================================================

    for disease in ALL_DISEASES:

        disease_text = disease.replace("_", " ")

        if disease_text in text:

            detected_disease = disease
            break

    # =====================================================
    # Safe Fuzzy Disease Match
    # =====================================================

    if not detected_disease:

        best_match = None
        best_score = 0

        # ---------------------------------------------
        # Ignore crop-only messages
        # ---------------------------------------------

        if text not in VALID_CROPS:

            for disease in ALL_DISEASES:

                disease_text = disease.replace("_", " ")

                score = fuzz.partial_ratio(
                    disease_text,
                    text
                )

                # Strong threshold
                if score >= 85 and score > best_score:

                    best_score = score
                    best_match = disease

        if best_match:

            detected_disease = best_match

    # =====================================================
    # Result Template
    # =====================================================

    result = {

        "crop": detected_crop,

        "disease": detected_disease,

        "valid": True,

        "error": None,

        "needs_crop_confirmation": False,

        "possible_crops": []
    }

    # =====================================================
    # Disease Without Crop
    # =====================================================

    if detected_disease and not detected_crop:

        possible_crops = DISEASE_TO_CROPS.get(
            detected_disease,
            []
        )

        # Multiple crops

        if len(possible_crops) > 1:

            result["needs_crop_confirmation"] = True

            result["possible_crops"] = possible_crops

        # Single crop

        elif len(possible_crops) == 1:

            result["crop"] = possible_crops[0]

    # =====================================================
    # Validate Combination
    # =====================================================

    if result["crop"] and detected_disease:

        crop = result["crop"]

        if detected_disease not in DISEASE_DATABASE[crop]:

            result["valid"] = False

            result["error"] = (

                f"{detected_disease.replace('_', ' ').title()} "
                f"is not found in {crop.title()} crop."
            )

    return result

    # =====================================================
    # Final Result
    # =====================================================

    return {

        "crop": detected_crop,

        "disease": detected_disease,

        "valid": True,

        "needs_crop_confirmation": False,

        "possible_crops": []
    }


# =========================================================
# Testing
# =========================================================

if __name__ == "__main__":

    while True:

        text = input("YOU: ")

        result = smart_entity_extractor(text)

        print("\nRESULT:\n")

        print(result)

        print("\n" + "=" * 50 + "\n")
