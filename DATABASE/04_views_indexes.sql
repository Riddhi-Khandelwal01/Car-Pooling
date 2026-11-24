
USE campusride;

-- =========================================
-- VIEW 1: DRIVER RATINGS
-- =========================================
CREATE OR REPLACE VIEW vw_driver_ratings AS
SELECT
    s.Student_ID AS Driver_ID,
    s.Student_Name AS Driver_Name,
    COUNT(r.Rating_ID) AS Number_Of_Ratings,
    ROUND(AVG(r.Rating), 2) AS Average_Rating
FROM STUDENT s
JOIN RATING r
    ON s.Student_ID = r.Driver_ID
GROUP BY s.Student_ID, s.Student_Name;


-- =========================================
-- VIEW 2: BOOKING SUMMARY
-- =========================================
CREATE OR REPLACE VIEW vw_booking_summary AS
SELECT
    b.Booking_ID,
    b.Ride_ID,
    b.Passenger_ID,
    s.Student_Name AS Passenger_Name,
    b.Booking_Date,
    b.Seats_Booked,
    b.Booking_Status,
    p.Payment_ID,
    p.Amount,
    p.Payment_Mode,
    p.Payment_Status
FROM BOOKING b
JOIN STUDENT s
    ON b.Passenger_ID = s.Student_ID
LEFT JOIN PAYMENT p
    ON b.Booking_ID = p.Booking_ID;


-- =========================================
-- REQUIRED INDEXES
-- =========================================

CREATE INDEX idx_ride_date_pickup_drop
ON RIDE(Ride_Date, Pickup_ID, Drop_ID);

CREATE INDEX idx_booking_passenger
ON BOOKING(Passenger_ID);


-- =========================================
-- EXPLAIN DEMONSTRATIONS
-- =========================================

EXPLAIN
SELECT *
FROM RIDE
WHERE Ride_Date = '2026-11-20'
AND Pickup_ID = 1
AND Drop_ID = 4;

EXPLAIN
SELECT *
FROM BOOKING
WHERE Passenger_ID = 2;

-- VERIFY VIEWS
SHOW FULL TABLES
WHERE Table_type = 'VIEW';

SELECT * FROM vw_driver_ratings;
SELECT * FROM vw_booking_summary;



