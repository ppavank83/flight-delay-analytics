-- Step 1: Assign a unique ID to each ATL-origin flight
WITH numbered_flights AS (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY flight_date, scheduled_dep_time) AS flight_id,
        *
    FROM flights_raw
    WHERE origin = 'ATL'
),

-- Step 2: Compute diversion rates
origin_diversion AS (
    SELECT 
        origin,
        CAST(SUM(CAST(diverted AS INT)) * 1.0 / COUNT(*) AS FLOAT) AS diversion_rate_origin
    FROM flights_raw
    GROUP BY origin
),
carrier_diversion AS (
    SELECT 
        carrier_code,
        CAST(SUM(CAST(diverted AS INT)) * 1.0 / COUNT(*) AS FLOAT) AS diversion_rate_carrier
    FROM flights_raw
    GROUP BY carrier_code
),

-- Step 3: Deduplicated exact matches (same hour)
exact_matches AS (
    SELECT *
    FROM (
        SELECT
            nf.flight_id,
            nf.flight_date,
            nf.carrier_code,
            nf.origin,
            nf.destination,
            CAST(nf.scheduled_dep_time / 100 AS INT) AS dep_hour,
            nf.day_of_week,
            w.temp_c,
            w.wind_speed_kph,
            w.visibility_km,
            w.weather_code,
            nf.dep_delay,
            nf.arr_delay,
            CASE WHEN nf.arr_delay > 15 THEN 1 ELSE 0 END AS delay_flag,
            od.diversion_rate_origin,
            cd.diversion_rate_carrier,
            ROW_NUMBER() OVER (
                PARTITION BY nf.flight_id
                ORDER BY w.date
            ) AS rn
        FROM numbered_flights nf
        JOIN weather_raw w
            ON w.station = CONCAT('K', nf.origin)
            AND CAST(nf.flight_date AS DATE) = CAST(w.date AS DATE)
            AND CAST(nf.scheduled_dep_time / 100 AS INT) = DATEPART(HOUR, w.date)
        LEFT JOIN origin_diversion od ON nf.origin = od.origin
        LEFT JOIN carrier_diversion cd ON nf.carrier_code = cd.carrier_code
    ) AS ranked_exact
    WHERE rn = 1
),

-- Step 4: Deduplicated closest match (±1 hour), excluding those already matched
ranked_matches AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY nf.flight_id
            ORDER BY ABS(CAST(nf.scheduled_dep_time / 100 AS INT) - DATEPART(HOUR, w.date))
        ) AS rn
    FROM numbered_flights nf
    JOIN weather_raw w
        ON w.station = CONCAT('K', nf.origin)
        AND CAST(nf.flight_date AS DATE) = CAST(w.date AS DATE)
        AND ABS(CAST(nf.scheduled_dep_time / 100 AS INT) - DATEPART(HOUR, w.date)) <= 1
        AND CAST(nf.scheduled_dep_time / 100 AS INT) <> DATEPART(HOUR, w.date)
),
closest_matches AS (
    SELECT
        nf.flight_id,
        nf.flight_date,
        nf.carrier_code,
        nf.origin,
        nf.destination,
        CAST(nf.scheduled_dep_time / 100 AS INT) AS dep_hour,
        nf.day_of_week,
        w.temp_c,
        w.wind_speed_kph,
        w.visibility_km,
        w.weather_code,
        nf.dep_delay,
        nf.arr_delay,
        CASE WHEN nf.arr_delay > 15 THEN 1 ELSE 0 END AS delay_flag,
        od.diversion_rate_origin,
        cd.diversion_rate_carrier
    FROM ranked_matches rm
    JOIN numbered_flights nf ON rm.flight_id = nf.flight_id
    JOIN weather_raw w
        ON w.station = CONCAT('K', nf.origin)
        AND CAST(nf.flight_date AS DATE) = CAST(w.date AS DATE)
        AND ABS(CAST(nf.scheduled_dep_time / 100 AS INT) - DATEPART(HOUR, w.date)) <= 1
        AND CAST(nf.scheduled_dep_time / 100 AS INT) <> DATEPART(HOUR, w.date)
    LEFT JOIN origin_diversion od ON nf.origin = od.origin
    LEFT JOIN carrier_diversion cd ON nf.carrier_code = cd.carrier_code
    WHERE rm.rn = 1
    AND NOT EXISTS (
        SELECT 1 FROM exact_matches em WHERE em.flight_id = rm.flight_id
    )
)

-- Step 5: Final result (exact if available, else closest)
SELECT
    flight_id,
    flight_date,
    carrier_code,
    origin,
    destination,
    dep_hour,
    day_of_week,
    temp_c,
    wind_speed_kph,
    visibility_km,
    weather_code,
    dep_delay,
    arr_delay,
    delay_flag,
    diversion_rate_origin,
    diversion_rate_carrier
FROM exact_matches

UNION

SELECT
    flight_id,
    flight_date,
    carrier_code,
    origin,
    destination,
    dep_hour,
    day_of_week,
    temp_c,
    wind_speed_kph,
    visibility_km,
    weather_code,
    dep_delay,
    arr_delay,
    delay_flag,
    diversion_rate_origin,
    diversion_rate_carrier
FROM closest_matches;
