# ============================================================
#   AgroScan — Smart Crop Disease Detection
#   Streamlit App  |  MobileNetV2 models  |  SQLite DB
# ============================================================

import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import os, requests
import warnings
warnings.filterwarnings("ignore")
tf.get_logger().setLevel("ERROR")

# ─── GLOBAL DEEP LEARNING MODEL CONFIGURATION INTERCEPTOR ───
# This patches Keras's deserialization loop globally to safely strip modern
# Keras 3 graph signatures before they hit the legacy Keras 2 constructor engines.
import keras

def sanitize_keras_config(d):
    if isinstance(d, dict):
        # 1. Sanitize input and preprocessing layer parameter dictionaries
        if "config" in d and isinstance(d["config"], dict):
            cfg = d["config"]
            if "batch_shape" in cfg:
                cfg["batch_input_shape"] = cfg.pop("batch_shape")
            if "optional" in cfg:
                cfg.pop("optional")
            if "data_format" in cfg:
                cfg.pop("data_format")
            # Flatten Keras 3 complex DTypePolicy objects into a legacy string name
            if "dtype" in cfg and isinstance(cfg["dtype"], dict):
                cfg["dtype"] = cfg["dtype"].get("config", {}).get("name", "float32")

        if "batch_shape" in d:
            d["batch_input_shape"] = d.pop("batch_shape")
        if "optional" in d:
            d.pop("optional")
        if "data_format" in d:
            d.pop("data_format")
        if "dtype" in d and isinstance(d["dtype"], dict):
            d["dtype"] = d["dtype"].get("config", {}).get("name", "float32")
            
        # 2. Re-route functional model structural definitions smoothly
        if d.get("module") == "keras.src.models.functional" or d.get("class_name") == "Functional":
            d["class_name"] = "Functional"
            try:
                import keras.src.engine.functional
                d["module"] = "keras.src.engine.functional"
            except ImportError:
                d["module"] = "keras.engine.functional"
                
        for k, v in list(d.items()):
            sanitize_keras_config(v)
    elif isinstance(d, list):
        for item in d:
            sanitize_keras_config(item)

# Bind the sanitizer hook into all available Keras layer object deserialization routines
if hasattr(keras.layers, "deserialize"):
    original_layers_deserialize = keras.layers.deserialize
    def patched_layers_deserialize(config, custom_objects=None):
        sanitize_keras_config(config)
        return original_layers_deserialize(config, custom_objects=custom_objects)
    keras.layers.deserialize = patched_layers_deserialize
    tf.keras.layers.deserialize = patched_layers_deserialize

try:
    from keras.src.saving import serialization_lib
    original_deserialize_obj = serialization_lib.deserialize_keras_object
    def patched_deserialize_obj(*args, **kwargs):
        if args:
            sanitize_keras_config(args[0])
        if "config" in kwargs:
            sanitize_keras_config(kwargs["config"])
        return original_deserialize_obj(*args, **kwargs)
    serialization_lib.deserialize_keras_object = patched_deserialize_obj
except Exception:
    pass

# ─── CHATBOT ENGINE ─────────────────────────────────────────
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from chatbot.response_generator import generate_chatbot_response as chatbot_response
except Exception:
    try:
        from chatbot.chatbot_engine import chatbot_response
    except Exception:
        def chatbot_response(text):
            return "Chatbot engine not found. Please check your chatbot folder."

# ─── PAGE CONFIG ────────────────────────────────────────────
st.set_page_config(
    page_title="AgroScan",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── PATHS ──────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))

MODEL_PATHS = {
    "Rice":   os.path.join(BASE_DIR, "rice_model.h5"),
    "Tomato": os.path.join(BASE_DIR, "tomato_model.h5"),
    "Potato": os.path.join(BASE_DIR, "potato_model.h5"),
    "Wheat":  os.path.join(BASE_DIR, "wheat_disease_finetuned_model.h5"),
}

CLASS_LABELS = {
    "Rice":   ["Bacterial Leaf Blight", "Brown Spot", "Healthy"],
    "Tomato": ["Early Blight", "Healthy", "Late Blight"],
    "Potato": ["Early Blight", "Healthy", "Late Blight"],
    "Wheat":  ["Brown Rust", "Healthy", "Yellow Rust"],
}

CROP_EMOJI = {"Rice":"🌾", "Tomato":"🍅", "Potato":"🥔", "Wheat":"🌿"}

# ─── WEATHER API KEY ────────────────────────────────────────
OWM_API_KEY = "4f81d79be632f9cbe6a92458c47efa2f"

