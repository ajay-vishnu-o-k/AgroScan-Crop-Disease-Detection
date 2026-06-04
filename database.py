import sqlite3

# =========================================================
# CONNECT DATABASE
# =========================================================

connection = sqlite3.connect("database.db")

cursor = connection.cursor()

# =========================================================
# CREATE FARMERS TABLE
# =========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS farmers (

    farmer_id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT NOT NULL,

    location TEXT NOT NULL,

    farm_size TEXT NOT NULL,

    main_crop TEXT NOT NULL

)
""")

# =========================================================
# CREATE PREDICTION HISTORY TABLE
# =========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS prediction_history (

    record_id INTEGER PRIMARY KEY AUTOINCREMENT,

    farmer_id INTEGER NOT NULL,

    crop_type TEXT NOT NULL,

    prediction_result TEXT NOT NULL,

    irrigation_recommendation TEXT NOT NULL,

    FOREIGN KEY (farmer_id)
    REFERENCES farmers(farmer_id)

)
""")

# =========================================================
# SAVE TABLE CREATION
# =========================================================

connection.commit()

# =========================================================
# INSERT FARMER FUNCTION
# =========================================================

def insert_farmer(
    username,
    location,
    farm_size,
    main_crop
):

    cursor.execute("""
    INSERT INTO farmers (

        username,
        location,
        farm_size,
        main_crop

    )

    VALUES (?, ?, ?, ?)
    """, (

        username,
        location,
        farm_size,
        main_crop

    ))

    connection.commit()

    print("\nFarmer profile created successfully.")

# =========================================================
# INSERT PREDICTION HISTORY FUNCTION
# =========================================================

def insert_prediction_history(
    farmer_id,
    crop_type,
    prediction_result,
    irrigation_recommendation
):

    cursor.execute("""
    INSERT INTO prediction_history (

        farmer_id,
        crop_type,
        prediction_result,
        irrigation_recommendation

    )

    VALUES (?, ?, ?, ?)
    """, (

        farmer_id,
        crop_type,
        prediction_result,
        irrigation_recommendation

    ))

    connection.commit()

    print("\nPrediction history saved successfully.")

# =========================================================
# DISPLAY FARMERS
# =========================================================

def display_farmers():

    cursor.execute("SELECT * FROM farmers")

    farmers = cursor.fetchall()

    print("\n" + "=" * 70)
    print("FARMERS TABLE")
    print("=" * 70)

    for farmer in farmers:
        print(farmer)

# =========================================================
# DISPLAY PREDICTION HISTORY
# =========================================================

def display_prediction_history():

    cursor.execute("SELECT * FROM prediction_history")

    records = cursor.fetchall()

    print("\n" + "=" * 70)
    print("PREDICTION HISTORY TABLE")
    print("=" * 70)

    for record in records:
        print(record)

# =========================================================
# CLOSE DATABASE
# =========================================================

def close_connection():
    connection.close()