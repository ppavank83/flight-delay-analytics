CREATE TABLE flight_weather_features (
    flight_id INT PRIMARY KEY,
    flight_date DATE,
    carrier_code VARCHAR(10),
    origin VARCHAR(5),
    destination VARCHAR(5),
    dep_hour INT,
    day_of_week INT,
    temp_c FLOAT,
    wind_speed_kph FLOAT,
    visibility_km FLOAT,
    weather_code VARCHAR(20),
    dep_delay FLOAT,
    arr_delay FLOAT,
    delay_flag INT,
    diversion_rate_origin FLOAT,
    diversion_rate_carrier FLOAT
);
