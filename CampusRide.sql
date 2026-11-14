DROP DATABASE IF EXISTS campusride;
CREATE DATABASE campusride;
USE campusride;

-- =====================================================================
-- PART 1 : TABLE CREATION (DDL)  -- 7 tables
-- =====================================================================

-- 1. STUDENT : one table for both drivers and passengers
CREATE TABLE STUDENT (
    Student_ID    INT AUTO_INCREMENT,
    Student_Name  VARCHAR(100) NOT NULL,
    Email         VARCHAR(100) NOT NULL,
    Phone         VARCHAR(15)  NOT NULL,
    Department    VARCHAR(50)  NOT NULL,
    `Year`        TINYINT      NOT NULL,
    CONSTRAINT pk_student       PRIMARY KEY (Student_ID),
    CONSTRAINT uq_student_email UNIQUE (Email),
    CONSTRAINT ck_student_year  CHECK (`Year` BETWEEN 1 AND 5),
    CONSTRAINT ck_student_phone CHECK (Phone REGEXP '^[0-9]{10,15}$')
) ENGINE=InnoDB;

-- 2. VEHICLE : owned by a student (1 student -> many vehicles)
CREATE TABLE VEHICLE (
    Vehicle_ID        INT AUTO_INCREMENT,
    Student_ID        INT         NOT NULL,
    Vehicle_Number    VARCHAR(20) NOT NULL,
    Vehicle_Model     VARCHAR(50) NOT NULL,
    Vehicle_Type      VARCHAR(20) NOT NULL DEFAULT 'Car',
    Seating_Capacity  INT         NOT NULL,   -- passenger seats available (excluding driver)
    CONSTRAINT pk_vehicle        PRIMARY KEY (Vehicle_ID),
    CONSTRAINT uq_vehicle_number UNIQUE (Vehicle_Number),
    CONSTRAINT fk_vehicle_owner  FOREIGN KEY (Student_ID) REFERENCES STUDENT(Student_ID),
    CONSTRAINT ck_vehicle_type   CHECK (Vehicle_Type IN ('Car','Bike','Scooter','SUV')),
    CONSTRAINT ck_vehicle_cap    CHECK (Seating_Capacity BETWEEN 1 AND 8)
) ENGINE=InnoDB;

-- 3. LOCATION : used twice in RIDE (pickup and drop)
CREATE TABLE LOCATION (
    Location_ID    INT AUTO_INCREMENT,
    Location_Name  VARCHAR(100) NOT NULL,
    Area           VARCHAR(50)  NOT NULL,
    City           VARCHAR(50)  NOT NULL,
    CONSTRAINT pk_location PRIMARY KEY (Location_ID),
    CONSTRAINT uq_location UNIQUE (Location_Name, Area, City)
) ENGINE=InnoDB;

-- 4. RIDE : offered by a driver (student) using one of his vehicles
CREATE TABLE RIDE (
    Ride_ID          INT AUTO_INCREMENT,
    Driver_ID        INT           NOT NULL,
    Vehicle_ID       INT           NOT NULL,
    Pickup_ID        INT           NOT NULL,
    Drop_ID          INT           NOT NULL,
    Ride_Date        DATE          NOT NULL,
    Ride_Time        TIME          NOT NULL,
    Available_Seats  INT           NOT NULL,
    Fare_Per_Seat    DECIMAL(8,2)  NOT NULL,
    Ride_Status      VARCHAR(15)   NOT NULL DEFAULT 'Scheduled',
    CONSTRAINT pk_ride        PRIMARY KEY (Ride_ID),
    CONSTRAINT fk_ride_driver FOREIGN KEY (Driver_ID)  REFERENCES STUDENT(Student_ID),
    CONSTRAINT fk_ride_vehicle FOREIGN KEY (Vehicle_ID) REFERENCES VEHICLE(Vehicle_ID),
    CONSTRAINT fk_ride_pickup FOREIGN KEY (Pickup_ID)  REFERENCES LOCATION(Location_ID),
    CONSTRAINT fk_ride_drop   FOREIGN KEY (Drop_ID)    REFERENCES LOCATION(Location_ID),
    CONSTRAINT ck_ride_seats  CHECK (Available_Seats >= 0),
    CONSTRAINT ck_ride_fare   CHECK (Fare_Per_Seat >= 0),
    CONSTRAINT ck_ride_route  CHECK (Pickup_ID <> Drop_ID),
    CONSTRAINT ck_ride_status CHECK (Ride_Status IN ('Scheduled','Ongoing','Completed','Cancelled'))
) ENGINE=InnoDB;

