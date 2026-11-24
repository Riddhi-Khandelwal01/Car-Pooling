
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from gui.db import fetch_all, call_proc


class OfferRideScreen:

    def __init__(self, parent, student):
        self.parent = parent
        self.student = student

        self.frame = tk.Frame(parent, bg="#F3F6FB")
        self.frame.pack(fill="both", expand=True)

        self.create_form()
        self.load_vehicles()
        self.load_locations()

    def create_form(self):

        tk.Label(
            self.frame,
            text="Offer a Ride",
            font=("Segoe UI", 24, "bold"),
            bg="#F3F6FB",
            fg="#19345F"
        ).pack(anchor="w", padx=35, pady=(30, 5))

        tk.Label(
            self.frame,
            text="Share your journey with fellow students",
            font=("Segoe UI", 11),
            bg="#F3F6FB",
            fg="#64748B"
        ).pack(anchor="w", padx=35, pady=(0, 20))

        form = tk.Frame(self.frame, bg="white")
        form.pack(fill="x", padx=35, pady=10)

        form.columnconfigure(1, weight=1)

        # Vehicle
        tk.Label(
            form, text="Your Vehicle",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=12)

        self.vehicle_combo = ttk.Combobox(
            form, state="readonly", width=35
        )
        self.vehicle_combo.grid(
            row=0, column=1, sticky="ew", padx=20, pady=12
        )

        # Pickup
        tk.Label(
            form, text="Pickup Location",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).grid(row=1, column=0, sticky="w", padx=20, pady=12)

        self.pickup_combo = ttk.Combobox(
            form, state="readonly", width=35
        )
        self.pickup_combo.grid(
            row=1, column=1, sticky="ew", padx=20, pady=12
        )

        # Drop
        tk.Label(
            form, text="Drop Location",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).grid(row=2, column=0, sticky="w", padx=20, pady=12)

        self.drop_combo = ttk.Combobox(
            form, state="readonly", width=35
        )
        self.drop_combo.grid(
            row=2, column=1, sticky="ew", padx=20, pady=12
        )

        # Date
        tk.Label(
            form, text="Ride Date (YYYY-MM-DD)",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).grid(row=3, column=0, sticky="w", padx=20, pady=12)

        self.date_entry = ttk.Entry(form, width=38)
        self.date_entry.grid(
            row=3, column=1, sticky="ew", padx=20, pady=12
        )
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

        # Time
        tk.Label(
            form, text="Departure Time (HH:MM)",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).grid(row=4, column=0, sticky="w", padx=20, pady=12)

        self.time_entry = ttk.Entry(form, width=38)
        self.time_entry.grid(
            row=4, column=1, sticky="ew", padx=20, pady=12
        )
        self.time_entry.insert(0, "09:00")

        # Seats
        tk.Label(
            form, text="Available Seats",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).grid(row=5, column=0, sticky="w", padx=20, pady=12)

        self.seats_entry = ttk.Entry(form, width=38)
        self.seats_entry.grid(
            row=5, column=1, sticky="ew", padx=20, pady=12
        )

        # Fare
        tk.Label(
            form, text="Fare per Seat (₹)",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).grid(row=6, column=0, sticky="w", padx=20, pady=12)

        self.fare_entry = ttk.Entry(form, width=38)
        self.fare_entry.grid(
            row=6, column=1, sticky="ew", padx=20, pady=12
        )

        # Submit button
        tk.Button(
            form,
            text="Offer Ride",
            font=("Segoe UI", 11, "bold"),
            bg="#2457C5",
            fg="white",
            activebackground="#19345F",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10,
            command=self.submit_ride
        ).grid(row=7, column=0, columnspan=2, pady=25)

    def load_vehicles(self):

        try:
            student_id = self.student["Student_ID"]

            vehicles = fetch_all(
                "SELECT Vehicle_ID, Vehicle_Number, Vehicle_Model, "
                "Seating_Capacity FROM Vehicle WHERE Student_ID = %s",
                (student_id,)
            )

            self.vehicle_data = {}

            vehicle_options = []

            for vehicle in vehicles:
                label = (
                    f'{vehicle["Vehicle_Number"]} - '
                    f'{vehicle["Vehicle_Model"]}'
                )

                vehicle_options.append(label)
                self.vehicle_data[label] = vehicle

            self.vehicle_combo["values"] = vehicle_options

            if vehicle_options:
                self.vehicle_combo.current(0)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load vehicles:\n{e}")

    def load_locations(self):

        try:
            locations = fetch_all(
                "SELECT Location_ID, Location_Name FROM Location"
            )

            self.location_data = {}

            options = []

            for location in locations:
                label = location["Location_Name"]
                options.append(label)
                self.location_data[label] = location["Location_ID"]

            self.pickup_combo["values"] = options
            self.drop_combo["values"] = options

        except Exception as e:
            messagebox.showerror("Error", f"Could not load locations:\n{e}")

    def submit_ride(self):

        vehicle_label = self.vehicle_combo.get()
        pickup = self.pickup_combo.get()
        drop = self.drop_combo.get()
        ride_date = self.date_entry.get().strip()
        ride_time = self.time_entry.get().strip()
        seats = self.seats_entry.get().strip()
        fare = self.fare_entry.get().strip()

        # Required fields
        if not all([vehicle_label, pickup, drop, ride_date,
                    ride_time, seats, fare]):
            messagebox.showwarning(
                "Missing Details",
                "Please fill in all the fields."
            )
            return

        # Different pickup and drop
        if pickup == drop:
            messagebox.showwarning(
                "Invalid Route",
                "Pickup and drop locations must be different."
            )
            return

        # Date validation
        try:
            datetime.strptime(ride_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Invalid Date",
                "Date must be in YYYY-MM-DD format."
            )
            return

        # Time validation
        try:
            datetime.strptime(ride_time, "%H:%M")
        except ValueError:
            messagebox.showerror(
                "Invalid Time",
                "Time must be in HH:MM format (24-hour clock)."
            )
            return

        # Seats validation
        try:
            seats = int(seats)

            capacity = self.vehicle_data[vehicle_label]["Seating_Capacity"]

            if seats <= 0 or seats > capacity:
                messagebox.showerror(
                    "Invalid Seats",
                    f"Seats must be between 1 and {capacity}."
                )
                return

        except ValueError:
            messagebox.showerror(
                "Invalid Seats",
                "Seats must be a whole number."
            )
            return

        # Fare validation
        try:
            fare = float(fare)

            if fare <= 0:
                messagebox.showerror(
                    "Invalid Fare",
                    "Fare must be greater than zero."
                )
                return

        except ValueError:
            messagebox.showerror(
                "Invalid Fare",
                "Please enter a valid numeric fare."
            )
            return

        vehicle_id = self.vehicle_data[vehicle_label]["Vehicle_ID"]
        pickup_id = self.location_data[pickup]
        drop_id = self.location_data[drop]
        driver_id = self.student["Student_ID"]

        # Insert ride using stored procedure
        try:
            call_proc("sp_create_ride", (
                driver_id,
                vehicle_id,
                pickup_id,
                drop_id,
                ride_date,
                ride_time,
                seats,
                fare
            ))

            messagebox.showinfo(
                "Success",
                "Your ride has been offered successfully!"
            )

            self.seats_entry.delete(0, tk.END)
            self.fare_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror(
                "Database Error",
                f"Could not offer ride:\n{e}"
            )
