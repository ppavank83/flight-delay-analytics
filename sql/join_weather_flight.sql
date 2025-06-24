-- Compute diversion rate (ratio of diverted flights) per origin airport
WITH origin_diversion AS (
    SELECT 
        origin,
        CAST(SUM(CAST(diverted AS INT)) * 1.0 / COUNT(*) AS FLOAT) AS diversion_rate_origin
        -- Convert BIT to INT, then compute average = diversion rate
    FROM flights_raw
    GROUP BY origin
),

-- Compute diversion rate per carrier (airline)
carrier_diversion AS (
    SELECT 
        carrier_code,
        CAST(SUM(CAST(diverted AS INT)) * 1.0 / COUNT(*) AS FLOAT) AS diversion_rate_carrier
    FROM flights_raw
    GROUP BY carrier_code
),

-- Extract flights with exact weather match (same hour)
exact_matches AS (
    SELECT
        f.flight_date,
        f.carrier_code,
        f.origin,
        f.destination,
        CAST(f.scheduled_dep_time / 100 AS INT) AS dep_hour,  -- Extract departure hour from HHMM format
        f.day_of_week,
        w.temp_c,
        w.wind_speed_kph,
        w.visibility_km,
        w.weather_code,
        f.dep_delay,
        f.arr_delay,
        CASE WHEN f.arr_delay > 15 THEN 1 ELSE 0 END AS delay_flag,  -- Binary label for delayed arrival
        od.diversion_rate_origin,
        cd.diversion_rate_carrier,
        -- Generate a unique flight key using carrier, origin, flight number, and date
        f.carrier_code + '_' + f.origin + '_' + CAST(f.flight_number AS VARCHAR) + '_' + CONVERT(VARCHAR, f.flight_date, 23) AS flight_key
    FROM flights_raw f
    JOIN weather_raw w
        ON w.station = CONCAT('K', f.origin)  -- Weather station format is like 'KATL' for ATL
        AND CAST(f.flight_date AS DATE) = CAST(w.date AS DATE)  -- Join on same day
        AND CAST(f.scheduled_dep_time / 100 AS INT) = DATEPART(HOUR, w.date)  -- Exact hour match
    LEFT JOIN origin_diversion od ON f.origin = od.origin
    LEFT JOIN carrier_diversion cd ON f.carrier_code = cd.carrier_code
    WHERE f.origin = 'ATL'  -- Filter only for ATL flights
),

-- Find closest weather match for each flight (excluding exact matches)
ranked_matches AS (
    SELECT *,
        -- Assign rank to each weather match for a flight based on how close the hour is to departure
        ROW_NUMBER() OVER (
            PARTITION BY f.carrier_code, f.origin, f.flight_number, f.flight_date
            ORDER BY ABS(CAST(f.scheduled_dep_time / 100 AS INT) - DATEPART(HOUR, w.date))  -- Lower hour diff = better
        ) AS rn
    FROM flights_raw f
    JOIN weather_raw w
        ON w.station = CONCAT('K', f.origin)
        AND CAST(f.flight_date AS DATE) = CAST(w.date AS DATE)
        AND ABS(CAST(f.scheduled_dep_time / 100 AS INT) - DATEPART(HOUR, w.date)) <= 1  -- Match within ±1 hour
        AND CAST(f.scheduled_dep_time / 100 AS INT) <> DATEPART(HOUR, w.date)  -- Exclude exact matches
    WHERE f.origin = 'ATL'
),

-- Select only the closest weather row for each unmatched flight
closest_matches AS (
    SELECT
        f.flight_date,
        f.carrier_code,
        f.origin,
        f.destination,
        CAST(f.scheduled_dep_time / 100 AS INT) AS dep_hour,
        f.day_of_week,
        w.temp_c,
        w.wind_speed_kph,
        w.visibility_km,
        w.weather_code,
        f.dep_delay,
        f.arr_delay,
        CASE WHEN f.arr_delay > 15 THEN 1 ELSE 0 END AS delay_flag,
        od.diversion_rate_origin,
        cd.diversion_rate_carrier,
        f.carrier_code + '_' + f.origin + '_' + CAST(f.flight_number AS VARCHAR) + '_' + CONVERT(VARCHAR, f.flight_date, 23) AS flight_key
    FROM ranked_matches f
    JOIN weather_raw w
        ON w.station = CONCAT('K', f.origin)
        AND CAST(f.flight_date AS DATE) = CAST(w.date AS DATE)
        AND ABS(CAST(f.scheduled_dep_time / 100 AS INT) - DATEPART(HOUR, w.date)) <= 1
        AND CAST(f.scheduled_dep_time / 100 AS INT) <> DATEPART(HOUR, w.date)
    LEFT JOIN origin_diversion od ON f.origin = od.origin
    LEFT JOIN carrier_diversion cd ON f.carrier_code = cd.carrier_code
    WHERE f.rn = 1  -- Keep only the top-ranked (closest) weather row
)

-- Final union of exact and closest matches
-- UNION automatically removes duplicates based on all selected fields (includes flight_key)
SELECT * FROM exact_matches
UNION
SELECT * FROM closest_matches