-- 5. BOOKING : a passenger books seats in a ride
CREATE TABLE BOOKING (
    Booking_ID      INT AUTO_INCREMENT,
    Ride_ID         INT         NOT NULL,
    Passenger_ID    INT         NOT NULL,
    Booking_Date    DATE        NOT NULL DEFAULT (CURRENT_DATE),
    Seats_Booked    INT         NOT NULL,
    Booking_Status  VARCHAR(15) NOT NULL DEFAULT 'Confirmed',
    CONSTRAINT pk_booking           PRIMARY KEY (Booking_ID),
    CONSTRAINT fk_booking_ride      FOREIGN KEY (Ride_ID)      REFERENCES RIDE(Ride_ID),
    CONSTRAINT fk_booking_passenger FOREIGN KEY (Passenger_ID) REFERENCES STUDENT(Student_ID),
    CONSTRAINT uq_booking_once      UNIQUE (Ride_ID, Passenger_ID),
    CONSTRAINT ck_booking_seats     CHECK (Seats_Booked > 0),
    CONSTRAINT ck_booking_status    CHECK (Booking_Status IN ('Confirmed','Cancelled','Completed'))
) ENGINE=InnoDB;

-- 6. PAYMENT : exactly one payment per booking (1:1 -> Booking_ID is UNIQUE)
CREATE TABLE PAYMENT (
    Payment_ID      INT AUTO_INCREMENT,
    Booking_ID      INT           NOT NULL,
    Payment_Date    DATE          NOT NULL DEFAULT (CURRENT_DATE),
    Amount          DECIMAL(8,2)  NOT NULL,
    Payment_Mode    VARCHAR(10)   NOT NULL,
    Payment_Status  VARCHAR(10)   NOT NULL DEFAULT 'Pending',
    CONSTRAINT pk_payment         PRIMARY KEY (Payment_ID),
    CONSTRAINT uq_payment_booking UNIQUE (Booking_ID),
    CONSTRAINT fk_payment_booking FOREIGN KEY (Booking_ID) REFERENCES BOOKING(Booking_ID),
    CONSTRAINT ck_payment_amount  CHECK (Amount >= 0),
    CONSTRAINT ck_payment_mode    CHECK (Payment_Mode IN ('Cash','UPI','Card','Wallet')),
    CONSTRAINT ck_payment_status  CHECK (Payment_Status IN ('Pending','Paid','Refunded'))
) ENGINE=InnoDB;

-- 7. RATING : passenger rates the driver after a completed ride
CREATE TABLE RATING (
    Rating_ID     INT AUTO_INCREMENT,
    Ride_ID       INT          NOT NULL,
    Passenger_ID  INT          NOT NULL,
    Driver_ID     INT          NOT NULL,
    Rating        TINYINT      NOT NULL,
    Review        VARCHAR(255),
    Rating_Date   DATE         NOT NULL DEFAULT (CURRENT_DATE),
    CONSTRAINT pk_rating           PRIMARY KEY (Rating_ID),
    CONSTRAINT fk_rating_ride      FOREIGN KEY (Ride_ID)      REFERENCES RIDE(Ride_ID),
    CONSTRAINT fk_rating_passenger FOREIGN KEY (Passenger_ID) REFERENCES STUDENT(Student_ID),
    CONSTRAINT fk_rating_driver    FOREIGN KEY (Driver_ID)    REFERENCES STUDENT(Student_ID),
    CONSTRAINT uq_rating_once      UNIQUE (Ride_ID, Passenger_ID),
    CONSTRAINT ck_rating_value     CHECK (Rating BETWEEN 1 AND 5)
) ENGINE=InnoDB;

-- Helpful indexes for searching rides
CREATE INDEX idx_ride_search   ON RIDE (Pickup_ID, Drop_ID, Ride_Date);
CREATE INDEX idx_booking_ride  ON BOOKING (Ride_ID);


-- =====================================================================
-- PART 2 : TRIGGERS (business rules + automatic seat update)
-- =====================================================================
DELIMITER $$

-- Ride: driver must own the vehicle, offered seats cannot exceed capacity
CREATE TRIGGER trg_ride_before_insert
BEFORE INSERT ON RIDE
FOR EACH ROW
BEGIN
    DECLARE v_owner INT;
    DECLARE v_cap   INT;

    SELECT Student_ID, Seating_Capacity INTO v_owner, v_cap
    FROM VEHICLE WHERE Vehicle_ID = NEW.Vehicle_ID;

    IF v_owner IS NULL OR v_owner <> NEW.Driver_ID THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Driver can offer rides only with his/her own vehicle';
    END IF;

    IF NEW.Available_Seats > v_cap THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Available seats cannot exceed the vehicle seating capacity';
    END IF;
END$$

