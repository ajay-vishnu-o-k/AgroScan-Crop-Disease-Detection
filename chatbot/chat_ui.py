
# =========================================================
# AgroScan Chatbot UI
# =========================================================

import streamlit as st

from response_generator import generate_chatbot_response

from context_memory import chat_memory


# =========================================================
# Page Config
# =========================================================

st.set_page_config(

    page_title="AgroScan Chatbot",

    page_icon="🌱",

    layout="wide"
)


# =========================================================
# PROFESSIONAL COLOR THEME
# =========================================================

st.markdown("""

<style>

/* =====================================================
MAIN APP
===================================================== */

.stApp {

    background-color: #E8F1E5;

    color: #1B1B1B;
}


/* =====================================================
TITLE
===================================================== */

.chat-title {

    font-size: 42px;

    font-weight: bold;

    color: #2E7D32;

    text-align: center;

    margin-bottom: 8px;
}

.chat-subtitle {

    text-align: center;

    color: #4E4E4E;

    font-size: 18px;

    margin-bottom: 30px;
}


/* =====================================================
USER MESSAGE
===================================================== */

.user-message {

    background-color: #D9FDD3;

    color: #000000;

    padding: 15px;

    border-radius: 15px;

    margin-bottom: 15px;

    margin-left: 25%;

    font-size: 16px;

    line-height: 1.7;

    box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
}


/* =====================================================
BOT MESSAGE
===================================================== */

.bot-message {

    background-color: #FFFFFF;

    color: #1B1B1B;

    padding: 18px;

    border-radius: 15px;

    margin-bottom: 20px;

    margin-right: 20%;

    font-size: 16px;

    line-height: 1.8;

    border-left: 5px solid #2E7D32;

    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}


/* =====================================================
SIDEBAR
===================================================== */

section[data-testid="stSidebar"] {

    background-color: #DDEAD7;
}


/* =====================================================
SIDEBAR TEXT
===================================================== */

section[data-testid="stSidebar"] * {

    color: #1B1B1B !important;
}


/* =====================================================
CHAT INPUT BOX
===================================================== */

.stChatInputContainer {

    background-color: white;

    border-radius: 12px;

    border: 2px solid #388E3C;

    padding: 6px;
}


/* =====================================================
TEXT INPUT
===================================================== */

textarea {

    color: #000000 !important;

    font-size: 16px !important;
}


/* =====================================================
BUTTONS
===================================================== */

.stButton button {

    background-color: #2E7D32;

    color: white;

    border-radius: 10px;

    border: none;

    padding: 10px 18px;

    font-size: 15px;

    font-weight: 600;
}

.stButton button:hover {

    background-color: #1B5E20;

    color: white;
}


/* =====================================================
WELCOME MESSAGE AREA
===================================================== */

.welcome-card {

    background-color: #FFFFFF;

    padding: 25px;

    border-radius: 15px;

    border: 1px solid #DADADA;

    margin-bottom: 20px;

    color: #1B1B1B;

    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}


/* =====================================================
MARKDOWN FIX
===================================================== */

.markdown-text-container {

    color: #1B1B1B !important;
}


/* =====================================================
TEXT FIX
===================================================== */

.bot-message p,
.user-message p {

    color: inherit !important;
}


/* =====================================================
SCROLLBAR
===================================================== */

::-webkit-scrollbar {

    width: 8px;
}

::-webkit-scrollbar-thumb {

    background: #A5D6A7;

    border-radius: 10px;
}


/* =====================================================
REMOVE TOP SPACE
===================================================== */

.block-container {

    padding-top: 2rem;
}

</style>

""", unsafe_allow_html=True)


# =========================================================
# Title
# =========================================================

st.markdown(

    "<div class='chat-title'>🌱 AgroScan AI Assistant</div>",

    unsafe_allow_html=True
)

st.markdown(

    "<div class='chat-subtitle'>Smart Agricultural Chatbot for Crop Disease & Irrigation Guidance</div>",

    unsafe_allow_html=True
)


# =========================================================
# Initialize Chat History
# =========================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# =========================================================
# Welcome Message
# =========================================================

