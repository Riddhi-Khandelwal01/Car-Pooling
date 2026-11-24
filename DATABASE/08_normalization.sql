
/*
=========================================================
              CAMPUSRIDE DATABASE
              NORMALIZATION DOCUMENTATION
=========================================================

Normalization is the process of organizing database tables
to reduce data redundancy and avoid insertion, deletion
and update anomalies.

The CampusRide database contains seven main tables:
STUDENT, VEHICLE, LOCATION, RIDE, BOOKING, PAYMENT, RATING.


---------------------------------------------------------
1. FIRST NORMAL FORM (1NF)
---------------------------------------------------------

A relation is in 1NF when:
- Every column contains atomic (single) values.
- There are no repeating groups.
- Every record can be uniquely identified.

Application in CampusRide:
- Student details are stored in individual columns.
- Vehicle information is stored separately.
- Each booking represents a booking record.
- Each rating is stored as a separate record.

Therefore, the design follows the principles of 1NF.


---------------------------------------------------------
2. SECOND NORMAL FORM (2NF)
---------------------------------------------------------

A relation is in 2NF when:
- It is already in 1NF.
- Every non-key attribute is fully dependent on
  the entire candidate key.
- There are no partial dependencies.

Application in CampusRide:
- Student details depend on Student_ID.
- Vehicle details depend on Vehicle_ID.
- Ride details depend on Ride_ID.
- Booking details depend on Booking_ID.
- Payment details depend on Payment_ID.
- Rating details depend on Rating_ID.

The tables use separate primary keys, avoiding
partial dependencies on their primary keys.


---------------------------------------------------------
3. THIRD NORMAL FORM (3NF)
---------------------------------------------------------

A relation is in 3NF when:
- It is already in 2NF.
- There are no transitive dependencies
  of non-key attributes on candidate keys.

Application in CampusRide:
- Student information is maintained in STUDENT.
- Vehicle information is maintained in VEHICLE.
- Location information is maintained in LOCATION.
- Ride information references the relevant driver,
  vehicle, pickup and drop locations through IDs.
- Booking information references rides and passengers.
- Payment information references bookings.
- Rating information references rides, passengers
  and drivers.

Separating these entities reduces duplication
and update anomalies.


---------------------------------------------------------
4. BOYCE-CODD NORMAL FORM (BCNF)
---------------------------------------------------------

A relation is in BCNF when:
- It is already in 3NF.
- Every determinant is a candidate key.

Application in CampusRide:
- Primary keys uniquely identify records.
- Student Email has a UNIQUE constraint.
- Payment Booking_ID has a UNIQUE constraint.
- Rating has a UNIQUE constraint on
  (Ride_ID, Passenger_ID).
- Booking has a UNIQUE constraint on
  (Ride_ID, Passenger_ID).

These constraints enforce important uniqueness rules.

A complete BCNF claim requires verification of all
functional dependencies in the schema.


---------------------------------------------------------
5. PRIMARY KEY AND FOREIGN KEY RELATIONSHIPS
---------------------------------------------------------

STUDENT:
- Primary Key: Student_ID

VEHICLE:
- Primary Key: Vehicle_ID
- Foreign Key: Student_ID

LOCATION:
- Primary Key: Location_ID

RIDE:
- Primary Key: Ride_ID
- Foreign Keys: Driver_ID, Vehicle_ID,
  Pickup_ID, Drop_ID

BOOKING:
- Primary Key: Booking_ID
- Foreign Keys: Ride_ID, Passenger_ID

PAYMENT:
- Primary Key: Payment_ID
- Foreign Key: Booking_ID

RATING:
- Primary Key: Rating_ID
- Foreign Keys: Ride_ID, Passenger_ID, Driver_ID


---------------------------------------------------------
6. BENEFITS OF NORMALIZATION
---------------------------------------------------------

1. Reduces duplicate data.
2. Improves data consistency.
3. Prevents insertion anomalies.
4. Prevents update anomalies.
5. Prevents deletion anomalies.
6. Maintains referential integrity.
7. Makes database maintenance easier.

=========================================================
                 END OF DOCUMENTATION
=========================================================
*/