-- Booking: validate before saving
CREATE TRIGGER trg_booking_before_insert
BEFORE INSERT ON BOOKING
FOR EACH ROW
BEGIN
    DECLARE v_driver INT;
    DECLARE v_seats  INT;
    DECLARE v_status VARCHAR(15);

    SELECT Driver_ID, Available_Seats, Ride_Status
    INTO v_driver, v_seats, v_status
    FROM RIDE WHERE Ride_ID = NEW.Ride_ID
    FOR UPDATE;

    IF v_status IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ride does not exist';
    END IF;
    IF v_status <> 'Scheduled' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seats can be booked only in a Scheduled ride';
    END IF;
    IF v_driver = NEW.Passenger_ID THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Driver cannot book a seat in his/her own ride';
    END IF;
    IF NEW.Seats_Booked > v_seats THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Not enough seats available in this ride';
    END IF;
END$$

-- Booking: reduce available seats automatically
CREATE TRIGGER trg_booking_after_insert
AFTER INSERT ON BOOKING
FOR EACH ROW
BEGIN
    IF NEW.Booking_Status = 'Confirmed' THEN
        UPDATE RIDE
        SET Available_Seats = Available_Seats - NEW.Seats_Booked
        WHERE Ride_ID = NEW.Ride_ID;
    END IF;
END$$

-- Booking: give seats back when a confirmed booking is cancelled
CREATE TRIGGER trg_booking_after_update
AFTER UPDATE ON BOOKING
FOR EACH ROW
BEGIN
    IF OLD.Booking_Status = 'Confirmed' AND NEW.Booking_Status = 'Cancelled' THEN
        UPDATE RIDE
        SET Available_Seats = Available_Seats + OLD.Seats_Booked
        WHERE Ride_ID = OLD.Ride_ID;
    END IF;
END$$

-- Payment: amount must equal seats booked x fare per seat
CREATE TRIGGER trg_payment_before_insert
BEFORE INSERT ON PAYMENT
FOR EACH ROW
BEGIN
    DECLARE v_expected DECIMAL(8,2);

    SELECT b.Seats_Booked * r.Fare_Per_Seat INTO v_expected
    FROM BOOKING b JOIN RIDE r ON r.Ride_ID = b.Ride_ID
    WHERE b.Booking_ID = NEW.Booking_ID;

    IF v_expected IS NULL OR NEW.Amount <> v_expected THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Payment amount must equal Seats_Booked x Fare_Per_Seat';
    END IF;
END$$

-- Rating: only a passenger of a completed ride can rate that ride's driver
CREATE TRIGGER trg_rating_before_insert
BEFORE INSERT ON RATING
FOR EACH ROW
BEGIN
    DECLARE v_driver INT;
    DECLARE v_status VARCHAR(15);
    DECLARE v_booked INT;

    SELECT Driver_ID, Ride_Status INTO v_driver, v_status
    FROM RIDE WHERE Ride_ID = NEW.Ride_ID;

    SELECT COUNT(*) INTO v_booked
    FROM BOOKING
    WHERE Ride_ID = NEW.Ride_ID AND Passenger_ID = NEW.Passenger_ID
      AND Booking_Status IN ('Confirmed','Completed');

    IF v_status IS NULL OR v_status <> 'Completed' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only completed rides can be rated';
    END IF;
    IF v_driver <> NEW.Driver_ID THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Driver_ID does not match the driver of this ride';
    END IF;
    IF v_booked = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Passenger did not travel in this ride';
    END IF;
END$$

DELIMITER ;


-- =====================================================================
-- PART 3 : SAMPLE DATA
-- =====================================================================

INSERT INTO STUDENT (Student_Name, Email, Phone, Department, `Year`) VALUES
('Anukriti Pandey',  'anukriti.pandey@jiit.ac.in',  '9811000001', 'CSE',  2),  -- 1
('Riddhi Khandelwal','riddhi.khandelwal@jiit.ac.in','9811000002', 'CSE',  2),  -- 2
('Aarav Sharma',     'aarav.sharma@jiit.ac.in',     '9811000003', 'ECE',  3),  -- 3
('Priya Singh',      'priya.singh@jiit.ac.in',      '9811000004', 'CSE',  4),  -- 4
('Rohan Verma',      'rohan.verma@jiit.ac.in',      '9811000005', 'IT',   1),  -- 5
('Neha Gupta',       'neha.gupta@jiit.ac.in',       '9811000006', 'BT',   3),  -- 6
('Karan Mehta',      'karan.mehta@jiit.ac.in',      '9811000007', 'ECE',  2),  -- 7
('Simran Kaur',      'simran.kaur@jiit.ac.in',      '9811000008', 'IT',   4),  -- 8
('Aditya Jain',      'aditya.jain@jiit.ac.in',      '9811000009', 'CSE',  1),  -- 9
('Ishita Rao',       'ishita.rao@jiit.ac.in',       '9811000010', 'BT',   2);  -- 10

