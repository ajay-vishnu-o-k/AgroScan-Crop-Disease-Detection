
# =========================================================
# AgroScan Synonym Matcher
# =========================================================

from rapidfuzz import fuzz


# =========================================================
# Crop Synonyms
# =========================================================

CROP_SYNONYMS = {

    "wheat": [
        "wheat",
        "wheet",
        "whet"
    ],

    "rice": [
        "rice",
        "paddy"
    ],

    "potato": [
        "potato",
        "potatoes",
        "potatto",
        "aloo"
    ],

    "tomato": [
        "tomato",
        "tomatoes",
        "tomoto"
    ]
}


# =========================================================
# Disease Synonyms
# =========================================================

DISEASE_SYNONYMS = {

    "brown_rust": [
        "brown rust",
        "rust",
        "leaf rust",
        "brown fungus"
    ],

    "yellow_rust": [
        "yellow rust",
        "yellow fungus",
        "yellow leaf disease"
    ],

    "bacterial_leaf_blight": [
        "bacterial leaf blight",
        "leaf blight",
        "rice blight",
        "bacterial blight"
    ],

    "brown_spot": [
        "brown spot",
        "leaf spots",
        "brown leaf spots"
    ],

    "late_blight": [
        "late blight",
        "blight",
        "black spots",
        "leaf rot",
        "fungal blight"
    ],

    "early_blight": [
        "early blight",
        "target spots",
        "brown rings"
    ]
}


# =========================================================
# Disease To Crop Mapping
# =========================================================

DISEASE_CROP_MAPPING = {

    "brown_rust": ["wheat"],

    "yellow_rust": ["wheat"],

    "bacterial_leaf_blight": ["rice"],

    "brown_spot": ["rice"],

    "late_blight": ["potato", "tomato"],

    "early_blight": ["tomato"]
}


# =========================================================
# Detect Crop
# =========================================================

def detect_crop(user_text):

    user_text = user_text.lower()

    # Exact Matching
    for crop, synonyms in CROP_SYNONYMS.items():

        for word in synonyms:

            if word in user_text:
                return crop

    # Fuzzy Matching
    for crop, synonyms in CROP_SYNONYMS.items():

        for word in synonyms:

            score = fuzz.partial_ratio(word, user_text)

            if score >= 85:
                return crop

    return None


# =========================================================
# Detect Disease
# =========================================================

def detect_disease(user_text):

    user_text = user_text.lower()

    # Exact Matching
    for disease, synonyms in DISEASE_SYNONYMS.items():

        for word in synonyms:

            if word in user_text:
                return disease

    # Fuzzy Matching
    for disease, synonyms in DISEASE_SYNONYMS.items():

        for word in synonyms:

            score = fuzz.partial_ratio(word, user_text)

            if score >= 85:
                return disease

    return None


# =========================================================
# Get Possible Crops For Disease
# =========================================================

def get_possible_crops(disease):

    return DISEASE_CROP_MAPPING.get(disease, [])


# =========================================================
# Validate Crop Disease Combination
# =========================================================

def validate_crop_disease(crop, disease):

    possible_crops = get_possible_crops(disease)

    return crop in possible_crops


# =========================================================
# Main Smart Detection Function
# =========================================================

def smart_detect(user_text):

    crop = detect_crop(user_text)

    disease = detect_disease(user_text)

    result = {
        "crop": crop,
        "disease": disease,
        "needs_crop_confirmation": False,
        "possible_crops": []
    }

    # If disease exists but crop missing
    if disease and not crop:

        possible_crops = get_possible_crops(disease)

        # Disease affects multiple crops
        if len(possible_crops) > 1:

            result["needs_crop_confirmation"] = True
            result["possible_crops"] = possible_crops

        # Disease affects only one crop
        elif len(possible_crops) == 1:

            result["crop"] = possible_crops[0]

    # If both detected validate combination
    if crop and disease:

        valid = validate_crop_disease(crop, disease)

        if not valid:

            result["error"] = (
                f"{disease.replace('_', ' ').title()} "
                f"is not found in {crop.title()} crop."
            )

    return result


# =========================================================
# Example Testing
# =========================================================

if __name__ == "__main__":

    tests = [

        "late blight treatment",
        "potato late blight",
        "tomato blight cure",
        "yellow rust in wheat",
        "rice bacterial leaf blight",
        "potatto blight",
        "tomoto early blight"
    ]

    for text in tests:

        print("\nUser Input:", text)

        result = smart_detect(text)

        print(result)