# ============================================================
#   CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Custom App-Wide Scrollbars ── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #F8F5EF; }
::-webkit-scrollbar-thumb { background: #C8C0B0; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #2D6A2D; }
section[data-testid="stSidebar"] ::-webkit-scrollbar-track { background: #1B3A1B; }
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); }
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover { background: #4CAF50; }

html, body, [class*="css"], p, span, div, label {
    font-family: 'DM Sans', sans-serif;
    color: #110A05;
    font-size: 15px;
}

/* General text size boost — only size, NOT color, to avoid overriding white-on-dark areas */
p, li {
    font-size: 15px !important;
    line-height: 1.6 !important;
}

/* ── Main background ── */
.main .block-container {
    background: #F8F5EF;
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1100px;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1B3A1B 0%, #2D4A1E 100%) !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stRadio > div > label > div,
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stTextInput > div > div > input,
section[data-testid="stSidebar"] .stNumberInput > div > div > input,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] a,
section[data-testid="stSidebar"] button,
section[data-testid="stSidebar"] [data-baseweb="tab"],
section[data-testid="stSidebar"] .stMarkdown {
    color: #F1F8E9 !important;
    font-size: 17px !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] .stTabs [data-baseweb="tab"] {
    font-size: 17px !important;
    font-weight: 700 !important;
}
section[data-testid="stSidebar"] .stTabs [data-baseweb="tab"] p,
section[data-testid="stSidebar"] .stTabs [data-baseweb="tab"] span,
section[data-testid="stSidebar"] .stTabs [data-baseweb="tab"] div {
    font-size: 17px !important;
    font-weight: 700 !important;
    color: #F1F8E9 !important;
}
section[data-testid="stSidebar"] .stRadio label span,
section[data-testid="stSidebar"] .stRadio label p,
section[data-testid="stSidebar"] .stRadio div {
    font-size: 17px !important;
    font-weight: 600 !important;
    color: #F1F8E9 !important;
}
section[data-testid="stSidebar"] .stMarkdown p {
    font-size: 17px !important;
    color: #F1F8E9 !important;
}

section[data-testid="stSidebar"] div.sidebar-alert-crit { color: #C62828 !important; }
section[data-testid="stSidebar"] div.sidebar-alert-sub  { color: #B71C1C !important; }
section[data-testid="stSidebar"] div.sidebar-alert-good { color: #ffffff !important; font-weight: 800 !important; }

section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stTextInput > div > div > input,
section[data-testid="stSidebar"] .stNumberInput > div > div > input {
    background: rgba(255,255,255,0.15) !important;
    border: 1.5px solid rgba(255,255,255,0.3) !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    font-size: 17px !important;
}

/* ── Card Lift Micro-Interactions ── */
.metric-card, .scan-item, .info-box, .healthy-box, .irr-card {
    transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.25s ease !important;
}
.metric-card:hover, .scan-item:hover, .info-box:hover, .healthy-box:hover, .irr-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 20px rgba(45, 106, 45, 0.08) !important;
    border-color: #A5D6A7 !important;
}

/* ── Metric cards ── */
.metric-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 22px 24px;
    border: 1.5px solid #C8BFAF;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 8px;
}
.metric-card .mc-label {
    font-size: 16px !important;
    text-transform: uppercase;
    letter-spacing: .08em;
    color: #4A3A2A;
    font-weight: 700;
    margin-bottom: 6px;
}
.metric-card .mc-value {
    font-family: 'Syne', sans-serif;
    font-size: 36px !important;
    font-weight: 800;
    color: #110A05;
    line-height: 1;
}
.metric-card .mc-sub {
    font-size: 17px !important;
    color: #2E7D32;
    font-weight: 600;
    margin-top: 4px;
}

/* ── Section heading ── */
.section-head {
    font-family: 'Syne', sans-serif;
    font-size: 28px !important;
    font-weight: 800;
    color: #110A05;
    border-left: 5px solid #2D6A2D;
    padding-left: 14px;
    margin: 22px 0 16px;
}

/* ── Disease result banner ── */
.disease-banner, .conf-wrap, [data-testid="stNotificationContent"] {
    animation: fadeInSlide 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes fadeInSlide {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.disease-banner {
    border-radius: 16px;
    padding: 22px 26px;
    margin-bottom: 18px;
    border: 2px solid;
    border-left: 8px solid;
}
.disease-banner.high    { background: #FFEBEE; border-color: #C62828; }
.disease-banner.med     { background: #FFF3E0; border-color: #E65100; }
.disease-banner.healthy { background: #1B5E20; border-color: #2E7D32; }
.disease-banner.healthy h2,
.disease-banner.healthy p { color: #ffffff !important; }
.disease-banner h2 {
    font-family: 'Syne', sans-serif;
    font-size: 30px !important;
    font-weight: 800;
    margin: 0 0 6px;
    color: #110A05;
}
.disease-banner p {
    font-size: 19px !important;
    margin: 0;
    color: #110A05;
    font-weight: 500;
}

/* ── Info box ── */
.info-box {
    background: #ffffff;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 12px;
    border: 1.5px solid #C8BFAF;
}
.info-box h4 {
    font-family: 'Syne', sans-serif;
    font-size: 21px !important;
    font-weight: 700;
    color: #110A05;
    margin: 0 0 10px;
}
.info-box ul { margin: 0; padding-left: 18px; }
.info-box li { font-size: 19px !important; line-height: 2 !important; color: #110A05; }

/* ── Healthy tip box ── */
.healthy-box {
    background: #1B5E20;
    border-radius: 14px;
    padding: 20px 22px;
    border: 1.5px solid #81C784;
    margin-bottom: 12px;
}
.healthy-box h4 {
    font-family: 'Syne', sans-serif;
    font-size: 21px !important;
    font-weight: 700;
    color: #ffffff !important;
    margin: 0 0 10px;
}
.healthy-box li { font-size: 19px !important; line-height: 2 !important; color: #ffffff !important; font-weight: 500; }
.healthy-box ul li, .healthy-box p, .healthy-box span, .healthy-box div {
    color: #ffffff !important;
}

/* ── Irrigation card ── */
.irr-card {
    background: #F0F8FF;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 12px;
    border: 1.5px solid #90CAF9;
}
.irr-card h4 {
    font-family: 'Syne', sans-serif;
    font-size: 21px !important;
    font-weight: 700;
    color: #0D47A1;
    margin: 0 0 10px;
}
.irr-card p, .irr-card li { font-size: 19px !important; line-height: 2 !important; color: #0D47A1; font-weight: 500; }

/* ── Weather card ── */
@keyframes auraBreath {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.weather-card {
    background: linear-gradient(-45deg, #07170C, #13331C, #1C3D25, #0B2112);
    background-size: 300% 300%;
    animation: auraBreath 10s ease infinite;
    border-radius: 18px;
    padding: 24px 26px;
    margin-bottom: 14px;
    border: 2px solid #66BB6A;
    box-shadow: 0 8px 24px rgba(0,0,0,0.22);
    position: relative;
    overflow: hidden;
}
.weather-card * { color: #ffffff !important; }
.weather-card .wc-city  { font-size: 19px !important; font-weight: 700; margin-bottom: 10px; letter-spacing: 0.04em; color: #E8F5E9 !important; }
.weather-card .wc-temp  { font-family: 'Syne', sans-serif; font-size: 58px !important; font-weight: 800; line-height: 1; text-shadow: 0 2px 8px rgba(0,0,0,0.3); }
.weather-card .wc-desc  { font-size: 19px !important; text-transform: capitalize; margin-top: 6px; font-weight: 700; color: #C8E6C9 !important; }
.weather-card .wc-stats { display: flex; gap: 24px; margin-top: 18px; font-size: 18px !important; font-weight: 600; border-top: 1px solid rgba(255,255,255,0.18); padding-top: 12px; }
.weather-card .wc-stats span { font-weight: 600 !important; font-size: 18px !important; }

/* ── Risk badge ── */
.risk-badge {
    display: inline-block;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 15px;
    font-weight: 700;
    margin: 6px 0;
}
.risk-high { background: #FFEBEE; color: #C62828; border: 2px solid #C62828; }
.risk-med  { background: #FFF3E0; color: #E65100; border: 2px solid #E65100; }
.risk-low  { background: #1B5E20; color: #ffffff;  border: 2px solid #2E7D32; }

/* ── Confidence bar ── */
.conf-wrap { background: #E8E2D8; border-radius: 8px; height: 12px; overflow: hidden; margin-top: 8px; }
.conf-fill  { height: 100%; border-radius: 8px; }

/* ── Recent scan item ── */
.scan-item {
    background: #ffffff;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 8px;
    border: 1.5px solid #C8BFAF;
}
.scan-item .si-title { font-size: 19px !important; font-weight: 700; color: #110A05; }
.scan-item .si-date  { font-size: 16px !important; color: #4A3A2A; margin-top: 4px; }

/* ── Buttons ── */
.stButton > button {
    background: #2D6A2D !important;
    color: #ffffff !important;
    border-radius: 12px !important;
    border: none !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 19px !important;
    padding: 14px 28px !important;
}
.stButton > button:hover { background: #1B4A1B !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    padding: 10px 20px !important;
    background: #EDE8DF !important;
    border: none !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 18px !important;
    color: #110A05 !important;
    font-weight: 800 !important;
}
.stTabs [aria-selected="true"] {
    background: #2D6A2D !important;
    color: #ffffff !important;
    font-weight: 800 !important;
}
.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] span,
.stTabs [aria-selected="true"] div {
    color: #ffffff !important;
    font-weight: 800 !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stNumberInput input,
.stNumberInput > div > div > div > input,
.stSelectbox > div > div,
.stTextArea > div > div > textarea {
    background: #ffffff !important;
    color: #110A05 !important;
    border: 1.5px solid #9A8E7C !important;
    border-radius: 10px !important;
    font-size: 20px !important;
}
.stNumberInput > div {
    background: #ffffff !important;
    color: #110A05 !important;
}
.stNumberInput button {
    background: #f0ede8 !important;
    color: #110A05 !important;
    border: 1px solid #9A8E7C !important;
}
.stNumberInput button svg,
.stNumberInput button p {
    color: #110A05 !important;
    fill: #110A05 !important;
}
.stTextInput label, .stNumberInput label,
.stSelectbox label, .stSlider label,
.stTextArea label, .stFileUploader label {
    color: #110A05 !important;
    font-size: 18px !important;
    font-weight: 700 !important;
}

/* ── Slider ── */
.stSlider > div > div > div > div { background: #4CAF50 !important; }

/* ── Upload zone ── */
[data-testid="stFileUploader"] section {
            background: #ffffff !important;
            border: 2px dashed #2D6A2D !important;
            border-radius: 16px !important;
        }
        [data-testid="stFileUploader"] section span,
        [data-testid="stFileUploader"] section p,
        [data-testid="stFileUploader"] section div,
        [data-testid="stFileUploader"] section small,
        [data-testid="stFileUploader"] section * {
            color: #110A05 !important;
            font-weight: 700 !important;
            font-size: 16px !important;
        }
        [data-testid="stFileUploader"] section svg {
            fill: #2D6A2D !important;
        }

/* ── Dataframe ── */
.stDataFrame { border-radius: 12px !important; overflow: hidden; }
[data-testid="stDataFrameResizable"] { color: #110A05 !important; font-size: 18px !important; }

/* ── Alerts ── */
.stAlert { border-radius: 12px !important; }

/* ── Expander ── */
.streamlit-expanderHeader { color: #110A05 !important; font-weight: 700 !important; font-size: 19px !important; }

/* ── Radio buttons ── */
.stRadio > div > label > div { color: #110A05 !important; font-size: 18px !important; }

/* ── Active Crop Soft Glow ── */
div[data-testid="column"] > div:has(div[style*="background:#2D6A2D"]) {
    box-shadow: 0 0 16px rgba(45, 106, 45, 0.4) !important;
    animation: activePulse 3s ease-in-out infinite;
}
@keyframes activePulse {
    0%   { box-shadow: 0 0 12px rgba(45, 106, 45, 0.3); }
    50%  { box-shadow: 0 0 20px rgba(45, 106, 45, 0.5); }
    100% { box-shadow: 0 0 12px rgba(45, 106, 45, 0.3); }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
#   FARMER STORAGE
# ============================================================
import json, hashlib
from datetime import datetime

FARMERS_FILE = os.path.join(BASE_DIR, "farmers.json")

def _load_farmers():
    if os.path.exists(FARMERS_FILE):
        with open(FARMERS_FILE, "r") as f:
            return json.load(f)
    return {}

def _save_farmers(data):
    with open(FARMERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def _make_id(username, location):
    raw = f"{username}{location}{datetime.now().timestamp()}"
    return "FRM-" + hashlib.md5(raw.encode()).hexdigest()[:6].upper()

def register_farmer(username, location, farm_size, main_crop, password):
    farmers = _load_farmers()
    for fid, data in farmers.items():
        if data["username"].lower() == username.lower():
            return None, "Username already exists. Please login."
    fid = _make_id(username, location)
    farmers[fid] = {
        "farmer_id":  fid,
        "username":   username,
        "location":   location,
        "farm_size":  str(farm_size),
        "main_crop":  main_crop,
        "password":   hashlib.sha256(password.encode()).hexdigest(),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    _save_farmers(farmers)
    return farmers[fid], None

def login_farmer(username, password):
    farmers = _load_farmers()
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    for fid, data in farmers.items():
        if data["username"].lower() == username.lower() and data["password"] == pw_hash:
            return data, None
    return None, "Incorrect username or password."

def update_farmer_crop(new_crop):
    st.session_state.farmer_data["main_crop"] = new_crop
    farmers = _load_farmers()
    fid = st.session_state.farmer_data["farmer_id"]
    if fid in farmers:
        farmers[fid]["main_crop"] = new_crop
        _save_farmers(farmers)

def _get_fid():
    return st.session_state.farmer_data["farmer_id"]

def add_scan_record(crop_type, result, confidence):
    record = {
        "crop_type":         crop_type,
        "prediction_result": result,
        "confidence":        confidence,
        "scan_date":         datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    if "scan_history" not in st.session_state:
        st.session_state.scan_history = []
    st.session_state.scan_history.insert(0, record)
    farmers = _load_farmers()
    fid = _get_fid()
    if fid in farmers:
        farmers[fid].setdefault("scan_history", []).insert(0, record)
        _save_farmers(farmers)

def add_irrigation_record(crop_type, rainfall, temperature, soil_type, recs):
    record = {
        "crop_type":      crop_type,
        "rainfall":       rainfall,
        "temperature":    temperature,
        "soil_type":      soil_type,
        "recommendation": "\n".join(recs),
        "log_date":       datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    if "irr_history" not in st.session_state:
        st.session_state.irr_history = []
    st.session_state.irr_history.insert(0, record)
    farmers = _load_farmers()
    fid = _get_fid()
    if fid in farmers:
        farmers[fid].setdefault("irr_history", []).insert(0, record)
        _save_farmers(farmers)

def load_farmer_history():
    farmers = _load_farmers()
    fid = _get_fid()
    if fid in farmers:
        st.session_state.scan_history = farmers[fid].get("scan_history", [])
        st.session_state.irr_history  = farmers[fid].get("irr_history",  [])
    else:
        st.session_state.scan_history = []
        st.session_state.irr_history  = []


# ============================================================
#   MODEL LOADER
# ============================================================
@st.cache_resource(show_spinner="Loading AI model…")
def load_model(crop: str):
    path = MODEL_PATHS[crop]
    if not os.path.exists(path):
        st.error(f"Model file not found: {path}")
        return None

    # Gather clean dynamic functional dictionary objects mapping overrides
    custom_map = {}
    try:
        import keras.engine.functional as legacy_funct
        custom_map["Functional"] = legacy_funct.Functional
    except ImportError:
        try:
            import keras.src.engine.functional as legacy_src_funct
            custom_map["Functional"] = legacy_src_funct.Functional
        except ImportError:
            pass

    # Try standard model load loop
    try:
        return tf.keras.models.load_model(path, compile=False, custom_objects=custom_map)
    except Exception:
        pass

    # For .keras format — unzip package stream and execute target JSON structural adjustments
    if path.endswith(".keras"):
        try:
            import zipfile
            import tempfile
            import json

            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(path, "r") as z:
                    z.extractall(tmpdir)

                config_path = os.path.join(tmpdir, "config.json")
                weights_path = os.path.join(tmpdir, "model.weights.h5")

                if os.path.exists(config_path):
                    with open(config_path, "r") as cf:
                        raw_config = cf.read()
                    
                    patched_config = raw_config.replace("keras.src.models.functional", "keras.src.engine.functional")
                    config = json.loads(patched_config)

                    # Strip cross-version metrics before compiling internal matrices
                    sanitize_keras_config(config)

                    model = tf.keras.models.model_from_json(
                        json.dumps(config),
                        custom_objects=custom_map
                    )
                    if os.path.exists(weights_path):
                        model.load_weights(weights_path)
                    return model
        except Exception:
            pass

    # Fallback secondary layout recovery reload strategy
    try:
        return tf.keras.models.load_model(
            path,
            compile=False,
            custom_objects=custom_map
        )
    except Exception as e:
        st.error(f"Model load error for {crop}: {str(e)}")
        return None

def predict(model, img_pil, crop: str):
    img  = img_pil.convert("RGB").resize((224, 224))
    arr  = np.array(img, dtype=np.float32) / 255.0
    arr  = np.expand_dims(arr, 0)
    pred = model.predict(arr, verbose=0)[0]
    idx  = int(np.argmax(pred))
    conf = float(pred[idx]) * 100
    label= CLASS_LABELS[crop][idx]
    return label, conf, pred


# ============================================================
#   DISEASE DATABASE
# ============================================================
DISEASE_DB = {
  "Tomato": {
    "Healthy": {
      "status": "The tomato plant is healthy and shows no visible signs of disease.",
      "maintenance_tips": [
        "Continue proper irrigation practices",
        "Provide balanced fertilizers regularly",
        "Monitor leaves regularly for unusual spots or discoloration",
        "Ensure proper sunlight exposure",
        "Maintain good air circulation around plants"
      ]
    },
    "Early Blight": {
      "causes": [
        "Fungal infection caused by Alternaria solani in warm and humid conditions",
        "Disease spreads rapidly when leaves remain wet for long periods",
        "Poor air circulation and unhealthy soil conditions increase risk"
      ],
      "prevention": [
        "Avoid overhead watering",
        "Use disease-free seeds",
        "Maintain proper spacing between plants",
        "Remove infected leaves immediately",
        "Practice crop rotation each season"
      ],
      "treatment": [
        "Apply recommended fungicide spray",
        "Remove and destroy infected plant parts",
        "Improve air circulation around plants",
        "Use copper-based fungicide if necessary"
      ]
    },
    "Late Blight": {
      "causes": [
        "Caused by Phytophthora infestans during cool and wet weather",
        "Excess moisture and poor ventilation help disease spread quickly",
        "Continuous rainfall and damp leaves increase infection risk"
      ],
      "prevention": [
        "Avoid excessive irrigation",
        "Use resistant tomato varieties",
        "Ensure proper field drainage",
        "Monitor weather conditions regularly"
      ],
      "treatment": [
        "Apply fungicide immediately upon detection",
        "Remove all infected plants from field",
        "Destroy severely affected crops",
        "Maintain dry foliage conditions"
      ]
    }
  },
  "Potato": {
    "Healthy": {
      "status": "The potato crop is healthy and growing under suitable conditions.",
      "maintenance_tips": [
        "Maintain balanced soil moisture levels",
        "Use proper nutrient management",
        "Inspect plants regularly for disease symptoms",
        "Avoid overwatering the field",
        "Keep the field free from weeds"
      ]
    },
    "Early Blight": {
      "causes": [
        "Fungal infection thriving in warm and humid environments",
        "Poor soil nutrition and water stress increase vulnerability",
        "Disease spreads faster when infected debris remains in field"
      ],
      "prevention": [
        "Practice crop rotation every season",
        "Use certified disease-free seeds",
        "Maintain proper field sanitation",
        "Avoid water stress on plants"
      ],
      "treatment": [
        "Apply suitable fungicide immediately",
        "Remove infected leaves from plant",
        "Improve soil fertility with balanced nutrients",
        "Monitor disease spread regularly"
      ]
    },
    "Late Blight": {
      "causes": [
        "Infection by Phytophthora infestans in cool and wet conditions",
        "High humidity and poor drainage encourage rapid development",
        "Continuous wet weather helps pathogen spread quickly"
      ],
      "prevention": [
        "Avoid overwatering the crop",
        "Use resistant potato varieties",
        "Ensure proper field drainage",
        "Inspect crops frequently during wet seasons"
      ],
      "treatment": [
        "Apply fungicide spray immediately",
        "Remove infected plants from the field",
        "Destroy all affected tubers",
        "Maintain proper field hygiene throughout season"
      ]
    }
  },
  "Wheat": {
    "Healthy": {
      "status": "The wheat crop is healthy and currently free from visible diseases.",
      "maintenance_tips": [
        "Monitor crop growth regularly",
        "Maintain proper irrigation schedule",
        "Use balanced fertilization",
        "Ensure proper spacing and ventilation",
        "Inspect fields during humid weather conditions"
      ]
    },
    "Brown Rust": {
      "causes": [
        "Fungal infection caused by Puccinia triticina in warm and humid conditions",
        "Dense crop growth and excess moisture create favorable environment",
        "Fungus spreads through airborne spores infecting wheat leaves"
      ],
      "prevention": [
        "Use resistant wheat varieties",
        "Avoid excessive nitrogen fertilizer",
        "Ensure proper plant spacing for airflow",
        "Monitor fields frequently during warm weather"
      ],
      "treatment": [
        "Apply fungicide spray at first sign of infection",
        "Remove infected plant debris from field",
        "Practice crop rotation to break disease cycle",
        "Control excess moisture in affected fields"
      ]
    },
    "Yellow Rust": {
      "causes": [
        "Fungal infection spreading rapidly during cool and moist weather",
        "High humidity and dense planting increase disease spread",
        "Fungal spores carried by wind and moisture between plants"
      ],
      "prevention": [
        "Use resistant seed varieties",
        "Maintain proper field ventilation",
        "Avoid excessive irrigation",
        "Monitor crops closely during cool seasons"
      ],
      "treatment": [
        "Apply appropriate fungicide immediately",
        "Remove infected leaves from plants",
        "Destroy severely infected plants completely",
        "Monitor disease progression regularly"
      ]
    }
  },
  "Rice": {
    "Healthy": {
      "status": "The rice crop is healthy and growing properly without visible disease symptoms.",
      "maintenance_tips": [
        "Maintain proper water levels in the field",
        "Use balanced fertilizers for healthy growth",
        "Inspect plants regularly for early disease symptoms",
        "Keep the field clean and free from weeds",
        "Ensure proper drainage and airflow"
      ]
    },
    "Brown Spot": {
      "causes": [
        "Fungal infection in humid and nutrient-deficient conditions",
        "Poor soil fertility and lack of nutrients increase infection risk",
        "Disease spreads rapidly during continuous wet and warm weather"
      ],
      "prevention": [
        "Use disease-resistant rice varieties",
        "Apply balanced fertilizers regularly",
        "Maintain proper field drainage",
        "Use certified healthy seeds only",
        "Avoid excessive moisture in the field"
      ],
      "treatment": [
        "Apply suitable fungicide spray",
        "Remove infected leaves and plant debris",
        "Improve soil nutrition with proper fertilizers",
        "Monitor disease spread regularly"
      ]
    },
    "Bacterial Leaf Blight": {
      "causes": [
        "Bacterial infection spreading in warm and humid environments",
        "Heavy rainfall and strong winds spread bacteria between plants",
        "Excess nitrogen fertilizer and standing water increase severity"
      ],
      "prevention": [
        "Use resistant rice varieties",
        "Avoid excessive nitrogen fertilizer",
        "Ensure proper field drainage",
        "Use disease-free seeds",
        "Monitor crops during rainy seasons"
      ],
      "treatment": [
        "Remove severely infected plants from field",
        "Apply recommended bactericide if necessary",
        "Maintain balanced nutrient management",
        "Reduce standing water in affected areas"
      ]
    }
  }
}

SEVERITY = {
    "Healthy": "healthy",
    "Early Blight": "med",        "Late Blight": "high",
    "Brown Rust": "med",          "Yellow Rust": "high",
    "Brown Spot": "med",          "Bacterial Leaf Blight": "high",
}


# ============================================================
#   IRRIGATION MODULE
# ============================================================
def irrigation_recommendation(crop_type, rainfall, temperature, soil_type):
    crop_type = crop_type.lower()
    soil_type = soil_type.lower()
    recs = []

    if rainfall > 120:
        recs.append("Heavy rainfall detected — reduce irrigation to prevent waterlogging.")
    elif rainfall >= 60:
        recs.append("Average/Moderate rainfall available — maintain balanced irrigation schedule.")
    else:
        recs.append("☀️ Low rainfall detected — additional irrigation is necessary.")

    if temperature > 38:
        recs.append("🌡 Very high temperature — irrigate frequently to counter rapid evaporation.")
    elif temperature >= 25:
        recs.append("🌡 Temperature is normal — good conditions for healthy crop growth.")
    else:
        recs.append("🌡 Low temperature reduces evaporation — reduce irrigation frequency.")

    soil_advice = {
        "sandy":    "🪨 Sandy soil loses water quickly — light irrigation every 2 days recommended.",
        "clay":     "🪨 Clay soil retains water — less frequent irrigation needed.",
        "loamy":    "🪨 Loamy soil has balanced moisture — maintain regular irrigation schedule.",
        "red":      "🪨 Red soil dries quickly — moderate and regular irrigation required.",
        "black":    "🪨 Black soil retains moisture efficiently — avoid excessive irrigation.",
        "alluvial": "🪨 Alluvial soil supports good water retention and fertility.",
    }
    recs.append(soil_advice.get(soil_type, "🪨 Unknown soil type — monitor soil moisture manually."))

    crop_advice = {
        "tomato": "🍅 Tomato needs moderate consistent irrigation, especially during fruit development.",
        "potato": "🥔 Potato requires uniform soil moisture for healthy tuber formation.",
        "wheat":  "🌿 Wheat needs moderate irrigation during early growth stages.",
        "rice":   "🌾 Rice requires high water availability and performs well in flooded conditions.",
    }
    recs.append(crop_advice.get(crop_type, "🌱 Crop-specific irrigation data unavailable."))

    if rainfall < 50 and temperature > 35 and soil_type == "sandy":
        final = "⚠️ FINAL DECISION: Irrigate frequently — hot weather + low rainfall + sandy soil cause rapid moisture loss."
    elif rainfall > 120 and soil_type == "clay":
        final = "✅ FINAL DECISION: Avoid extra irrigation — heavy rainfall + clay soil risk waterlogging."
    elif soil_type == "loamy":
        final = "✅ FINAL DECISION: Irrigate every 3 days to maintain balanced soil moisture."
    else:
        final = "✅ FINAL DECISION: Monitor field moisture regularly and irrigate based on crop conditions."
    recs.append(final)

    return recs


# ============================================================
#   WEATHER API
# ============================================================
def get_weather(location: str):
    if OWM_API_KEY == "YOUR_OPENWEATHERMAP_API_KEY":
        return None
    try:
        url = (f"https://api.openweathermap.org/data/2.5/weather"
               f"?q={location}&appid={OWM_API_KEY}&units=metric")
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            d = r.json()
            return {
                "temp":     round(d["main"]["temp"], 1),
                "humidity": d["main"]["humidity"],
                "desc":     d["weather"][0]["description"],
                "icon":     d["weather"][0]["main"],
                "wind":     d["wind"]["speed"],
                "rain":     d.get("rain", {}).get("1h", 0),
                "city":     d["name"],
            }
    except Exception:
        pass
    return None

def weather_disease_risk(weather, crop):
    if not weather:
        return []
    temp, hum, rain = weather["temp"], weather["humidity"], weather.get("rain", 0)
    risks = []
    if crop == "Rice":
        if hum > 80 and temp > 25:
            risks.append(("high", "High risk of Bacterial Leaf Blight — hot & humid conditions detected."))
        if hum > 75:
            risks.append(("med",  "Moderate risk of Brown Spot — maintain good field drainage."))
    elif crop == "Tomato":
        if temp < 20 and rain > 0:
            risks.append(("high", "High risk of Late Blight — cool & wet conditions detected."))
        if hum > 75 and temp > 22:
            risks.append(("med",  "Moderate risk of Early Blight — warm & humid weather."))
    elif crop == "Potato":
        if temp < 20 and hum > 80:
            risks.append(("high", "High risk of Late Blight — cool & wet conditions."))
        if hum > 70:
            risks.append(("med",  "Watch for Early Blight — current humidity levels are elevated."))
    elif crop == "Wheat":
        if temp > 15 and hum > 70:
            risks.append(("high", "High risk of Brown Rust — warm & moist conditions."))
        if temp < 15 and hum > 80:
            risks.append(("high", "High risk of Yellow Rust — cool & wet conditions."))
    if not risks:
        risks.append(("low", "No significant disease risk from current weather conditions."))
    return risks


# ============================================================
#   NOTIFICATION ENGINE
# ============================================================
def generate_weather_notifications(weather, crop, location):
    if not weather:
        return []

    notifications = []
    temp  = weather["temp"]
    hum   = weather["humidity"]
    rain  = weather.get("rain", 0)
    wind  = weather.get("wind", 0)
    desc  = weather.get("desc", "")
    now   = datetime.now().strftime("%H:%M")

    if crop == "Rice":
        if hum > 80 and temp > 25:
            notifications.append({
                "type": "critical", "icon": "🔴",
                "title": "Bacterial Leaf Blight Risk",
                "message": f"Hot ({temp}°C) and humid ({hum}%) conditions in {location} — ideal for Bacterial Leaf Blight spread. Inspect rice leaves immediately.",
                "action": "Go to Disease Detection", "time": now,
            })
        if hum > 75:
            notifications.append({
                "type": "warning", "icon": "🟡",
                "title": "Brown Spot Risk",
                "message": f"Humidity at {hum}% — conditions favour Brown Spot in rice. Ensure proper field drainage.",
                "action": "Check Irrigation", "time": now,
            })
    elif crop == "Tomato":
        if temp < 20 and rain > 0:
            notifications.append({
                "type": "critical", "icon": "🔴",
                "title": "Late Blight Alert",
                "message": f"Cool ({temp}°C) and wet conditions — high Late Blight risk for tomato. Apply fungicide immediately.",
                "action": "Go to Disease Detection", "time": now,
            })
        if hum > 75 and temp > 22:
            notifications.append({
                "type": "warning", "icon": "🟡",
                "title": "Early Blight Risk",
                "message": f"Warm and humid weather ({hum}% humidity) — watch for Early Blight on tomato leaves.",
                "action": "Scan Your Crop", "time": now,
            })
    elif crop == "Potato":
        if temp < 20 and hum > 80:
            notifications.append({
                "type": "critical", "icon": "🔴",
                "title": "Late Blight Alert",
                "message": f"Cool ({temp}°C) and highly humid ({hum}%) — severe Late Blight risk for potato. Act immediately.",
                "action": "Go to Disease Detection", "time": now,
            })
        if hum > 70:
            notifications.append({
                "type": "warning", "icon": "🟡",
                "title": "Early Blight Watch",
                "message": f"Elevated humidity ({hum}%) — monitor potato plants for Early Blight symptoms.",
                "action": "Scan Your Crop", "time": now,
            })
    elif crop == "Wheat":
        if temp > 15 and hum > 70:
            notifications.append({
                "type": "critical", "icon": "🔴",
                "title": "Brown Rust Alert",
                "message": f"Warm ({temp}°C) and moist ({hum}%) — high Brown Rust risk for wheat. Apply fungicide spray.",
                "action": "Go to Disease Detection", "time": now,
            })
        if temp < 15 and hum > 80:
            notifications.append({
                "type": "critical", "icon": "🔴",
                "title": "Yellow Rust Alert",
                "message": f"Cool ({temp}°C) and wet ({hum}%) — Yellow Rust conditions detected. Monitor fields closely.",
                "action": "Scan Your Crop", "time": now,
            })

    if rain > 10:
        notifications.append({
            "type": "info", "icon": "🌧",
            "title": "Skip Irrigation Today",
            "message": f"Rainfall of {rain}mm detected in {location}. No additional irrigation needed today — save water.",
            "action": "View Irrigation Advisor", "time": now,
        })
    elif rain == 0 and temp > 35:
        notifications.append({
            "type": "warning", "icon": "🟠",
            "title": "Irrigate Urgently",
            "message": f"No rainfall and high temperature ({temp}°C) in {location}. Crops may be under heat stress — irrigate now.",
            "action": "View Irrigation Advisor", "time": now,
        })

    if wind > 7:
        notifications.append({
            "type": "info", "icon": "🌬️",
            "title": "Avoid Spraying Today",
            "message": f"Wind speed is {wind} m/s — too high for pesticide or fungicide spraying. Wait for calmer conditions.",
            "action": None, "time": now,
        })

    if temp > 38:
        notifications.append({
            "type": "warning", "icon": "☀️",
            "title": "Heat Stress Warning",
            "message": f"Extreme temperature of {temp}°C detected. {crop} crops may suffer heat stress — increase irrigation frequency.",
            "action": "View Irrigation Advisor", "time": now,
        })

    frost_thresh = {"Rice": 10, "Tomato": 8, "Potato": 5, "Wheat": 3}
    if temp < frost_thresh.get(crop, 5):
        notifications.append({
            "type": "critical", "icon": "❄️",
            "title": "Frost Risk Warning",
            "message": f"Temperature dropped to {temp}°C — frost risk for {crop}. Cover crops or apply protective measures immediately.",
            "action": None, "time": now,
        })

    if not notifications:
        notifications.append({
            "type": "good", "icon": "✅",
            "title": "Ideal Growing Conditions",
            "message": f"Weather in {location} is looking good for {crop} — {desc}, {temp}°C, {hum}% humidity. Keep up your routine care.",
            "action": None, "time": now,
        })

    return notifications

def get_notification_count(notifications):
    return len([n for n in notifications if n["type"] in ("critical","warning")])


# ============================================================
#   INIT SESSION STATE
# ============================================================
if "farmer_data" not in st.session_state:
    st.session_state.farmer_data = None


# ============================================================
#   SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 🌿 AgroScan")
    st.markdown("---")

    nav = None
    if st.session_state.farmer_data:
        f = st.session_state.farmer_data
        st.markdown(f"### 👤 {f['username']}")
        st.markdown(f"**ID:** `{f['farmer_id']}`")
        st.markdown(f"📍 {f['location']}")
        st.markdown(f"🌱 **Current Crop:** {CROP_EMOJI.get(f['main_crop'],'')} {f['main_crop']} · {f['farm_size']} acres")

        st.markdown("**Switch Crop:**")
        crops_list = ["Rice", "Tomato", "Potato", "Wheat"]
        current_index = crops_list.index(f["main_crop"]) if f["main_crop"] in crops_list else 0
        new_crop = st.selectbox(
            "Select crop", crops_list, index=current_index,
            format_func=lambda c: f"{CROP_EMOJI.get(c,'')} {c}",
            label_visibility="collapsed", key="crop_switcher"
        )
        if new_crop != f["main_crop"]:
            if st.button(f"✅ Switch to {CROP_EMOJI.get(new_crop,'')} {new_crop}", use_container_width=True):
                update_farmer_crop(new_crop)
                st.success(f"Switched to {new_crop}!")
                st.rerun()

        st.markdown("---")

        _w      = get_weather(f["location"])
        _notifs = generate_weather_notifications(_w, f["main_crop"], f["location"]) if _w else []
        _n_count= get_notification_count(_notifs)

        if _n_count > 0:
            st.markdown(f"""
            <div style='background:#FFEBEE;border-radius:10px;padding:12px 14px;
                        margin-bottom:4px;border:1.5px solid #C62828;border-left:5px solid #C62828;'>
              <div class="sidebar-alert-crit" style='font-size:17px;font-weight:700;'>
                🔔 {_n_count} Active Alert{'s' if _n_count>1 else ''}
              </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔔 Tap Notifications to view", key="sidebar_notif_btn", use_container_width=True):
                st.session_state["nav_override"] = "🔔 Notifications"
                st.rerun()
        else:
            st.markdown("""
            <div style='background:#1B5E20;border-radius:10px;padding:10px 14px;
                        margin-bottom:12px;border:1.5px solid #4CAF50;border-left:5px solid #4CAF50;'>
              <div class="sidebar-alert-good" style='font-size:17px;font-weight:800;'>✅ No active alerts</div>
            </div>
            """, unsafe_allow_html=True)

        nav = st.radio(
            "Navigation",
            ["🏠 Dashboard", "🔬 Disease Detection", "🌧 Irrigation Advisor",
             "🔔 Notifications", "🤖 Agro Chatbot", "📋 Scan History",
             "💧 Irrigation History", "👨‍🌾 My Profile"],
            label_visibility="collapsed"
        )
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.farmer_data = None
            for key in ["scan_history","irr_history","chat_history","selected_crop","nav_override"]:
                st.session_state.pop(key, None)
            st.rerun()
    else:
        st.markdown("#### Register or Login")
        st.markdown("Create your farm profile to start scanning crops.")

    st.markdown("---")
    st.markdown("<p style='font-size:13px;color:rgba(255,255,255,0.5);font-weight:600;'>AgroScan v1.0 · AI Crop Health</p>", unsafe_allow_html=True)


# ============================================================
#   REGISTER / LOGIN PAGE
# ============================================================
if not st.session_state.farmer_data:
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("""
        <div style='text-align:center; padding:32px 0 28px'>
          <div style='font-size:60px'>🌿</div>
          <div style='font-family:Syne,sans-serif; font-size:36px; font-weight:800; color:#110A05; margin-top:8px'>AgroScan</div>
          <div style='font-size:18px; color:#4A3A2A; margin-top:6px; font-weight:600;'>AI-Powered Crop Disease Detection</div>
        </div>
        """, unsafe_allow_html=True)

        tab_reg, tab_login = st.tabs(["📝 New Farmer", "🔑 Existing Farmer"])

        with tab_reg:
            with st.form("register_form"):
                st.markdown("#### Create your farm profile")
                username  = st.text_input("Full Name", placeholder="e.g. Rajan Pillai")
                password  = st.text_input("Password", type="password", placeholder="Create a password")
                password2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
                location  = st.text_input("Village / Town", placeholder="e.g. Thrissur, Kerala")
                farm_size = st.number_input("Farm Size (acres)", min_value=0.1, step=0.5, value=2.0)
                main_crop = st.selectbox("Primary Crop", ["Rice", "Tomato", "Potato", "Wheat"])
                submitted = st.form_submit_button("Register & Continue →", use_container_width=True)
                if submitted:
                    if not username.strip() or not location.strip():
                        st.error("Please fill in all fields.")
                    elif not password.strip():
                        st.error("Please set a password.")
                    elif password != password2:
                        st.error("Passwords do not match.")
                    else:
                        farmer, err = register_farmer(
                            username.strip(), location.strip(),
                            farm_size, main_crop, password
                        )
                        if err:
                            st.error(err)
                        else:
                            st.session_state.farmer_data = farmer
                            load_farmer_history()
                            st.success(f"✅ Welcome, {username}! Your ID: {farmer['farmer_id']}")
                            st.rerun()

        with tab_login:
            with st.form("login_form"):
                st.markdown("#### Login to your account")
                l_username = st.text_input("Username", placeholder="Enter your name")
                l_password = st.text_input("Password", type="password", placeholder="Enter your password")
                login_btn  = st.form_submit_button("Login →", use_container_width=True)
                if login_btn:
                    if not l_username.strip() or not l_password.strip():
                        st.error("Please enter username and password.")
                    else:
                        farmer, err = login_farmer(l_username.strip(), l_password)
                        if err:
                            st.error(err)
                        else:
                            st.session_state.farmer_data = farmer
                            load_farmer_history()
                            st.success(f"✅ Welcome back, {farmer['username']}!")
                            st.rerun()
    st.stop()


if not st.session_state.farmer_data:
    st.rerun()

f = st.session_state.get("farmer_data", None)
if f is None:
    st.warning("Session expired. Please login again.")
    st.session_state.farmer_data = None
    st.rerun()

crop = f["main_crop"]

if "scan_history" not in st.session_state or "irr_history" not in st.session_state:
    load_farmer_history()

# ── Nav override from sidebar alert button and notification action buttons ──
if "nav_override" in st.session_state:
    nav = st.session_state.pop("nav_override")


# ============================================================
#   DASHBOARD
# ============================================================
if nav == "🏠 Dashboard":
    _dw = get_weather(f["location"])
    _dn = generate_weather_notifications(_dw, crop, f["location"]) if _dw else []
    _critical = [n for n in _dn if n["type"] == "critical"]
    if _critical:
        for alert in _critical:
            st.markdown(f"""
            <div style='background:#FFEBEE;border-radius:14px;padding:16px 20px;
                        margin-bottom:14px;border:2px solid #C62828;border-left:8px solid #C62828;
                        display:flex;align-items:center;gap:14px;box-shadow:0 4px 12px rgba(198,40,40,0.12);'>
              <div style='font-size:36px'>{alert['icon']}</div>
              <div>
                <div style='font-family:Syne,sans-serif;font-size:18px;font-weight:800;color:#C62828'>{alert['title']}</div>
                <div style='font-size:16px;color:#110A05;margin-top:4px;font-weight:600;line-height:1.5;'>{alert['message']}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='padding:16px 0 20px'>
      <div style='font-size:15px; color:#4A3A2A; text-transform:uppercase; letter-spacing:.08em; font-weight:700;'>Welcome back,</div>
      <div style='font-family:Syne,sans-serif; font-size:34px; font-weight:800; color:#110A05; margin-top:2px'>
        {f['username']} {CROP_EMOJI.get(crop,'')}
      </div>
      <div style='font-size:17px; color:#110A05; margin-top:4px; font-weight:600;'>
        {f['farmer_id']} · {f['location']} · {f['farm_size']} acres · {crop}
      </div>
    </div>
    """, unsafe_allow_html=True)

    scan_hist = st.session_state.get("scan_history", [])
    irr_hist  = st.session_state.get("irr_history", [])
    diseases  = [h for h in scan_hist if h["prediction_result"] != "Healthy"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
          <div class="mc-label">Total Scans</div>
          <div class="mc-value">{len(scan_hist)}</div>
          <div class="mc-sub">Disease scans</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
          <div class="mc-label">Diseases Found</div>
          <div class="mc-value" style="color:#C62828">{len(diseases)}</div>
          <div class="mc-sub" style="color:#C62828">Detected</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
          <div class="mc-label">Healthy Scans</div>
          <div class="mc-value" style="color:#2E7D32">{len(scan_hist) - len(diseases)}</div>
          <div class="mc-sub" style="color:#2E7D32">No disease</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
          <div class="mc-label">Irrigation Logs</div>
          <div class="mc-value" style="color:#1565C0">{len(irr_hist)}</div>
          <div class="mc-sub" style="color:#1565C0">Recommendations</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col_w, col_h = st.columns([1.3, 1])

    with col_w:
        st.markdown('<div class="section-head">🌤 Live Weather & Disease Alerts</div>', unsafe_allow_html=True)
        weather = get_weather(f["location"])
        if weather:
            w_icon = {"Rain":"🌧","Clouds":"☁️","Clear":"☀️","Thunderstorm":"⛈️","Drizzle":"🌦️","Mist":"🌫️"}.get(weather["icon"], "🌡️")
            st.markdown(f"""
            <div class="weather-card">
              <div class="wc-city">📍 {weather['city']}</div>
              <div style="display:flex; align-items:center; gap:18px; margin-bottom:8px">
                <div style="font-size:58px; filter: drop-shadow(0px 2px 6px rgba(0,0,0,0.25));">{w_icon}</div>
                <div>
                  <div class="wc-temp">{weather['temp']}°C</div>
                  <div class="wc-desc">{weather['desc']}</div>
                </div>
              </div>
              <div class="wc-stats">
                <span>💧 {weather['humidity']}% humidity</span>
                <span>💨 {weather['wind']} m/s wind</span>
                <span>🌧 {weather['rain']} mm rain</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<b style='font-size:17px; color:#110A05; display:block; margin-bottom:6px;'>🔍 Weather-based Disease Risk:</b>", unsafe_allow_html=True)
            risks = weather_disease_risk(weather, crop)
            for level, msg in risks:
                cls  = {"high":"risk-high","med":"risk-med","low":"risk-low"}.get(level,"risk-low")
                icon = {"high":"🔴","med":"🟡","low":"🟢"}.get(level,"🟢")
                st.markdown(f'<div class="risk-badge {cls}">{icon} {msg}</div>', unsafe_allow_html=True)
        else:
            st.info("🌤 Weather data unavailable. Please check your internet connection or city name.")

    with col_h:
        st.markdown('<div class="section-head">📜 Recent Scans</div>', unsafe_allow_html=True)
        if scan_hist:
            for h in scan_hist[:5]:
                color = "#C62828" if h["prediction_result"] != "Healthy" else "#2E7D32"
                emoji = CROP_EMOJI.get(h["crop_type"], "🌱")
                conf  = f"{h['confidence']:.0f}%" if h.get("confidence") else ""
                st.markdown(f"""
                <div class="scan-item" style="border-left: 5px solid {color}">
                  <div class="si-title">{emoji} {h['crop_type']} — {h['prediction_result']} {conf}</div>
                  <div class="si-date">{h['scan_date'][:16]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No scans yet. Go to 🔬 Disease Detection to start!")


# ============================================================
#   DISEASE DETECTION
# ============================================================
elif nav == "🔬 Disease Detection":
    st.markdown('<div class="section-head">🔬 Disease Detection</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:16px; font-weight:700; color:#110A05;
                text-transform:uppercase; letter-spacing:.07em; margin-bottom:12px'>
        🌱 Select crop to scan
    </div>
    """, unsafe_allow_html=True)

    crops_list = ["Rice", "Tomato", "Potato", "Wheat"]
    if "selected_crop" not in st.session_state:
        st.session_state.selected_crop = f["main_crop"]

    c1, c2, c3, c4 = st.columns(4)
    for col, c in zip([c1, c2, c3, c4], crops_list):
        is_active = st.session_state.selected_crop == c
        with col:
            if is_active:
                st.markdown(f"""
                <div style='background:#2D6A2D; border-radius:14px; padding:16px 12px;
                            text-align:center; border:2px solid #2D6A2D; cursor:pointer;
                            box-shadow:0 4px 12px rgba(45,106,45,0.3)'>
                  <div style='font-size:32px'>{CROP_EMOJI.get(c,'')}</div>
                  <div style='font-size:17px; font-weight:700; color:#ffffff; margin-top:4px'>{c}</div>
                  <div style='font-size:13px; color:rgba(255,255,255,0.85); margin-top:2px'>✓ Active</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background:#ffffff; border-radius:14px; padding:16px 12px;
                            text-align:center; border:2px solid #C8BFAF; cursor:pointer'>
                  <div style='font-size:32px'>{CROP_EMOJI.get(c,'')}</div>
                  <div style='font-size:17px; font-weight:700; color:#110A05; margin-top:4px'>{c}</div>
                  <div style='font-size:13px; color:#5A4A3A; margin-top:2px'>Tap to select</div>
                </div>
                """, unsafe_allow_html=True)
            if st.button(f"Select {c}", key=f"cropsel_{c}", use_container_width=True, help=f"Switch to {c} model"):
                st.session_state.selected_crop = c
                st.rerun()

    crop = st.session_state.selected_crop

    col_up, col_res = st.columns([1, 1.3], gap="large")

    with col_up:
        st.markdown("#### 📷 Upload Leaf Image")
        uploaded   = st.file_uploader("Choose a leaf photo", type=["jpg","jpeg","png"])
        st.markdown("**— or take a photo —**")
        camera_img = st.camera_input("Open camera")
        st.markdown("---")
        scan_btn = st.button("🔍 Detect Disease", use_container_width=True)

    with col_res:
        img_source = uploaded if uploaded else camera_img
        if img_source:
            img_pil = Image.open(img_source)
            st.image(img_pil, caption="Leaf image", width=600)

        if scan_btn:
            if not img_source:
                st.warning("Please upload or take a photo first.")
            else:
                with st.spinner(f"Running {crop} disease model…"):
                    model = load_model(crop)
                    if model:
                        label, conf, probs = predict(model, img_pil, crop)
                        add_scan_record(crop, label, conf)

                        sev      = SEVERITY.get(label, "med")
                        sev_icon = {"high":"🔴","med":"🟡","healthy":"🟢"}.get(sev,"🟡")

                        st.markdown(f"""
                        <div class="disease-banner {sev}">
                          <h2>{sev_icon} {label}</h2>
                          <p>Detected in <b>{crop}</b> leaf sample · Confidence: <b>{conf:.1f}%</b></p>
                        </div>
                        """, unsafe_allow_html=True)

                        bar_color = "#C62828" if sev=="high" else "#E65100" if sev=="med" else "#2E7D32"
                        st.markdown(f"""
                        <div style='margin-bottom:16px'>
                          <div style='display:flex; justify-content:space-between; font-size:15px; color:#110A05; margin-bottom:5px; font-weight:600;'>
                            <span>Model confidence</span>
                            <span style='font-weight:700; color:{bar_color}'>{conf:.1f}%</span>
                          </div>
                          <div class='conf-wrap'>
                            <div class='conf-fill' style='width:{conf}%; background:{bar_color}'></div>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown("<b style='color:#110A05; font-size:16px; display:block; margin-bottom:8px;'>All class probabilities:</b>", unsafe_allow_html=True)
                        for i, lbl in enumerate(CLASS_LABELS[crop]):
                            pct = float(probs[i]) * 100
                            col = "#2E7D32" if "Healthy" in lbl else "#C62828"
                            st.markdown(f"""
                            <div style='display:flex; align-items:center; gap:10px; margin-bottom:8px'>
                              <span style='min-width:180px; font-size:15px; color:#110A05; font-weight:600;'>{lbl}</span>
                              <div class='conf-wrap' style='flex:1'>
                                <div class='conf-fill' style='width:{pct}%; background:{col}'></div>
                              </div>
                              <span style='min-width:50px; text-align:right; font-size:15px; font-weight:700; color:{col}'>{pct:.1f}%</span>
                            </div>
                            """, unsafe_allow_html=True)

                        st.markdown("---")
                        info = DISEASE_DB.get(crop, {}).get(label, {})
                        if label == "Healthy":
                            st.markdown(f"""
                            <div class="healthy-box">
                              <h4>✅ {info.get('status', 'Plant is healthy.')}</h4>
                              <ul>{''.join(f"<li>{t}</li>" for t in info.get('maintenance_tips', []))}</ul>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            t1, t2, t3 = st.tabs(["🦠 Causes", "💊 Treatment", "🛡 Prevention"])
                            with t1:
                                st.markdown(f"""<div class="info-box">
                                  <h4>🦠 Root Causes of {label}</h4>
                                  <ul>{''.join(f"<li>{c}</li>" for c in info.get('causes',[]))}</ul>
                                </div>""", unsafe_allow_html=True)
                            with t2:
                                st.markdown(f"""<div class="info-box">
                                  <h4>💊 Treatment Plan</h4>
                                  <ul>{''.join(f"<li>{t}</li>" for t in info.get('treatment',[]))}</ul>
                                </div>""", unsafe_allow_html=True)
                            with t3:
                                st.markdown(f"""<div class="info-box">
                                  <h4>🛡 Prevention Tips</h4>
                                  <ul>{''.join(f"<li>{p}</li>" for p in info.get('prevention',[]))}</ul>
                                </div>""", unsafe_allow_html=True)

                        st.success("✅ Scan result saved to your history!")


# ============================================================
#   IRRIGATION ADVISOR
# ============================================================
elif nav == "🌧 Irrigation Advisor":
    st.markdown(f'<div class="section-head">🌧 Automated Live Irrigation Advisor — {CROP_EMOJI.get(crop,"")} {crop}</div>', unsafe_allow_html=True)

    weather = get_weather(f["location"])
    if weather:
        temperature = weather["temp"]
        rainfall    = weather.get("rain", 0)
        soil_type   = "Loamy"

        recs = irrigation_recommendation(crop, rainfall, temperature, soil_type)
        add_irrigation_record(crop, rainfall, temperature, soil_type, recs)

        st.markdown("""
        <div style='background:#0D47A1; border-radius:12px; padding:16px 20px; margin-bottom:22px; border:1.5px solid #1565C0'>
          <span style='font-size:17px; color:#ffffff; font-weight:600'>
            ✅ Live Automation Active! Field metrics have been automatically synced using real-time local weather feeds for <b>{}</b>. No manual adjustments required.
          </span>
        </div>
        """.format(f['location']), unsafe_allow_html=True)

        col_in, col_out = st.columns([1, 1.2], gap="large")

        with col_in:
            st.markdown("#### ⚙️ Synced Field Environmental Metrics")
            st.markdown("""
            <div style='background:#ffffff; border-radius:14px; padding:22px 24px; margin-bottom:16px;
                        border:1.5px solid #C8BFAF; box-shadow:0 4px 12px rgba(0,0,0,0.05)'>
              <div style='font-size:14px; color:#4A3A2A; text-transform:uppercase; letter-spacing:.06em; margin-bottom:14px; font-weight:700;'>Real-time Metrics</div>
              <div style='display:flex; flex-direction:column; gap:14px'>
                <div style='display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #EDE8DF; padding-bottom:8px;'>
                  <span style='font-size:16px; color:#4A3A2A; font-weight:600;'>📍 Location</span>
                  <b style='font-size:17px; color:#110A05'>{}</b>
                </div>
                <div style='display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #EDE8DF; padding-bottom:8px;'>
                  <span style='font-size:16px; color:#1565C0; font-weight:600;'>🌧 Live Rainfall</span>
                  <b style='font-size:18px; color:#1565C0'>{} mm</b>
                </div>
                <div style='display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #EDE8DF; padding-bottom:8px;'>
                  <span style='font-size:16px; color:#E65100; font-weight:600;'>🌡️ Live Temperature</span>
                  <b style='font-size:18px; color:#E65100'>{}°C</b>
                </div>
                <div style='display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #EDE8DF; padding-bottom:8px;'>
                  <span style='font-size:16px; color:#5D4037; font-weight:600;'>🪨 Soil Context</span>
                  <b style='font-size:18px; color:#5D4037'>{} Context</b>
                </div>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                  <span style='font-size:16px; color:#2E7D32; font-weight:600;'>🌱 Target Crop</span>
                  <b style='font-size:18px; color:#2E7D32'>{}</b>
                </div>
              </div>
            </div>
            """.format(f['location'], rainfall, temperature, soil_type, crop), unsafe_allow_html=True)

        with col_out:
            st.markdown("#### 💧 Smart Irrigation Advisories")
            for rec in recs[:-1]:
                st.markdown("""
                <div class="irr-card">
                  <p style='margin:0; font-weight:500;'>{}</p>
                </div>
                """.format(rec), unsafe_allow_html=True)

            final = recs[-1]
            final_bg = "#C62828" if "frequently" in final.lower() or "warning" in final.lower() else "#1B5E20"
            
            st.markdown(f"""
            <div style="background:{final_bg}; border-radius:14px; padding:20px 22px; border:2px solid #4CAF50; margin-top:8px">
              <div style="font-family:Syne,sans-serif; font-size:17px; font-weight:800; color:#ffffff; margin-bottom:6px">
                Final Decision
              </div>
              <p style="font-size:16px; color:#ffffff; margin:0; font-weight:600;">{final}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#FFF3E0; border-radius:14px; padding:32px; border:1.5px solid #FFCC80; text-align:center'>
          <div style='font-size:44px; margin-bottom:12px'>🌤</div>
          <div style='font-family:Syne,sans-serif; font-size:18px; font-weight:700; color:#E65100'>Weather Connection Offline</div>
          <div style='font-size:16px; color:#4A3A2A; margin-top:8px; font-weight:600;'>Unable to automate irrigation parameters. Please ensure your OpenWeatherMap API Key is configured properly inside app.py.</div>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
#   SCAN HISTORY
# ============================================================
elif nav == "📋 Scan History":
    st.markdown('<div class="section-head">📋 Disease Scan History</div>', unsafe_allow_html=True)
    history = st.session_state.get("scan_history", [])
    if not history:
        st.info("No disease scans yet. Go to 🔬 Disease Detection to start!")
    else:
        import pandas as pd
        df = pd.DataFrame(history)
        df = df[["crop_type","prediction_result","confidence","scan_date"]]
        df.columns = ["Crop","Result","Confidence (%)","Date"]
        df["Confidence (%)"] = df["Confidence (%)"].apply(lambda x: f"{x:.1f}%" if x else "—")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown(f"**Total scans:** {len(history)}  |  **Diseases detected:** {len([h for h in history if h['prediction_result'] != 'Healthy'])}")


# ============================================================
#   IRRIGATION HISTORY
# ============================================================
elif nav == "💧 Irrigation History":
    st.markdown('<div class="section-head">💧 Irrigation Recommendation History</div>', unsafe_allow_html=True)
    irr_hist = st.session_state.get("irr_history", [])
    if not irr_hist:
        st.info("No irrigation recommendations yet. Go to 🌧 Irrigation Advisor to get started!")
    else:
        for log in irr_hist:
            # Fixed the f-string syntax error here by removing the brackets around the rain emoji
            with st.expander(f"📅 {log['log_date']}  |  {log['crop_type']}  |  🌧 {log['rainfall']}mm  |  🌡 {log['temperature']}°C  |  Soil: {log['soil_type']}"):
                for line in log["recommendation"].split("\n"):
                    if line.strip():
                        st.markdown(f"- {line}")


# ============================================================
#   MY PROFILE
# ============================================================
elif nav == "👨‍🌾 My Profile":
    st.markdown('<div class="section-head">👨‍🌾 My Profile</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:#fff;border-radius:16px;padding:24px;border:1.5px solid #C8BFAF'>
      <div style='font-size:32px;margin-bottom:12px'>👤</div>
      <div style='font-family:Syne,sans-serif;font-size:22px;font-weight:700;color:#110A05'>{f['username']}</div>
      <div style='margin-top:14px;display:flex;flex-direction:column;gap:10px'>
        <div style='font-size:17px;color:#110A05;font-weight:500;'>📍 Location: <b>{f['location']}</b></div>
        <div style='font-size:17px;color:#110A05;font-weight:500;'>🌾 Farm size: <b>{f['farm_size']} acres</b></div>
        <div style='font-size:17px;color:#110A05;font-weight:500;'>{CROP_EMOJI.get(f['main_crop'],'')} Crop: <b>{f['main_crop']}</b></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
#   NOTIFICATIONS PAGE
# ============================================================
elif nav == "🔔 Notifications":
    st.markdown('<div class="section-head">🔔 Weather Notifications & Alerts</div>', unsafe_allow_html=True)

    weather = get_weather(f["location"])

    if not weather:
        st.markdown("""
        <div style='background:#FFF3E0;border-radius:14px;padding:24px;
                    border:1.5px solid #FFCC80;text-align:center'>
          <div style='font-size:40px;margin-bottom:12px'>🌤</div>
          <div style='font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#E65100'>
            Weather API Not Connected
          </div>
          <div style='font-size:16px;color:#4A3A2A;margin-top:8px;font-weight:600;'>
            Add your OpenWeatherMap API key in app.py to enable smart weather alerts.
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        notifications = generate_weather_notifications(weather, crop, f["location"])
        critical = [n for n in notifications if n["type"] == "critical"]
        warnings = [n for n in notifications if n["type"] == "warning"]
        info     = [n for n in notifications if n["type"] == "info"]
        good     = [n for n in notifications if n["type"] == "good"]

        w_icon = {"Rain":"🌧","Clouds":"☁️","Clear":"☀️","Thunderstorm":"⛈️","Drizzle":"🌦️","Mist":"🌫️"}.get(weather["icon"],"🌡️")
        
        st.markdown(f"""
        <div class='weather-card' style='margin-bottom:24px'>
          <div class='wc-city'>📍 {weather['city']} · Updated at {datetime.now().strftime('%H:%M')}</div>
          <div style='display:flex;align-items:center;gap:16px;margin-bottom:8px'>
            <div style='font-size:52px'>{w_icon}</div>
            <div>
              <div class='wc-temp'>{weather['temp']}°C</div>
              <div class='wc-desc'>{weather['desc']}</div>
            </div>
          </div>
          <div class='wc-stats'>
            <span>💧 {weather['humidity']}% humidity</span>
            <span>💨 {weather['wind']} m/s wind</span>
            <span>🌧 {weather['rain']} mm rain</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class='metric-card'>
              <div class='mc-label'>Critical</div>
              <div class='mc-value' style='color:#C62828'>{len(critical)}</div>
              <div class='mc-sub' style='color:#B71C1C;font-weight:700;'>Immediate action</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class='metric-card'>
              <div class='mc-label'>Warnings</div>
              <div class='mc-value' style='color:#E65100'>{len(warnings)}</div>
              <div class='mc-sub' style='color:#E65100;font-weight:700;'>Watch closely</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class='metric-card'>
              <div class='mc-label'>Info</div>
              <div class='mc-value' style='color:#1565C0'>{len(info)}</div>
              <div class='mc-sub' style='color:#1565C0;font-weight:700;'>Advisory</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class='metric-card'>
              <div class='mc-label'>Crop</div>
              <div class='mc-value' style='font-size:26px'>{CROP_EMOJI.get(crop,'')}</div>
              <div class='mc-sub' style='color:#110A05;font-weight:700;'>{crop}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")

        TYPE_STYLE = {
            "critical": ("border:2px solid #C62828; border-left:8px solid #C62828; background:#FFEBEE; box-shadow:0 4px 12px rgba(198,40,40,0.15);", "#C62828", "#110A05"),
            "warning":  ("border:2px solid #E65100; border-left:8px solid #E65100; background:#FFF3E0; box-shadow:0 4px 12px rgba(230,81,0,0.15);",  "#E65100", "#110A05"),
            "info":      ("border:2px solid #1565C0; border-left:8px solid #1565C0; background:#E3F2FD; box-shadow:0 4px 12px rgba(21,101,192,0.15);",  "#1565C0", "#110A05"),
            "good":      ("border:2px solid #2E7D32; border-left:8px solid #2E7D32; background:#1B5E20; box-shadow:0 4px 12px rgba(46,125,50,0.15);",   "#ffffff", "#ffffff"),
        }

        ACTION_MAP = {
            "Go to Disease Detection": "🔬 Disease Detection",
            "Scan Your Crop":          "🔬 Disease Detection",
            "Check Irrigation":        "🌧 Irrigation Advisor",
            "View Irrigation Advisor": "🌧 Irrigation Advisor",
        }

        if notifications:
            for idx, n in enumerate(notifications):
                style, color, msg_color = TYPE_STYLE.get(n["type"], TYPE_STYLE["info"])
                st.markdown(f"""
                <div style='{style} border-radius:16px; padding:20px 24px; margin-bottom:4px;'>
                  <div style='display:flex;align-items:flex-start;gap:16px'>
                    <div style='font-size:38px;margin-top:2px'>{n['icon']}</div>
                    <div style='flex:1'>
                      <div style='display:flex;justify-content:space-between;align-items:center'>
                        <div style='font-family:Syne,sans-serif;font-size:18px;
                                    font-weight:800;color:{color}'>{n['title']}</div>
                        <div style='font-size:14px;color:{msg_color};font-weight:600'>🕐 {n['time']}</div>
                      </div>
                      <div style='font-size:17px;color:{msg_color};margin-top:8px;line-height:1.6;font-weight:500'>
                        {n['message']}
                      </div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                if n.get("action"):
                    if st.button(f"→ {n['action']}", key=f"notif_action_{idx}", use_container_width=False):
                        target = ACTION_MAP.get(n["action"], "🏠 Dashboard")
                        st.session_state["nav_override"] = target
                        st.rerun()

                st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 Refresh Weather Alerts", use_container_width=True):
        st.rerun()


# ============================================================
#   AGRO CHATBOT PAGE
# ============================================================
elif nav == "🤖 Agro Chatbot":

    # ── Import new chatbot engine ──
    try:
        sys.path.insert(0, os.path.join(BASE_DIR, "chatbot"))
        from response_generator import generate_chatbot_response as _new_chatbot
        USE_NEW_CHATBOT = True
    except Exception:
        USE_NEW_CHATBOT = False

    # ── Format reply ──
    def _format_chatbot_reply(raw):
        if isinstance(raw, str):
            return raw
        if isinstance(raw, dict):
            reply = raw.get("reply", "")
            if isinstance(reply, dict):
                parts = []
                if "causes"     in reply: parts.append("**Causes:**\n"     + "\n".join(f"• {c}" for c in reply["causes"]))
                if "prevention" in reply: parts.append("**Prevention:**\n" + "\n".join(f"• {p}" for p in reply["prevention"]))
                if "treatment"  in reply: parts.append("**Treatment:**\n"  + "\n".join(f"• {t}" for t in reply["treatment"]))
                return "\n\n".join(parts)
            if isinstance(reply, list):
                return "\n".join(f"• {item}" for item in reply)
            return str(reply)
        return str(raw)

    # ── Render bot text into HTML ──
    def _render_bot_text(text):
        lines = text.split("\n")
        html  = []
        in_list = False
        for line in lines:
            if line.startswith("• ") or line.startswith("- "):
                if not in_list:
                    html.append("<ul style='margin:8px 0 8px 2px;padding-left:18px;'>")
                    in_list = True
                html.append(f"<li style='font-size:15px;font-weight:500;color:#110A05;margin-bottom:5px;line-height:1.6;'>{line[2:]}</li>")
            else:
                if in_list:
                    html.append("</ul>")
                    in_list = False
                if line.strip().endswith(":") and len(line.strip()) < 40:
                    html.append(f"<div style='font-family:Syne,sans-serif;font-size:15px;font-weight:800;color:#1B5E20;margin:12px 0 4px;border-left:3px solid #4CAF50;padding-left:8px;'>{line.strip()}</div>")
                elif line.startswith("**") and line.endswith("**"):
                    html.append(f"<div style='font-weight:800;font-size:15px;color:#1B5E20;margin:10px 0 4px;'>{line[2:-2]}</div>")
                elif line.strip() == "":
                    html.append("<div style='height:6px'></div>")
                else:
                    html.append(f"<div style='font-size:15px;font-weight:500;color:#110A05;line-height:1.7;'>{line}</div>")
        if in_list:
            html.append("</ul>")
        return "".join(html)

    # ── Detect message type from content ──
    def _detect_type(text):
        t = text.lower()
        if any(w in t for w in ["symptom","identify","sign","leaf spot"]): return "symptoms"
        if any(w in t for w in ["cause","reason","why","spread"]):         return "causes"
        if any(w in t for w in ["treatment","cure","fungicide","spray"]):  return "treatment"
        if any(w in t for w in ["prevent","protection","avoid"]):          return "prevention"
        if any(w in t for w in ["irrigat","water","rainfall","drip"]):     return "irrigation"
        if any(w in t for w in ["fertiliz","npk","nutrient","manure"]):    return "fertilizer"
        if any(w in t for w in ["weather","climate","temperature","humid"]): return "weather"
        if any(w in t for w in ["harvest","maturity","ready"]):            return "harvest"
        if any(w in t for w in ["hello","hi","hey","i am agroscan"]):      return "greeting"
        return "response"

    TYPE_META = {
        "greeting":   ("👋", "#4CAF50",  "#E8F5E9"),
        "symptoms":   ("🔍", "#7B1FA2",  "#F3E5F5"),
        "causes":     ("⚠️",  "#E65100",  "#FFF3E0"),
        "treatment":  ("💊", "#1565C0",  "#E3F2FD"),
        "prevention": ("🛡️",  "#2E7D32",  "#E8F5E9"),
        "irrigation": ("💧", "#0277BD",  "#E1F5FE"),
        "fertilizer": ("🌱", "#5D4037",  "#EFEBE9"),
        "weather":    ("🌤️",  "#00838F",  "#E0F7FA"),
        "harvest":    ("🌾", "#F57F17",  "#FFF8E1"),
        "response":   ("🌿", "#2D6A2D",  "#F1F8E9"),
    }

    # ── Init chat history ──
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.chat_history.append({
            "role": "bot",
            "text": f"🌱 Hello {f['username']}! I am AgroScan Agricultural Assistant.\n\nI can help you with:\n\n- Crop Diseases\n- Disease Symptoms\n- Disease Treatment\n- Irrigation Guidance\n- Weather Conditions\n- Crop Management\n\nSupported Crops:\n\n- Wheat\n- Rice\n- Potato\n- Tomato",
            "type": "greeting"
        })

    # ── HEADER ──
    st.markdown(f"""
    <div style='background:#1B5E20; border-radius:20px; padding:20px 26px;
                margin-bottom:20px; display:flex; align-items:center; gap:16px;
                border:1.5px solid #4CAF50; box-shadow:0 4px 16px rgba(27,94,32,0.25);'>
      <div style='width:52px;height:52px;border-radius:50%;
                  background:rgba(255,255,255,0.15);
                  display:flex;align-items:center;justify-content:center;font-size:26px;'>
        🌿
      </div>
      <div style='flex:1'>
        <div style='font-family:Syne,sans-serif;font-size:20px;font-weight:800;color:#ffffff;'>
          AgroScan Agricultural Assistant
        </div>
        <div style='font-size:14px;color:rgba(255,255,255,0.75);margin-top:3px;font-weight:500;'>
          Diseases · Irrigation · Fertilizer · Weather · Harvest · Soil
        </div>
      </div>
      <div style='display:flex;align-items:center;gap:6px;
                  background:rgba(255,255,255,0.12);
                  border-radius:20px;padding:6px 14px;'>
        <div style='width:8px;height:8px;border-radius:50%;background:#A5D6A7;'></div>
        <span style='font-size:13px;font-weight:700;color:#ffffff;'>Online</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── QUICK SUGGESTIONS ──
    st.markdown("""
    <div style='font-size:13px;font-weight:800;color:#4A3A2A;
                text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px;'>
       💬 Quick Questions
    </div>
    """, unsafe_allow_html=True)

    suggestions = [
        ("🌾", "Rice"),
        ("🌿", "Wheat"),
        ("🍅", "Tomato"),
        ("🥔", "Potato"),
    ]
    sug_cols = st.columns(4)
    for i, (icon, sug) in enumerate(suggestions):
        with sug_cols[i]:
            if st.button(f"{icon} {sug}", key=f"sug_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role":"user","text":sug})
                if USE_NEW_CHATBOT:
                    raw = _new_chatbot(sug)
                else:
                    raw = chatbot_response(sug)
                reply = _format_chatbot_reply(raw)
                st.session_state.chat_history.append({
                    "role":"bot","text":reply,
                    "type":_detect_type(reply)
                })
                st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── CONVERSATION LABEL ──
    st.markdown("""
    <div style='font-size:13px;font-weight:800;color:#4A3A2A;
                text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px;'>
        🗨️ Conversation
    </div>
    """, unsafe_allow_html=True)

    # ── CHAT MESSAGES ──
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style='display:flex;justify-content:flex-end;margin-bottom:16px;'>
              <div style='display:flex;align-items:flex-end;gap:8px;max-width:75%;'>
                <div style='background:#1B5E20;color:#ffffff;
                            border-radius:20px 20px 4px 20px;
                            padding:12px 18px;font-size:15px;
                            font-weight:500;line-height:1.6;
                            box-shadow:0 2px 10px rgba(27,94,32,0.25);'>
                  {msg['text']}
                </div>
                <div style='width:32px;height:32px;border-radius:50%;
                            background:#2D6A2D;flex-shrink:0;
                            display:flex;align-items:center;
                            justify-content:center;font-size:14px;
                            box-shadow:0 2px 6px rgba(0,0,0,0.15);'>
                  👤
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            msg_type = msg.get("type","response")
            icon, accent, bg = TYPE_META.get(msg_type, TYPE_META["response"])
            body = _render_bot_text(msg["text"])
            st.markdown(f"""
            <div style='display:flex;align-items:flex-start;gap:10px;margin-bottom:16px;'>
              <div style='width:36px;height:36px;border-radius:50%;
                          background:{accent};flex-shrink:0;
                          display:flex;align-items:center;
                          justify-content:center;font-size:17px;
                          box-shadow:0 2px 8px rgba(0,0,0,0.15);
                          margin-top:2px;'>
                {icon}
              </div>
              <div style='background:#ffffff;border-radius:4px 20px 20px 20px;
                          padding:16px 20px;max-width:82%;
                          border:1.5px solid #E8E2D8;
                          border-left:4px solid {accent};
                          box-shadow:0 2px 10px rgba(0,0,0,0.06);'>
                {body}
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    with st.form(key="chatbot_input_form", clear_on_submit=True):
        col_input, col_send = st.columns([5, 1])
        with col_input:
            user_input = st.text_input(
                "Message",
                placeholder="e.g. What causes rice brown spot? or Potato late blight treatment",
                label_visibility="collapsed"
            )
        with col_send:
            send_btn = st.form_submit_button("Send 📨", use_container_width=True)

        if send_btn and user_input.strip():
            msg_text = user_input.strip()
            st.session_state.chat_history.append({"role": "user", "text": msg_text})
            
            if USE_NEW_CHATBOT:
                raw = _new_chatbot(msg_text)
            else:
                raw = chatbot_response(msg_text)
                
            reply = _format_chatbot_reply(raw)
            st.session_state.chat_history.append({
                "role": "bot",
                "text": reply,
                "type": _detect_type(reply)
            })
            st.rerun()

    col_clr, col_sp = st.columns([1, 4])
    with col_clr:
        if st.session_state.chat_history:
            if st.button("🗑 Clear", key="clear_chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

    st.markdown("---")

    # ── CAPABILITIES GRID ──
    st.markdown("""
    <div style='font-size:13px;font-weight:800;color:#4A3A2A;
                text-transform:uppercase;letter-spacing:.08em;margin-bottom:14px;'>
        🌱 What I Can Help With
    </div>
    """, unsafe_allow_html=True)

    capabilities = [
        ("🦠", "#C62828", "Disease Info",    "Symptoms, causes, treatment & prevention"),
        ("💧", "#0277BD", "Irrigation",      "Water requirements & irrigation methods"),
        ("🌱", "#5D4037", "Fertilizer",      "NPK & nutrient recommendations per crop"),
        ("🌤", "#00838F", "Weather",         "Best climate & temperature conditions"),
        ("🌾", "#F57F17", "Harvest Tips",    "When and how to harvest each crop"),
        ("🌍", "#2E7D32", "Soil & Farming",  "Soil types and cultivation guidance"),
    ]
    cap_cols = st.columns(3)
    for i, (icon, color, title, desc) in enumerate(capabilities):
        with cap_cols[i % 3]:
            st.markdown(f"""
            <div style='background:#ffffff;border-radius:14px;padding:18px 16px;
                        border:1.5px solid #E8E2D8;margin-bottom:10px;
                        border-top:4px solid {color};
                        box-shadow:0 2px 8px rgba(0,0,0,0.05);'>
              <div style='font-size:28px;margin-bottom:8px;'>{icon}</div>
              <div style='font-size:15px;font-weight:800;color:#110A05;margin-bottom:4px;'>{title}</div>
              <div style='font-size:13px;color:#6A5A4A;line-height:1.5;font-weight:500;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)