INSERT INTO VEHICLE (Student_ID, Vehicle_Number, Vehicle_Model, Vehicle_Type, Seating_Capacity) VALUES
(1, 'UP16AB1234', 'Maruti Swift',      'Car',     4),   -- 1
(3, 'UP16CD5678', 'Honda Activa',      'Scooter', 1),   -- 2
(4, 'DL01EF9012', 'Maruti Ertiga',     'SUV',     6),   -- 3
(6, 'UP14GH3456', 'Hyundai i20',       'Car',     4),   -- 4
(8, 'HR26JK7890', 'Tata Nexon',        'Car',     4);   -- 5

INSERT INTO LOCATION (Location_Name, Area, City) VALUES
('JIIT Sector 62',            'Sector 62',      'Noida'),        -- 1
('Noida Sector 18 Metro',     'Sector 18',      'Noida'),        -- 2
('Botanical Garden Metro',    'Sector 38',      'Noida'),        -- 3
('Rajiv Chowk Metro',         'Connaught Place','New Delhi'),    -- 4
('Anand Vihar ISBT',          'Anand Vihar',    'New Delhi'),    -- 5
('New Delhi Railway Station', 'Paharganj',      'New Delhi'),    -- 6
('Pari Chowk',                'Alpha',          'Greater Noida'),-- 7
('Indirapuram Shakti Khand',  'Indirapuram',    'Ghaziabad'),    -- 8
('Noida City Centre Metro',   'Sector 32',      'Noida'),        -- 9
('Hazrat Nizamuddin Station', 'Nizamuddin',     'New Delhi');    -- 10

INSERT INTO RIDE (Driver_ID, Vehicle_ID, Pickup_ID, Drop_ID, Ride_Date, Ride_Time, Available_Seats, Fare_Per_Seat, Ride_Status) VALUES
(1, 1, 1, 2,  '2026-11-10', '08:30:00', 4,  40.00, 'Scheduled'),  -- 1  (completed later)
(1, 1, 2, 1,  '2026-11-10', '17:30:00', 4,  40.00, 'Scheduled'),  -- 2  (completed later)
(3, 2, 1, 3,  '2026-11-12', '09:00:00', 1,  30.00, 'Scheduled'),  -- 3  (completed later)
(4, 3, 1, 4,  '2026-11-20', '07:45:00', 3, 120.00, 'Scheduled'),  -- 4
(6, 4, 7, 1,  '2026-11-21', '08:00:00', 4,  60.00, 'Scheduled'),  -- 5
(8, 5, 1, 5,  '2026-11-22', '06:30:00', 3, 100.00, 'Scheduled'),  -- 6
(1, 1, 1, 6,  '2026-11-25', '05:30:00', 4, 150.00, 'Scheduled'),  -- 7
(4, 3, 8, 1,  '2026-11-18', '08:15:00', 5,  70.00, 'Scheduled');  -- 8

-- Bookings (seats in RIDE are reduced automatically by the trigger)
INSERT INTO BOOKING (Ride_ID, Passenger_ID, Booking_Date, Seats_Booked, Booking_Status) VALUES
(1, 2,  '2026-11-08', 2, 'Confirmed'),   -- 1
(1, 5,  '2026-11-08', 1, 'Confirmed'),   -- 2
(2, 2,  '2026-11-09', 1, 'Confirmed'),   -- 3
(2, 7,  '2026-11-09', 2, 'Confirmed'),   -- 4
(3, 5,  '2026-11-11', 1, 'Confirmed'),   -- 5
(4, 2,  '2026-11-13', 1, 'Confirmed'),   -- 6
(4, 9,  '2026-11-13', 2, 'Confirmed'),   -- 7
(5, 3,  '2026-11-13', 1, 'Confirmed'),   -- 8
(6, 10, '2026-11-13', 1, 'Confirmed'),   -- 9
(6, 7,  '2026-11-14', 1, 'Confirmed'),   -- 10 (cancelled below)
(7, 9,  '2026-11-14', 1, 'Confirmed'),   -- 11
(8, 2,  '2026-11-14', 2, 'Confirmed'),   -- 12
(8, 5,  '2026-11-14', 1, 'Confirmed'),   -- 13
(8, 9,  '2026-11-14', 1, 'Confirmed');   -- 14

