import mysql.connector
import streamlit as st
import random
from faker import Faker
from datetime import datetime, timedelta
import pandas as pd
import base64

# Initialize Faker and session state
fake = Faker()
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "soil_management",
    "port": 3306
}

# Helper Functions
def add_bg_from_url():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?ixlib=rb-4.0.3");
            background-attachment: fixed;
            background-size: cover;
        }}
        /* Custom CSS */
        .stTextInput, .stNumberInput, .stDateInput, .stSelectbox {{
            background-color: rgba(46, 46, 46, 0.7) !important;
            border-radius: 10px !important;
            padding: 10px !important;
            border: 1px solid #4CAF50 !important;
        }}
        .stButton>button {{
            background-color: #4CAF50 !important;
            color: white !important;
            border-radius: 10px !important;
            padding: 10px 20px !important;
            border: none !important;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2) !important;
            transition: 0.3s ease !important;
        }}
        .stButton>button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0px 6px 15px rgba(0, 0, 0, 0.3) !important;
        }}
        .element-container {{
            background-color: rgba(27, 27, 27, 0.7) !important;
            border-radius: 10px !important;
            padding: 20px !important;
            margin: 10px 0 !important;
        }}
        .css-1d391kg {{
            background-color: rgba(46, 46, 46, 0.7) !important;
        }}
        .recommendation-block {{
            background-color: rgba(46, 46, 46, 0.8) !important;
            border-radius: 10px !important;
            padding: 20px !important;
            margin: 20px auto !important;  /* Changed: added auto for horizontal centering */
            max-width: 90% !important;     /* Added: maximum width */
            text-align: center !important;
            border: 1px solid #4CAF50 !important;
            display: flex !important;       /* Added: flexbox */
            flex-direction: column !important;
            align-items: center !important; /* Added: center items */
        }}
        
        .recommendation-item {{
            color: white !important;
            margin: 10px 0 !important;
            padding: 5px !important;
            width: 100% !important;         /* Added: full width */
            text-align: center !important;  /* Added: ensure text centering */
            display: block !important;      /* Added: block display */
        }}

        .recommendations-header {{
            color: white !important;
            text-align: center !important;
            margin-bottom: 20px !important;
            text-shadow: 2px 2px 4px #000000 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def add_message(message, msg_type="success"):
    st.session_state['messages'] = [(msg_type, message)]

def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        error_message = f"Error connecting to database: {e}"
        add_message(error_message, "error")
        return None

def get_soil_recommendations(nitrogen, phosphorus, potassium, pH, moisture):
    recommendations = []
    
    # Nitrogen recommendations
    if nitrogen < 1.0:
        recommendations.append("Nitrogen: Low levels detected. Consider adding nitrogen-rich fertilizers or planting legumes.")
    elif nitrogen > 4.0:
        recommendations.append("Nitrogen: High levels detected. Reduce nitrogen fertilization.")
        
    # Phosphorus recommendations
    if phosphorus < 1.0:
        recommendations.append("Phosphorus: Low levels detected. Apply phosphate fertilizers or organic matter.")
    elif phosphorus > 4.0:
        recommendations.append("Phosphorus: High levels detected. Avoid phosphorus-rich fertilizers.")
        
    # pH recommendations
    if pH < 6.0:
        recommendations.append("pH Level: Acidic soil detected. Consider adding lime to raise pH.")
    elif pH > 7.5:
        recommendations.append("pH Level: Alkaline soil detected. Consider adding sulfur to lower pH.")
        
    # Moisture recommendations
    if moisture < 20:
        recommendations.append("Moisture: Low content detected. Improve irrigation and add organic matter.")
    elif moisture > 40:
        recommendations.append("Moisture: High content detected. Improve drainage system.")
        
    return recommendations

def insert_manual_record(farm_location, test_date, nitrogen, phosphorus, potassium, pH, moisture):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()

        if not farm_location:
            warning_message = "Farm Location field must be filled!"
            add_message(warning_message, "warning")
            return

        try:
            cursor.execute("""
                INSERT INTO soil_health (farm_location, test_date, nitrogen_level, phosphorus_level, potassium_level, pH_level, moisture_content)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (farm_location, test_date, nitrogen, phosphorus, potassium, pH, moisture))
            conn.commit()
            conn.close()
            success_message = "Soil record inserted successfully!"
            add_message(success_message, "success")
        except mysql.connector.Error as e:
            error_message = f"Error inserting record: {e}"
            add_message(error_message, "error")

def generate_soil_data():
    farm_location = fake.city()
    test_date = fake.date_between(start_date="-2y", end_date="today")
    nitrogen = round(random.uniform(0.1, 5.0), 2)
    phosphorus = round(random.uniform(0.1, 5.0), 2)
    potassium = round(random.uniform(0.1, 5.0), 2)
    pH = round(random.uniform(4.5, 8.5), 2)
    moisture = round(random.uniform(5.0, 50.0), 2)
    return (farm_location, test_date, nitrogen, phosphorus, potassium, pH, moisture)

def insert_bulk_records(total_records, batch_size):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        for i in range(0, total_records, batch_size):
            data_batch = [generate_soil_data() for _ in range(batch_size)]
            cursor.executemany("""
                INSERT INTO soil_health (farm_location, test_date, nitrogen_level, phosphorus_level, potassium_level, pH_level, moisture_content)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, data_batch)
            conn.commit()

        success_message = f"{total_records} records inserted successfully!"
        add_message(success_message, "success")
        conn.close()
        st.rerun()

def display_records(limit=None):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        query = "SELECT * FROM soil_health ORDER BY record_no DESC"
        if limit:
            query += f" LIMIT {limit}"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        df = pd.DataFrame(rows, columns=["Record No", "Farm Location", "Test Date", "Nitrogen Level", "Phosphorus Level", "Potassium Level", "pH Level", "Moisture Content"])
        st.dataframe(df, height=564, use_container_width=True)

def main():
    st.set_page_config(layout="wide", page_title="Smart Soil Management System")
    add_bg_from_url()

    st.markdown("""
        <h1 style='text-align: center; color: white; text-shadow: 2px 2px 4px #000000;'>
            Smart Soil Management System
        </h1>
        """, unsafe_allow_html=True)

    # Database initialization
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS soil_health (
                    record_no INT AUTO_INCREMENT PRIMARY KEY,
                    farm_location VARCHAR(255) NOT NULL,
                    test_date DATE,
                    nitrogen_level FLOAT,
                    phosphorus_level FLOAT,
                    potassium_level FLOAT,
                    pH_level FLOAT,
                    moisture_content FLOAT
                );
            """)
            conn.commit()
        except mysql.connector.Error as err:
            add_message(f"Error creating table: {err}", "error")
        finally:
            cursor.close()
            conn.close()

    # Layout
    col1, col2 = st.columns([1, 2])

    # Input column
    with col1:
        st.header("Input Data")
        farm_location = st.text_input("Farm Location")
        col11, col12 = st.columns([1, 1])
        
        with col11:
            test_date = st.date_input("Test Date")
            phosphorus = st.number_input("Phosphorus Level (mg/kg)", format="%.4f")
            pH = st.number_input("pH Level", format="%.4f")
        
        with col12:
            nitrogen = st.number_input("Nitrogen Level (mg/kg)", format="%.4f")
            potassium = st.number_input("Potassium Level (mg/kg)", format="%.4f")
            moisture = st.number_input("Moisture Content (%)", format="%.4f")

        if st.button("Insert Record"):
            insert_manual_record(farm_location, test_date, nitrogen, phosphorus, potassium, pH, moisture)
            
            # Show recommendations after successful insert
            if st.session_state['messages'] and st.session_state['messages'][0][0] == "success":
                st.markdown("<h3 class='recommendations-header'>Soil Analysis Recommendations</h3>", unsafe_allow_html=True)
                recommendations = get_soil_recommendations(nitrogen, phosphorus, potassium, pH, moisture)
                if recommendations:
                    recommendations_html = "<div class='recommendation-block'>"
                    for rec in recommendations:
                        recommendations_html += f"<div class='recommendation-item'>🌱&nbsp;&nbsp;{rec}</div>"
                    recommendations_html += "</div>"
                    st.markdown(recommendations_html, unsafe_allow_html=True)

        # Messages section
        st.markdown("---")
        st.subheader("Messages")
        if st.session_state['messages']:
            msg_type, msg = st.session_state['messages'][0]
            if msg_type == "success":
                st.success(msg)
            elif msg_type == "error":
                st.error(msg)
            elif msg_type == "warning":
                st.warning(msg)
            else:
                st.info(msg)

    # Display column
    with col2:
        col21, col22, col23, col24 = st.columns([3, 1, 1, 0.7])
        
        with col22:
            limit = st.selectbox("Select Limit for Table", 
                               ["Don't Limit", "Limit to 10 rows", "Limit to 50 rows", 
                                "Limit to 100 rows", "Limit to 200 rows", "Limit to 300 rows", 
                                "Limit to 500 rows"], index=3)
            limit_value = None if limit == "Don't Limit" else int(limit.split()[2])

        with col21:
            st.header(f"{'Last ' + str(limit_value) if limit_value else 'All'} Records")

        with col23:
            bulk_quantity = st.selectbox("Select Bulk Quantity", 
                                       [10, 50, 100, 500, 1000, 10000, 100000])

        with col24:
            if st.button("Insert Bulk Records"):
                batch_size = min(bulk_quantity, 10000)
                insert_bulk_records(bulk_quantity, batch_size)

        display_records(limit=limit_value)

if __name__ == "__main__":
    main()
