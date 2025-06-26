import pandas as pd
import pyodbc
from dotenv import load_dotenv
import os
from tqdm import tqdm

# Load environment variables
load_dotenv()

# SQL connection parameters
server = os.getenv("SQL_SERVER")
database = os.getenv("SQL_DATABASE")
username = os.getenv("SQL_USERNAME")
password = os.getenv("SQL_PASSWORD")

conn = None
cursor = None

try:
    # Establish connection
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )
    conn.autocommit = False
    cursor = conn.cursor()
    cursor.fast_executemany = True
    print("Connected to Azure SQL.")

    # Load join query
    sql_path = "sql\join_weather_flight.sql"
    with open(sql_path, "r") as file:
        join_query = file.read()

    # Execute and fetch result
    df = pd.read_sql(join_query, conn)
    print(f"Pulled {len(df)} rows from join query.")

    # Define expected insert column names
    expected_cols = [
        "flight_id", "flight_date", "carrier_code", "origin", "destination", "dep_hour",
        "day_of_week", "temp_c", "wind_speed_kph", "visibility_km", "weather_code",
        "dep_delay", "arr_delay", "delay_flag",
        "diversion_rate_origin", "diversion_rate_carrier"
    ]

    # Map actual column names in df (case-insensitive)
    col_lookup = {col.lower(): col for col in df.columns}

    # Validate all required columns are present
    missing = [col for col in expected_cols if col.lower() not in col_lookup]
    if missing:
        raise ValueError(f"Missing expected columns in SQL output: {missing}")

    # Build rows for insert
    flight_rows = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Preparing Rows"):
        values = [
            None if pd.isna(row[col_lookup[col.lower()]]) else row[col_lookup[col.lower()]]
            for col in expected_cols
        ]
        flight_rows.append(tuple(values))

    # Insert into flight_weather_features table
    insert_query = f"""
    INSERT INTO flight_weather_features ({', '.join(expected_cols)})
    VALUES ({', '.join(['?'] * len(expected_cols))})
    """

    for i in tqdm(range(0, len(flight_rows), 1000), desc="Inserting Batches"):
        batch = flight_rows[i:i + 1000]
        cursor.executemany(insert_query, batch)

    conn.commit()
    print(f"Successfully inserted {len(flight_rows)} rows into flight_weather_features.")

except KeyboardInterrupt:
    if conn:
        conn.rollback()
    print("\nOperation interrupted by user (Ctrl+C). Changes have been rolled back.")

except Exception as e:
    if conn:
        conn.rollback()
    print("Error occurred:", e)
    print("Rolled back all changes.")

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
    print("Connection closed.")
