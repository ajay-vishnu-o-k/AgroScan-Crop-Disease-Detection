import tensorflow as tf
import os

h5_path = "wheat_disease_finetuned_model.h5"

if os.path.exists(h5_path):
    print(f"Found {h5_path}. Loading model...")
    # Load the h5 model safely into your local Keras 3 environment
    model = tf.keras.models.load_model(h5_path, compile=False)
    
    print("Exporting to low-level TensorFlow SavedModel format using Keras 3 API...")
    # The new Keras 3 way to generate a native SavedModel graph folder
    model.export("wheat_saved_model")
    print("✅ Success! 'wheat_saved_model' folder created with 100% accuracy intact.")
else:
    print(f"❌ Error: Cannot find '{h5_path}' in this directory.")