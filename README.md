# ✈️ Flight Delay Analytics Project

This project analyzes and predicts flight delays using historical flight and weather data. It covers everything from data ingestion to feature engineering and prepares the data for machine learning model training and interpretation.

---
```
## 📁 Project Structure

flight-delay-analytics/
│
├── data/ # Raw flight and weather CSVs
├── data_ingestion/ # Scripts to load and process raw data
├── sql/ # SQL scripts to create and populate tables
├── model_training/ # Notebooks for EDA and modeling
├── test.ipynb # Temporary notebook for testing
├── README.md # Project documentation
└── requirements.txt # Required Python packages
```

---

## ✅ Completed Work

### 🔹 Data Ingestion

- Loaded historical **flight** and **weather** data.
- Filtered weather data for ATL station only.
- Created SQL tables using scripts in the `sql/` directory.
- Joined flight and weather data with time alignment logic:
  - Used **exact match** if flight hour matches weather hour.
  - If not, used **closest match within ±1 hour**.
- Created new features:
  - `delay_flag` (1 if arrival delay > 15 min)
  - `diversion_rate_origin` and `diversion_rate_carrier`.

### 🔹 ETL Scripts

- `load_data_to_sql.py`: Loads raw flight and weather CSVs into Azure SQL.
- `generate_flight_weather_features.py`: Joins and prepares final dataset for modeling.
- `clean_atl_weather.py`: Extracts ATL-specific weather data.

### 🔹 Database

- Azure SQL Database stores all structured tables.
- Joins use optimized logic based on time and station match.
- Final data saved to `flight_weather_features` table.

### 🔹 Git Integration

- Project is version-controlled using Git.
- GitHub used for repository management.
- `.gitignore` includes test files like `test.ipynb`.

---

## 🔄 Next Steps

- Perform **Exploratory Data Analysis (EDA)**.
- Handle **missing values** and **encode categorical features**.
- Perform additional **feature engineering** if necessary.
- Analyze **class separability**.
- Train and evaluate ML models.
- Compare **LIME** and **SHAP** explanations with feature importances.

---

## 📊 Data Sources

- ✈️ [Flight Delay Data (BTS)](https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ&QO_fu146_anzr=b0-gvzr)
- 🌦️ [Global Hourly Weather Data (NOAA)](https://www.ncei.noaa.gov/data/global-hourly/access/2025/)

---

## ⚙️ Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/flight-delay-analytics.git

# 2. Navigate to the project
cd flight-delay-analytics

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file in the root directory with the following variables:
SQL_SERVER=your_server.database.windows.net
SQL_DATABASE=your_database_name
SQL_USERNAME=your_sql_username
SQL_PASSWORD=your_sql_password


⚠️ Notes
.ipynb test files are excluded in .gitignore.

Large data files (>50 MB) are not recommended to track in GitHub directly. Use Git LFS or store them externally.
