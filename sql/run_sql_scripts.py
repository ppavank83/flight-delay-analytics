from dotenv import load_dotenv
import os
import pyodbc

# Load secrets from .env
load_dotenv()

server = os.getenv("SQL_SERVER")
database = os.getenv("SQL_DATABASE")
username = os.getenv("SQL_USERNAME")
password = os.getenv("SQL_PASSWORD")

# Connect
conn = pyodbc.connect(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};DATABASE={database};UID={username};PWD={password}"
)
cursor = conn.cursor()

# Table names and corresponding scripts
script_map = {
    "flights_raw": "sql/create_flights_table.sql",
    "weather_raw": "sql/create_weather_raw.sql",
    "flight_weather_features": "sql/create_flight_weather_features.sql",
    "flight_predictions": "sql/create_flight_predictions.sql"
}

# Function to check if table exists
def table_exists(table_name):
    cursor.execute("""
        SELECT 1
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME = ?
    """, (table_name,))
    return cursor.fetchone() is not None

# Execute scripts if needed
for table, path in script_map.items():
    if table_exists(table):
        print(f"  Table '{table}' already exists. Skipping: {path}")
        continue

    with open(path, 'r') as file:
        sql = file.read()
        for statement in sql.strip().split('GO'):
            if statement.strip():
                cursor.execute(statement)
        conn.commit()
        print(f" Executed and created table: {table} from {path}")

cursor.close()
conn.close()
