CREATE TABLE flight_predictions (
    flight_id INT,
    prediction FLOAT,
    predicted_label INT,
    predicted_on DATETIME DEFAULT GETDATE()
);
