import pyodbc

# Replace these with your actual credentials
server = 'flight-sql-server-pavan.database.windows.net'
database = 'flightdb'
username = 'sqladmin'
password = 'P@van2306'

try:
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )
    print(" Connection successful!")

    # Optional: test query
    cursor = conn.cursor()
    cursor.execute("SELECT GETDATE();")
    print(" Server Time:", cursor.fetchone()[0])

    conn.close()
except Exception as e:
    print("Connection failed:", e)