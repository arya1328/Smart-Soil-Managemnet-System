# Smart-Soil-Managemnet-System
This system aims to collect and analyze soil data to provide recommendations for best farming practices.
Overview

The Smart Soil Management System is a web-based application built with Streamlit and MySQL to manage soil health data. This system allows users to manually input soil test data, store it in a database, and receive recommendations based on soil nutrient levels. Additionally, bulk data can be generated and inserted into the database for analysis.

Features

1.Manual Entry of Soil Data: Users can enter soil health parameters such as nitrogen, phosphorus, potassium, pH, and moisture levels.  
2. Automated Recommendations: Based on input values, the system provides recommendations for improving soil health.  
3. Bulk Data Generation & Insertion: Automatically generates random soil data and inserts it into the database.  
4. Database Integration: Stores data in a MySQL database and retrieves records for display.  
5. Stylized UI with Streamlit: Includes a responsive UI with a background image and custom styling.  

Tech Stack

Frontend: Streamlit (Python)

Backend: Python

Database: MySQL

Libraries Used:

mysql.connector (for database connection)

streamlit (for UI development)

faker (for random data generation)

pandas (for data manipulation)

random (for generating random values)

datetime (for handling date inputs)
