import pandas as pd
import pyodbc
from dotenv import load_dotenv
import os
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Connect to Azure SQL
conn = pyodbc.connect(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={os.getenv('SQL_SERVER')};"
    f"DATABASE={os.getenv('SQL_DATABASE')};"
    f"UID={os.getenv('SQL_USERNAME')};"
    f"PWD={os.getenv('SQL_PASSWORD')}"
)
conn.autocommit = False
cursor = conn.cursor()
cursor.fast_executemany = True

print("✅ Connected to Azure SQL database.")

try:
    # -------------------- FLIGHT DATA --------------------
    print("🚀 Reading and preparing flight data...")
    df = pd.read_csv("data/T_ONTIME_REPORTING.csv")
    df = df[df["ORIGIN"] == "ATL"]
    df["FL_DATE"] = pd.to_datetime(df["FL_DATE"], format="%m/%d/%Y %I:%M:%S %p", errors='coerce').dt.date
    df = df.where(pd.notnull(df), None)

    # Use tqdm for progress monitoring
    print("📦 Transforming flight rows...")
    flight_rows = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="⏳ Preparing Flights"):
        flight_rows.append(tuple(None if pd.isna(v) else v for v in [
            row["YEAR"], row["MONTH"], row["DAY_OF_MONTH"], row["DAY_OF_WEEK"], row["FL_DATE"],
            row["OP_UNIQUE_CARRIER"], row["OP_CARRIER_FL_NUM"], row["ORIGIN"], row["DEST"],
            row["CRS_DEP_TIME"], row["DEP_TIME"], row["DEP_DELAY"],
            row["CRS_ARR_TIME"], row["ARR_TIME"], row["ARR_DELAY"],
            row["CANCELLED"], row["CANCELLATION_CODE"], row["DIVERTED"], row["DISTANCE"],
            row["CARRIER_DELAY"], row["WEATHER_DELAY"], row["NAS_DELAY"],
            row["SECURITY_DELAY"], row["LATE_AIRCRAFT_DELAY"]
        ]))

    print("📝 Inserting flight data (batch)...")
    cursor.executemany("""
        INSERT INTO flights_raw (
            year, month, day_of_month, day_of_week, flight_date,
            carrier_code, flight_number, origin, destination,
            scheduled_dep_time, actual_dep_time, dep_delay,
            scheduled_arr_time, actual_arr_time, arr_delay,
            cancelled, cancellation_code, diverted, distance,
            carrier_delay, weather_delay, nas_delay, security_delay, late_aircraft_delay
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, flight_rows)
    print("✅ Flight data inserted successfully.")

    # -------------------- WEATHER DATA --------------------
    print("🌦️ Reading and preparing weather data...")
    weather_df = pd.read_csv("data/weather_atl_march2025.csv")
    weather_df["date"] = pd.to_datetime(weather_df["date"], errors='coerce')
    weather_df = weather_df.where(pd.notnull(weather_df), None)

    print("📦 Transforming weather rows...")
    weather_rows = []
    for _, row in tqdm(weather_df.iterrows(), total=len(weather_df), desc="⏳ Preparing Weather"):
        weather_rows.append((
            row["station"], row["date"], row["temp_c"], row["wind_speed_kph"],
            row["visibility_km"], row["weather_code"]
        ))

    print("📝 Inserting weather data (batch)...")
    cursor.executemany("""
        INSERT INTO weather_raw (
            station, date, temp_c, wind_speed_kph, visibility_km, weather_code
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, weather_rows)
    print("✅ Weather data inserted successfully.")

    conn.commit()

except Exception as e:
    conn.rollback()
    print("🚨 Error occurred:", e)
    print("🔁 Rolled back all changes.")

finally:
    cursor.close()
    conn.close()
    print("🔒 Database connection closed.")
    print("✅ Data loading process completed successfully.")