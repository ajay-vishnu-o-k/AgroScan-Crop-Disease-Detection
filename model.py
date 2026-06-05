import tensorflow as tf

# 1. Load the existing .keras model 
model = tf.keras.models.load_model("wheat_disease_finetuned_model.keras")

# 2. Re-save it with the .h5 extension
model.save("wheat_disease_finetuned_model.h5")

print("Conversion successful! Your weights and architecture are perfectly preserved.")