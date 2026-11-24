
USE campusride;

DELIMITER $$

-- =============================================
-- 1. REGISTER A NEW STUDENT
-- =============================================
DROP PROCEDURE IF EXISTS sp_register_student$$

CREATE PROCEDURE sp_register_student(
    IN p_name VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_phone VARCHAR(15),
    IN p_department VARCHAR(50),
    IN p_year TINYINT
)
BEGIN
    INSERT INTO STUDENT
        (Student_Name, Email, Phone, Department, `Year`)
    VALUES
        (p_name, p_email, p_phone, p_department, p_year);

    SELECT LAST_INSERT_ID() AS Student_ID,
           'Student registered successfully' AS Message;
END$$


-- =============================================
-- 2. ADD A VEHICLE
-- =============================================
DROP PROCEDURE IF EXISTS sp_add_vehicle$$

CREATE PROCEDURE sp_add_vehicle(
    IN p_student_id INT,
    IN p_vehicle_no VARCHAR(20),
    IN p_model VARCHAR(50),
    IN p_type VARCHAR(20),
    IN p_capacity INT
)
BEGIN
    INSERT INTO VEHICLE
        (Student_ID, Vehicle_Number, Vehicle_Model,
         Vehicle_Type, Seating_Capacity)
    VALUES
        (p_student_id, p_vehicle_no, p_model,
         p_type, p_capacity);

    SELECT LAST_INSERT_ID() AS Vehicle_ID,
           'Vehicle added successfully' AS Message;
END$$


-- =============================================
-- 3. CREATE / OFFER A RIDE
-- =============================================
DROP PROCEDURE IF EXISTS sp_create_ride$$

CREATE PROCEDURE sp_create_ride(
    IN p_driver_id INT,
    IN p_vehicle_id INT,
    IN p_pickup_id INT,
    IN p_drop_id INT,
    IN p_date DATE,
    IN p_time TIME,
    IN p_seats INT,
    IN p_fare DECIMAL(8,2)
)
BEGIN
    INSERT INTO RIDE
        (Driver_ID, Vehicle_ID, Pickup_ID, Drop_ID,
         Ride_Date, Ride_Time, Available_Seats, Fare_Per_Seat)
    VALUES
        (p_driver_id, p_vehicle_id, p_pickup_id, p_drop_id,
         p_date, p_time, p_seats, p_fare);

    SELECT LAST_INSERT_ID() AS Ride_ID,
           'Ride created successfully' AS Message;
END$$


-- =============================================
-- 4. MAKE PAYMENT
-- =============================================
DROP PROCEDURE IF EXISTS sp_make_payment$$

CREATE PROCEDURE sp_make_payment(
    IN p_booking_id INT,
    IN p_payment_mode VARCHAR(10)
)
BEGIN
    DECLARE v_amount DECIMAL(8,2);
    DECLARE v_status VARCHAR(15);
    DECLARE v_count INT DEFAULT 0;

    SELECT COUNT(*)
    INTO v_count
    FROM BOOKING
    WHERE Booking_ID = p_booking_id;

    IF v_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Booking does not exist';
    END IF;

    SELECT b.Seats_Booked * r.Fare_Per_Seat,
           b.Booking_Status
    INTO v_amount, v_status
    FROM BOOKING b
    JOIN RIDE r ON b.Ride_ID = r.Ride_ID
    WHERE b.Booking_ID = p_booking_id;

    IF v_status = 'Cancelled' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot pay for a cancelled booking';
    END IF;

    SELECT COUNT(*)
    INTO v_count
    FROM PAYMENT
    WHERE Booking_ID = p_booking_id;

    IF v_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Payment already exists for this booking';
    END IF;

    INSERT INTO PAYMENT
        (Booking_ID, Amount, Payment_Mode, Payment_Status)
    VALUES
        (p_booking_id, v_amount, p_payment_mode, 'Paid');

    SELECT LAST_INSERT_ID() AS Payment_ID,
           v_amount AS Amount,
           'Payment successful' AS Message;
END$$


-- =============================================
-- 5. ADD A DRIVER RATING
-- =============================================
DROP PROCEDURE IF EXISTS sp_add_rating$$

CREATE PROCEDURE sp_add_rating(
    IN p_ride_id INT,
    IN p_passenger_id INT,
    IN p_rating TINYINT,
    IN p_review VARCHAR(255)
)
BEGIN
    DECLARE v_driver_id INT;
    DECLARE v_ride_status VARCHAR(15);
    DECLARE v_booking_count INT DEFAULT 0;

    SELECT Driver_ID, Ride_Status
    INTO v_driver_id, v_ride_status
    FROM RIDE
    WHERE Ride_ID = p_ride_id;

    IF v_ride_status <> 'Completed' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Only completed rides can be rated';
    END IF;

    SELECT COUNT(*)
    INTO v_booking_count
    FROM BOOKING
    WHERE Ride_ID = p_ride_id
      AND Passenger_ID = p_passenger_id
      AND Booking_Status = 'Completed';

    IF v_booking_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Passenger must have completed this ride';
    END IF;

    INSERT INTO RATING
        (Ride_ID, Passenger_ID, Driver_ID, Rating, Review)
    VALUES
        (p_ride_id, p_passenger_id, v_driver_id,
         p_rating, p_review);

    SELECT LAST_INSERT_ID() AS Rating_ID,
           'Rating submitted successfully' AS Message;
END$$

DELIMITER ;

USE campusride;

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_book_ride$$

CREATE PROCEDURE sp_book_ride(
    IN p_ride_id INT,
    IN p_passenger_id INT,
    IN p_seats INT,
    IN p_mode VARCHAR(10)
)
BEGIN
    DECLARE v_fare DECIMAL(8,2);
    DECLARE v_booking_id INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Lock the ride row until transaction completes
    SELECT Fare_Per_Seat
    INTO v_fare
    FROM RIDE
    WHERE Ride_ID = p_ride_id
    FOR UPDATE;

    -- Insert booking
    INSERT INTO BOOKING
        (Ride_ID, Passenger_ID, Seats_Booked)
    VALUES
        (p_ride_id, p_passenger_id, p_seats);

    SET v_booking_id = LAST_INSERT_ID();

    -- Insert payment
    INSERT INTO PAYMENT
        (Booking_ID, Amount, Payment_Mode, Payment_Status)
    VALUES
        (v_booking_id, v_fare * p_seats, p_mode,
         CASE
             WHEN p_mode = 'Cash' THEN 'Pending'
             ELSE 'Paid'
         END);

    COMMIT;

    SELECT
        v_booking_id AS Booking_ID,
        v_fare * p_seats AS Amount_To_Pay,
        'Booking successful' AS Message;

END$$

DELIMITER ;