-- Payments (Amount = Seats_Booked x Fare_Per_Seat)
INSERT INTO PAYMENT (Booking_ID, Payment_Date, Amount, Payment_Mode, Payment_Status) VALUES
(1,  '2026-11-08',  80.00, 'UPI',    'Paid'),
(2,  '2026-11-10',  40.00, 'Cash',   'Paid'),
(3,  '2026-11-10',  40.00, 'UPI',    'Paid'),
(4,  '2026-11-10',  80.00, 'Cash',   'Paid'),
(5,  '2026-11-12',  30.00, 'UPI',    'Paid'),
(6,  '2026-11-13', 120.00, 'UPI',    'Paid'),
(7,  '2026-11-13', 240.00, 'Cash',   'Pending'),
(8,  '2026-11-13',  60.00, 'UPI',    'Paid'),
(9,  '2026-11-13', 100.00, 'Card',   'Paid'),
(10, '2026-11-14', 100.00, 'UPI',    'Paid'),
(11, '2026-11-14', 150.00, 'Cash',   'Pending'),
(12, '2026-11-14', 140.00, 'UPI',    'Paid'),
(13, '2026-11-14',  70.00, 'Cash',   'Pending'),
(14, '2026-11-14',  70.00, 'Wallet', 'Paid');

-- Cancel booking 10 : trigger gives the seat back, payment is refunded
UPDATE BOOKING SET Booking_Status = 'Cancelled' WHERE Booking_ID = 10;
UPDATE PAYMENT SET Payment_Status = 'Refunded'  WHERE Booking_ID = 10;

-- Complete rides 1, 2 and 3 and their bookings
UPDATE RIDE    SET Ride_Status    = 'Completed' WHERE Ride_ID IN (1, 2, 3);
UPDATE BOOKING SET Booking_Status = 'Completed' WHERE Ride_ID IN (1, 2, 3);

-- Ratings (allowed only for completed rides)
INSERT INTO RATING (Ride_ID, Passenger_ID, Driver_ID, Rating, Review, Rating_Date) VALUES
(1, 2, 1, 5, 'Very punctual and safe driving',      '2026-11-10'),
(1, 5, 1, 4, 'Comfortable ride, good music',        '2026-11-10'),
(2, 2, 1, 5, 'Smooth ride back to campus',          '2026-11-10'),
(2, 7, 1, 4, 'Good, slightly late start',           '2026-11-11'),
(3, 5, 3, 5, 'Quick and convenient scooter ride',   '2026-11-12');


-- =====================================================================
-- PART 4 : VIEW AND STORED PROCEDURES
-- =====================================================================

-- Complete ride details (multi-table JOIN, LOCATION used twice via aliases)
CREATE VIEW vw_ride_details AS
SELECT  r.Ride_ID,
        s.Student_Name   AS Driver_Name,
        s.Phone          AS Driver_Phone,
        v.Vehicle_Model,
        v.Vehicle_Number,
        lp.Location_Name AS Pickup_Location,
        ld.Location_Name AS Drop_Location,
        r.Ride_Date,
        r.Ride_Time,
        r.Available_Seats,
        r.Fare_Per_Seat,
        r.Ride_Status
FROM    RIDE r
JOIN    STUDENT  s  ON r.Driver_ID  = s.Student_ID
JOIN    VEHICLE  v  ON r.Vehicle_ID = v.Vehicle_ID
JOIN    LOCATION lp ON r.Pickup_ID  = lp.Location_ID
JOIN    LOCATION ld ON r.Drop_ID    = ld.Location_ID;

DELIMITER $$

-- Search available rides by pickup, drop (partial names allowed) and date
CREATE PROCEDURE sp_search_rides (
    IN p_pickup VARCHAR(100),
    IN p_drop   VARCHAR(100),
    IN p_date   DATE
)
BEGIN
    SELECT *
    FROM   vw_ride_details
    WHERE  Pickup_Location LIKE CONCAT('%', p_pickup, '%')
      AND  Drop_Location   LIKE CONCAT('%', p_drop,   '%')
      AND  Ride_Date = p_date
      AND  Ride_Status = 'Scheduled'
      AND  Available_Seats > 0
    ORDER  BY Ride_Time;
END$$

-- Book seats and create the payment record in one transaction
CREATE PROCEDURE sp_book_ride (
    IN p_ride_id      INT,
    IN p_passenger_id INT,
    IN p_seats        INT,
    IN p_mode         VARCHAR(10)
)
BEGIN
    DECLARE v_fare       DECIMAL(8,2);
    DECLARE v_booking_id INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    SELECT Fare_Per_Seat INTO v_fare FROM RIDE WHERE Ride_ID = p_ride_id;

    INSERT INTO BOOKING (Ride_ID, Passenger_ID, Seats_Booked)
    VALUES (p_ride_id, p_passenger_id, p_seats);

    SET v_booking_id = LAST_INSERT_ID();

    INSERT INTO PAYMENT (Booking_ID, Amount, Payment_Mode, Payment_Status)
    VALUES (v_booking_id, v_fare * p_seats, p_mode,
            CASE WHEN p_mode = 'Cash' THEN 'Pending' ELSE 'Paid' END);

    COMMIT;

    SELECT v_booking_id AS Booking_ID,
           v_fare * p_seats AS Amount_To_Pay,
           'Booking successful' AS Message;
