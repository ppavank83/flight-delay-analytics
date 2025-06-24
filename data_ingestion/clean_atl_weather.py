import pandas as pd

# Load the raw NOAA weather file (ATL - Station 72219013874)
df = pd.read_csv("72219013874.csv")

# Filter for March 2025 (optional: skip if you want full year)
df["DATE"] = pd.to_datetime(df["DATE"])
df = df[df["DATE"].dt.month == 3]

# Helper functionspy
def parse_temperature(tmp_str):
    try:
        temp = int(str(tmp_str).split(',')[0])  # TMP column = "+0128,1"
        return temp / 10.0  # NOAA temp is in tenths of °C
    except:
        return None

def parse_wind_speed(wnd_str):
    try:
        parts = str(wnd_str).split(',')
        wind_speed_mps = int(parts[3])
        return round(wind_speed_mps * 3.6, 1)  # convert m/s to km/h
    except:
        return None

def parse_visibility(vis_str):
    try:
        vis_m = int(str(vis_str).split(',')[0])
        return round(vis_m / 1000.0, 1)  # meters to km
    except:
        return None

# Clean fields
df["temp_c"] = df["TMP"].apply(parse_temperature)
df["wind_speed_kph"] = df["WND"].apply(parse_wind_speed)
df["visibility_km"] = df["VIS"].apply(parse_visibility)
df["station"] = "KATL"
df["weather_code"] = "Clear"  # fallback, WX info is sparse in NOAA

# Final columns
clean_df = df[["station", "DATE", "temp_c", "wind_speed_kph", "visibility_km", "weather_code"]]
clean_df.columns = ["station", "date", "temp_c", "wind_speed_kph", "visibility_km", "weather_code"]

# Save cleaned file
clean_df.to_csv("weather_atl_march2025.csv", index=False)
print("Cleaned weather data saved as weather_atl_march2025.csv")
