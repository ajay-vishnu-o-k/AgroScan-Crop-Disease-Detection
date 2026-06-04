# Crop Advisor — Capstone Project

This repository contains a Streamlit-based Crop Advisor app for disease detection, irrigation recommendations, and crop suggestions using trained ML models and a simple chatbot.

## Project structure

- `app.py` — main Streamlit app
- `database.py` — data persistence (if used)
- `irrigation.py` — irrigation recommendation logic
- `*.h5`, `*.keras` — trained model files (potato, rice, tomato, wheat)
- `farmers.json`, `recommendation.json` — sample data/config
- `chatbot/` — chatbot components (intent classification, response generation, fuzzy matching, context memory)

## Requirements

- Python 3.8+
- Recommended packages: `streamlit`, `tensorflow`/`keras`, `numpy`, `pandas`, `scikit-learn`

You can create a virtual environment and install packages with:

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install --upgrade pip
pip install streamlit tensorflow numpy pandas scikit-learn
```

## Run the app

Start the Streamlit app from the project root:

```bash
streamlit run app.py
```

## Models

- `potato_model.h5`, `rice_model.h5`, `tomato_model.h5`, `wheat_disease_finetuned_model.keras` — placed in repository root. The app loads these for predictions.

## Chatbot

The `chatbot/` folder contains components used to power a conversational assistant:

- `intent_classifier.py`, `response_generator.py`, `entity_extractor.py`, `fuzzy_engine.py`, `synonym_matcher.py`, `context_memory.py`, `agriculture_filter.py`

## Data

- `chatbot/data/` — supporting data modules such as `disease_data.py` and `irrigation_data.py`.

## Notes

- If the app raises errors loading models, ensure TensorFlow/Keras versions are compatible with the saved model formats.
- If you'd like, I can add a `requirements.txt` or a quick health-check script to validate model loading.

## Contact

For follow-up changes or to add CI/tests, open an issue or ask me to implement them.