END$$

-- Cancel a booking (seats are restored by trigger, payment is refunded)
CREATE PROCEDURE sp_cancel_booking (IN p_booking_id INT)
BEGIN
    UPDATE BOOKING SET Booking_Status = 'Cancelled'
    WHERE  Booking_ID = p_booking_id AND Booking_Status = 'Confirmed';

    UPDATE PAYMENT SET Payment_Status = 'Refunded'
    WHERE  Booking_ID = p_booking_id AND Payment_Status = 'Paid';

    SELECT ROW_COUNT() AS Payments_Refunded;
END$$

DELIMITER ;


-- =====================================================================
-- PART 5 : SQL QUERIES / REPORTS
-- =====================================================================

-- Q1. View all tables
SELECT * FROM STUDENT;
SELECT * FROM VEHICLE;
SELECT * FROM LOCATION;
SELECT * FROM RIDE;
SELECT * FROM BOOKING;
SELECT * FROM PAYMENT;
SELECT * FROM RATING;

-- Q2. Ride search: Multi-table JOIN (RIDE, STUDENT, VEHICLE, LOCATION twice)
SELECT  r.Ride_ID,
        s.Student_Name   AS Driver,
        v.Vehicle_Model,
        lp.Location_Name AS Pickup,
        ld.Location_Name AS Destination,
        r.Ride_Date, r.Ride_Time,
        r.Available_Seats, r.Fare_Per_Seat
FROM    RIDE r
JOIN    STUDENT  s  ON r.Driver_ID  = s.Student_ID
JOIN    VEHICLE  v  ON r.Vehicle_ID = v.Vehicle_ID
JOIN    LOCATION lp ON r.Pickup_ID  = lp.Location_ID
JOIN    LOCATION ld ON r.Drop_ID    = ld.Location_ID
WHERE   lp.Location_Name LIKE '%JIIT%'
  AND   ld.Location_Name LIKE '%Rajiv Chowk%'
  AND   r.Ride_Date = '2026-11-20'
  AND   r.Available_Seats > 0;

-- Q3. Same search using the stored procedure
CALL sp_search_rides('JIIT', 'Rajiv', '2026-11-20');

-- Q4. Aggregate functions: COUNT, SUM, AVG, MAX
SELECT COUNT(*)           AS Total_Bookings        FROM BOOKING;
SELECT SUM(Amount)        AS Total_Amount_Paid     FROM PAYMENT WHERE Payment_Status = 'Paid';
SELECT ROUND(AVG(Rating),2) AS Overall_Avg_Rating  FROM RATING;
SELECT ROUND(AVG(Fare_Per_Seat),2) AS Average_Fare FROM RIDE;
SELECT MAX(Fare_Per_Seat) AS Highest_Fare          FROM RIDE;

-- Q5. GROUP BY: bookings (confirmed/completed) and seats per ride
SELECT  Ride_ID,
        COUNT(*)          AS Total_Bookings,
        SUM(Seats_Booked) AS Total_Seats_Booked
FROM    BOOKING
WHERE   Booking_Status <> 'Cancelled'
GROUP BY Ride_ID
ORDER BY Ride_ID;

-- Q6. GROUP BY: total payment collected per payment mode
SELECT  Payment_Mode,
        COUNT(*)    AS Payments,
        SUM(Amount) AS Total_Amount
FROM    PAYMENT
WHERE   Payment_Status = 'Paid'
GROUP BY Payment_Mode
ORDER BY Total_Amount DESC;

-- Q7. GROUP BY + HAVING: average rating per driver, only drivers with avg >= 4
SELECT  s.Student_Name AS Driver,
        COUNT(rt.Rating_ID)    AS Ratings_Received,
        ROUND(AVG(rt.Rating),2) AS Avg_Rating
FROM    RATING rt
JOIN    STUDENT s ON rt.Driver_ID = s.Student_ID
GROUP BY rt.Driver_ID, s.Student_Name
HAVING  AVG(rt.Rating) >= 4
ORDER BY Avg_Rating DESC;

-- Q8. HAVING: rides with more than two bookings
SELECT  Ride_ID, COUNT(*) AS Total_Bookings
FROM    BOOKING
WHERE   Booking_Status <> 'Cancelled'
GROUP BY Ride_ID
HAVING  COUNT(*) > 2;

-- Q9. Subquery: rides with fare above the average fare
SELECT  Ride_ID, Pickup_Location, Drop_Location, Fare_Per_Seat
FROM    vw_ride_details
WHERE   Fare_Per_Seat > (SELECT AVG(Fare_Per_Seat) FROM RIDE);