if len(st.session_state.messages) == 0:

    welcome_message = (

        "👋 Welcome to AgroScan AI Assistant!\n\n"

        "I can help you with:\n\n"

        "🌾 Wheat Diseases\n"
        "🌾 Rice Diseases\n"
        "🥔 Potato Diseases\n"
        "🍅 Tomato Diseases\n"
        "💧 Irrigation Guidance\n"
        "🌦 Weather Conditions\n"
        "🌱 Soil Information\n\n"

        "Try asking:\n\n"

        "• Potato late blight treatment\n"
        "• Symptoms of yellow rust\n"
        "• Irrigation for rice\n"
        "• Best soil for tomato\n"
        "• Causes of bacterial leaf blight"
    )

    st.session_state.messages.append({

        "role": "assistant",

        "content": welcome_message
    })


# =========================================================
# Display Messages
# =========================================================


# =========================================================
# Display Messages
# =========================================================

for message in st.session_state.messages:

    # Convert line breaks properly
    formatted_message = message["content"].replace(
        "\n",
        "<br>"
    )

    # -----------------------------------------------------
    # USER MESSAGE
    # -----------------------------------------------------

    if message["role"] == "user":

        st.markdown(

            f"""
            <div style="
                background-color: #D9FDD3;
                color: #000000;
                padding: 15px;
                border-radius: 15px;
                margin-bottom: 15px;
                margin-left: 25%;
                font-size: 16px;
                line-height: 1.7;
                box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
            ">

            <b>👨 User</b><br><br>

            {formatted_message}

            </div>
            """,

            unsafe_allow_html=True
        )

    # -----------------------------------------------------
    # BOT MESSAGE
    # -----------------------------------------------------

    else:

        st.markdown(

            f"""
            <div style="
                background-color: #FFFFFF;
                color: #1B1B1B;
                padding: 18px;
                border-radius: 15px;
                margin-bottom: 20px;
                margin-right: 20%;
                font-size: 16px;
                line-height: 1.8;
                border-left: 5px solid #2E7D32;
                box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
            ">

            <b>🤖 AgroScan Assistant</b><br><br>

            {formatted_message}

            </div>
            """,

            unsafe_allow_html=True
        )


# =========================================================
# Chat Input
# =========================================================

user_input = st.chat_input(

    "Ask your agriculture question..."
)


# =========================================================
# Process User Input
# =========================================================

if user_input:

    # -----------------------------------------------------
    # Save User Message
    # -----------------------------------------------------

    st.session_state.messages.append({

        "role": "user",

        "content": user_input
    })

    # -----------------------------------------------------
    # Generate Response
    # -----------------------------------------------------

    with st.spinner("AgroScan is analyzing..."):

        bot_response = generate_chatbot_response(
            user_input
        )

    # -----------------------------------------------------
    # Save Bot Response
    # -----------------------------------------------------

    st.session_state.messages.append({

        "role": "assistant",

        "content": bot_response
    })

    # -----------------------------------------------------
    # Refresh UI
    # -----------------------------------------------------

    st.rerun()


# =========================================================
# Sidebar
# =========================================================

with st.sidebar:

    st.title("🌱 AgroScan")

    st.markdown("---")

    st.subheader("Supported Crops")

    st.markdown("""

    🌾 Wheat  
    🌾 Rice  
    🥔 Potato  
    🍅 Tomato

    """)

    st.markdown("---")

    st.subheader("Supported Features")

    st.markdown("""

    ✅ Disease Detection  
    ✅ Symptoms Analysis  
    ✅ Treatment Guidance  
    ✅ Prevention Advice  
    ✅ Irrigation Guidance  
    ✅ Soil Information  
    ✅ Weather Information  
    ✅ Smart Typo Correction  
    ✅ Context Memory

    """)

    st.markdown("---")

    # -----------------------------------------------------
    # Clear Chat Button
    # -----------------------------------------------------

    if st.button("🗑 Clear Chat"):

        st.session_state.messages = []

        chat_memory.clear_memory()

        st.rerun()

    st.markdown("---")

    st.caption("AgroScan AI Agricultural Assistant")