-- Q10. Subquery: students who have never made a booking
SELECT  Student_ID, Student_Name, Department
FROM    STUDENT
WHERE   Student_ID NOT IN (SELECT Passenger_ID FROM BOOKING);

-- Q11. Subquery: students who have never offered a ride (never drove)
SELECT  Student_ID, Student_Name
FROM    STUDENT
WHERE   Student_ID NOT IN (SELECT Driver_ID FROM RIDE);

-- Q12. Booking history of a passenger (Riddhi, Student_ID = 2)
SELECT  b.Booking_ID, lp.Location_Name AS Pickup, ld.Location_Name AS Destination,
        r.Ride_Date, b.Seats_Booked, p.Amount, p.Payment_Mode, p.Payment_Status, b.Booking_Status
FROM    BOOKING b
JOIN    RIDE r      ON b.Ride_ID   = r.Ride_ID
JOIN    LOCATION lp ON r.Pickup_ID = lp.Location_ID
JOIN    LOCATION ld ON r.Drop_ID   = ld.Location_ID
LEFT JOIN PAYMENT p ON p.Booking_ID = b.Booking_ID
WHERE   b.Passenger_ID = 2
ORDER BY r.Ride_Date;

-- Q13. Passenger list of every scheduled ride (driver's view)
SELECT  r.Ride_ID, d.Student_Name AS Driver, ps.Student_Name AS Passenger,
        b.Seats_Booked, ps.Phone AS Passenger_Phone
FROM    RIDE r
JOIN    STUDENT d   ON r.Driver_ID    = d.Student_ID
JOIN    BOOKING b   ON b.Ride_ID      = r.Ride_ID
JOIN    STUDENT ps  ON b.Passenger_ID = ps.Student_ID
WHERE   r.Ride_Status = 'Scheduled' AND b.Booking_Status = 'Confirmed'
ORDER BY r.Ride_ID;

-- Q14. Earnings of each driver (paid amounts only)
SELECT  d.Student_Name AS Driver, SUM(p.Amount) AS Total_Earnings
FROM    PAYMENT p
JOIN    BOOKING b ON p.Booking_ID = b.Booking_ID
JOIN    RIDE r    ON b.Ride_ID    = r.Ride_ID
JOIN    STUDENT d ON r.Driver_ID  = d.Student_ID
WHERE   p.Payment_Status = 'Paid'
GROUP BY d.Student_ID, d.Student_Name
ORDER BY Total_Earnings DESC;

-- Q15. Pending payments with passenger details
SELECT  p.Payment_ID, s.Student_Name AS Passenger, p.Amount, p.Payment_Mode
FROM    PAYMENT p
JOIN    BOOKING b ON p.Booking_ID   = b.Booking_ID
JOIN    STUDENT s ON b.Passenger_ID = s.Student_ID
WHERE   p.Payment_Status = 'Pending';

-- Q16. Vehicles of each student (LEFT JOIN shows students without vehicles too)
SELECT  s.Student_Name, v.Vehicle_Number, v.Vehicle_Model, v.Seating_Capacity
FROM    STUDENT s
LEFT JOIN VEHICLE v ON v.Student_ID = s.Student_ID
ORDER BY s.Student_ID;

-- Q17. Seat occupancy per scheduled ride
SELECT  r.Ride_ID, v.Seating_Capacity,
        r.Available_Seats,
        (SELECT COALESCE(SUM(b.Seats_Booked),0) FROM BOOKING b
          WHERE b.Ride_ID = r.Ride_ID AND b.Booking_Status = 'Confirmed') AS Seats_Booked
FROM    RIDE r JOIN VEHICLE v ON r.Vehicle_ID = v.Vehicle_ID
WHERE   r.Ride_Status = 'Scheduled';

-- Q18. Most popular route (pickup -> drop) by number of bookings
SELECT  lp.Location_Name AS Pickup, ld.Location_Name AS Destination,
        COUNT(b.Booking_ID) AS Total_Bookings
FROM    RIDE r
JOIN    LOCATION lp ON r.Pickup_ID = lp.Location_ID
JOIN    LOCATION ld ON r.Drop_ID   = ld.Location_ID
JOIN    BOOKING b   ON b.Ride_ID   = r.Ride_ID
WHERE   b.Booking_Status <> 'Cancelled'
GROUP BY r.Pickup_ID, r.Drop_ID, lp.Location_Name, ld.Location_Name
ORDER BY Total_Bookings DESC
LIMIT 3;


-- =====================================================================
-- PART 6 : DEMONSTRATION OF THE COMPLETE PROCESS
--          (offer ride -> search -> book -> pay -> complete -> rate)
-- =====================================================================

-- Step 1: A student (Neha, ID 6) offers a new ride using her own vehicle (ID 4)
INSERT INTO RIDE (Driver_ID, Vehicle_ID, Pickup_ID, Drop_ID, Ride_Date, Ride_Time, Available_Seats, Fare_Per_Seat)
VALUES (6, 4, 1, 9, '2026-11-28', '09:15:00', 3, 25.00);

-- Step 2: Other students search for it
CALL sp_search_rides('JIIT', 'City Centre', '2026-11-28');

-- Step 3: Aditya (ID 9) books 2 seats using UPI -> booking + payment created, seats reduced
CALL sp_book_ride(LAST_INSERT_ID(), 9, 2, 'UPI');

-- Check seats were reduced (3 -> 1)
SELECT Ride_ID, Available_Seats FROM RIDE ORDER BY Ride_ID DESC LIMIT 1;

-- Step 4: Ride is completed
UPDATE RIDE    SET Ride_Status    = 'Completed' WHERE Ride_Date = '2026-11-28' AND Driver_ID = 6;
UPDATE BOOKING SET Booking_Status = 'Completed'
WHERE  Ride_ID = (SELECT Ride_ID FROM RIDE WHERE Ride_Date = '2026-11-28' AND Driver_ID = 6);

-- Step 5: Passenger rates the driver
INSERT INTO RATING (Ride_ID, Passenger_ID, Driver_ID, Rating, Review)
SELECT Ride_ID, 9, 6, 5, 'Friendly driver, on time'
FROM   RIDE WHERE Ride_Date = '2026-11-28' AND Driver_ID = 6;

SELECT * FROM RATING ORDER BY Rating_ID DESC LIMIT 1;


-- =====================================================================
-- PART 7 : CONSTRAINT / TRIGGER TESTS
--          (each statement below is EXPECTED to fail with an error;
--           run them one at a time to demonstrate the rules)
-- =====================================================================

-- T1. Rating outside 1-5 (CHECK)
-- INSERT INTO RATING (Ride_ID, Passenger_ID, Driver_ID, Rating) VALUES (1, 2, 1, 7);

-- T2. Duplicate email (UNIQUE)
-- INSERT INTO STUDENT (Student_Name, Email, Phone, Department, `Year`)
-- VALUES ('Test User', 'anukriti.pandey@jiit.ac.in', '9999999999', 'CSE', 1);

-- T3. Duplicate vehicle number (UNIQUE)
-- INSERT INTO VEHICLE (Student_ID, Vehicle_Number, Vehicle_Model, Vehicle_Type, Seating_Capacity)
-- VALUES (2, 'UP16AB1234', 'Swift', 'Car', 4);

-- T4. Booking more seats than available (trigger)
-- INSERT INTO BOOKING (Ride_ID, Passenger_ID, Seats_Booked) VALUES (4, 5, 5);

-- T5. Driver booking his own ride (trigger)
-- INSERT INTO BOOKING (Ride_ID, Passenger_ID, Seats_Booked) VALUES (4, 4, 1);

-- T6. Foreign key violation: non-existing driver
-- INSERT INTO RIDE (Driver_ID, Vehicle_ID, Pickup_ID, Drop_ID, Ride_Date, Ride_Time, Available_Seats, Fare_Per_Seat)
-- VALUES (99, 1, 1, 2, '2026-12-01', '09:00:00', 2, 30);

-- T7. Rating a ride that is not completed (trigger)
-- INSERT INTO RATING (Ride_ID, Passenger_ID, Driver_ID, Rating) VALUES (4, 2, 4, 5);

-- T8. Second payment for the same booking (1:1 UNIQUE)
-- INSERT INTO PAYMENT (Booking_ID, Amount, Payment_Mode) VALUES (1, 80, 'Cash');

-- T9. Using someone else's vehicle for a ride (trigger)
-- INSERT INTO RIDE (Driver_ID, Vehicle_ID, Pickup_ID, Drop_ID, Ride_Date, Ride_Time, Available_Seats, Fare_Per_Seat)
-- VALUES (2, 1, 1, 2, '2026-12-01', '09:00:00', 2, 30);

-- T10. Pickup and drop the same (CHECK)
-- INSERT INTO RIDE (Driver_ID, Vehicle_ID, Pickup_ID, Drop_ID, Ride_Date, Ride_Time, Available_Seats, Fare_Per_Seat)
-- VALUES (1, 1, 2, 2, '2026-12-01', '09:00:00', 2, 30);

-- Cancel a booking demo (seats restored automatically):
-- CALL sp_cancel_booking(6);
-- SELECT Ride_ID, Available_Seats FROM RIDE WHERE Ride_ID = 4;

-- =====================  END OF SCRIPT  =====================

