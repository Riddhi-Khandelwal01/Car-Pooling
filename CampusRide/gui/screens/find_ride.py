
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from gui.db import fetch_all, call_proc


class FindRideScreen:
    def __init__(self, parent, student):
        self.parent = parent
        self.student = student

        self.create_layout()
        self.load_locations()

    def create_layout(self):
        # Main container
        self.frame = tk.Frame(self.parent, bg="#f4f6f9")
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Heading
        tk.Label(
            self.frame,
            text="Find a Ride",
            font=("Segoe UI", 22, "bold"),
            bg="#f4f6f9",
            fg="#172554"
        ).pack(anchor="w")

        tk.Label(
            self.frame,
            text="Search for available rides to your destination.",
            font=("Segoe UI", 10),
            bg="#f4f6f9",
            fg="#64748b"
        ).pack(anchor="w", pady=(2, 20))

        # Search form
        search_frame = tk.LabelFrame(
            self.frame,
            text="Search Rides",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        search_frame.pack(fill="x", pady=(0, 20))

        # Pickup
        tk.Label(
            search_frame,
            text="Pickup Location",
            bg="white",
            font=("Segoe UI", 10)
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.pickup_combo = ttk.Combobox(
            search_frame,
            width=28,
            state="readonly"
        )
        self.pickup_combo.grid(row=1, column=0, padx=5, pady=5)

        # Drop
        tk.Label(
            search_frame,
            text="Drop Location",
            bg="white",
            font=("Segoe UI", 10)
        ).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        self.drop_combo = ttk.Combobox(
            search_frame,
            width=28,
            state="readonly"
        )
        self.drop_combo.grid(row=1, column=1, padx=5, pady=5)

        # Date
        tk.Label(
            search_frame,
            text="Ride Date (YYYY-MM-DD)",
            bg="white",
            font=("Segoe UI", 10)
        ).grid(row=0, column=2, sticky="w", padx=5, pady=5)

        self.date_entry = ttk.Entry(search_frame, width=20)
        self.date_entry.grid(row=1, column=2, padx=5, pady=5)

        # Search button
        ttk.Button(
            search_frame,
            text="Search Rides",
            command=self.search_rides
        ).grid(row=1, column=3, padx=15, pady=5)

        # Results heading
        tk.Label(
            self.frame,
            text="Available Rides",
            font=("Segoe UI", 14, "bold"),
            bg="#f4f6f9",
            fg="#172554"
        ).pack(anchor="w", pady=(0, 10))

        # Book selected ride button
        ttk.Button(
            self.frame,
            text="Book Selected Ride",
            command=self.book_selected_ride
        ).pack(anchor="e", pady=10)

        # Table frame
        table_frame = tk.Frame(self.frame, bg="white")
        table_frame.pack(fill="both", expand=True)

        columns = (
            "ride_id", "driver", "vehicle", "pickup", "drop",
            "date", "time", "seats", "fare"
        )

        self.ride_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "ride_id": "Ride ID",
            "driver": "Driver",
            "vehicle": "Vehicle",
            "pickup": "Pickup",
            "drop": "Drop",
            "date": "Date",
            "time": "Time",
            "seats": "Seats",
            "fare": "Fare/Seat"
        }

        widths = {
            "ride_id": 65,
            "driver": 130,
            "vehicle": 160,
            "pickup": 170,
            "drop": 170,
            "date": 100,
            "time": 90,
            "seats": 70,
            "fare": 90
        }

        for col in columns:
            self.ride_table.heading(col, text=headings[col])
            self.ride_table.column(
                col,
                width=widths[col],
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.ride_table.yview
        )

        self.ride_table.configure(yscrollcommand=scrollbar.set)

        self.ride_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Result message
        self.result_label = tk.Label(
            self.frame,
            text="Select locations and date to search for rides.",
            font=("Segoe UI", 10),
            bg="#f4f6f9",
            fg="#64748b"
        )
        self.result_label.pack(anchor="w", pady=10)

    def load_locations(self):
        try:
            locations = fetch_all(
                "SELECT Location_Name FROM Location ORDER BY Location_ID"
            )

            location_names = [row["Location_Name"] for row in locations]

            self.pickup_combo["values"] = location_names
            self.drop_combo["values"] = location_names

        except Exception as e:
            messagebox.showerror(
                "Database Error",
                f"Could not load locations.\n\n{e}"
            )

    def search_rides(self):
        pickup = self.pickup_combo.get()
        drop = self.drop_combo.get()
        ride_date = self.date_entry.get().strip()

        # Validate location selections
        if not pickup or not drop:
            messagebox.showwarning(
                "Missing Locations",
                "Please select both pickup and drop locations."
            )
            return

        if pickup == drop:
            messagebox.showwarning(
                "Invalid Route",
                "Pickup and drop locations cannot be the same."
            )
            return

        # Validate date format
        try:
            datetime.strptime(ride_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning(
                "Invalid Date",
                "Please enter the date in YYYY-MM-DD format.\n"
                "Example: 2026-11-25"
            )
            return

        # Clear previous search results
        for item in self.ride_table.get_children():
            self.ride_table.delete(item)

        try:
            # Call the MySQL stored procedure
            _, results = call_proc(
                "sp_search_rides",
                (pickup, drop, ride_date)
            )

            rides = results[0] if results else []

            # Insert rides into the table
            for ride in rides:
                self.ride_table.insert(
                    "",
                    "end",
                    values=(
                        ride[0],                         # Ride ID
                        ride[1],                         # Driver Name
                        f"{ride[3]} ({ride[4]})",         # Vehicle
                        ride[5],                         # Pickup
                        ride[6],                         # Drop
                        ride[7],                         # Date
                        str(ride[8])[:5],                # Time
                        ride[9],                          # Seats
                        f"₹{ride[10]:.2f}"               # Fare
                    )
                )

            if rides:
                self.result_label.config(
                    text=f"{len(rides)} ride(s) found.",
                    fg="#15803d"
                )
            else:
                self.result_label.config(
                    text="No rides found for the selected route and date.",
                    fg="#dc2626"
                )

        except Exception as e:
            messagebox.showerror(
                "Search Error",
                f"Could not search for rides.\n\n{e}"
            )
            self.result_label.config(
                text="Search failed.",
                fg="#dc2626"
            )
  
    def book_selected_ride(self):
        selected = self.ride_table.selection()

        if not selected:
            messagebox.showwarning(
                "No Ride Selected",
                "Please select a ride from the table first."
            )
            return

        # Get data from selected row
        ride_values = self.ride_table.item(selected[0], "values")

        ride_id = ride_values[0]
        driver_name = ride_values[1]
        vehicle = ride_values[2]
        pickup = ride_values[3]
        drop_location = ride_values[4]
        ride_date = ride_values[5]
        ride_time = ride_values[6]
        available_seats = int(ride_values[7])
        fare_text = str(ride_values[8]).replace("₹", "").strip()
        fare = float(fare_text)

        # Booking window
        booking_window = tk.Toplevel(self.parent)
        booking_window.title("Book Ride")
        booking_window.geometry("420x500")
        booking_window.resizable(False, False)
        booking_window.configure(bg="white")
        booking_window.grab_set()

        tk.Label(
            booking_window,
            text="Confirm Your Booking",
            font=("Segoe UI", 18, "bold"),
            bg="white",
            fg="#172554"
        ).pack(pady=(20, 15))

        # Ride details
        details = (
            f"Ride ID: {ride_id}\n"
            f"Driver: {driver_name}\n"
            f"Vehicle: {vehicle}\n"
            f"Route: {pickup} → {drop_location}\n"
            f"Date: {ride_date}\n"
            f"Time: {ride_time}\n"
            f"Available seats: {available_seats}\n"
            f"Fare per seat: ₹{fare:.2f}"
        )

        tk.Label(
            booking_window,
            text=details,
            font=("Segoe UI", 10),
            bg="white",
            justify="left"
        ).pack(anchor="w", padx=25, pady=10)

        # Seat selection
        tk.Label(
            booking_window,
            text="Number of Seats",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).pack(pady=(10, 5))

        seat_var = tk.StringVar(value="1")

        seat_combo = ttk.Combobox(
            booking_window,
            textvariable=seat_var,
            state="readonly",
            width=10,
            values=tuple(str(i) for i in range(1, available_seats + 1))
        )
        seat_combo.pack()

        # Payment mode
        tk.Label(
            booking_window,
            text="Payment Mode",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).pack(pady=(12, 5))

        payment_var = tk.StringVar(value="Cash")

        payment_combo = ttk.Combobox(
            booking_window,
            textvariable=payment_var,
            state="readonly",
            width=15,
            values=("Cash", "Online")
        )
        payment_combo.pack()

        # Total fare
        total_label = tk.Label(
            booking_window,
            text=f"Total: ₹{fare:.2f}",
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#15803d"
        )
        total_label.pack(pady=15)

        def update_total(event=None):
            seats = int(seat_var.get())
            total = seats * fare
            total_label.config(text=f"Total: ₹{total:.2f}")

        seat_combo.bind("<<ComboboxSelected>>", update_total)


        def confirm_booking():
            print("LOGGED-IN STUDENT:", self.student)
            seats = int(seat_var.get())
            mode = payment_var.get()

            try:
                _, result_sets = call_proc(
                    "sp_book_ride",
                    (
                        int(ride_id),
                        int(self.student["Student_ID"]),
                        seats,
                        mode
                    )
                )

                booking_result = (
                    result_sets[0][0]
                    if result_sets and result_sets[0]
                    else None
                )

                booking_id = booking_result[0] if booking_result else "N/A"
                amount = booking_result[1] if booking_result else seats * fare

                payment_status = "Pending" if mode == "Cash" else "Paid"

                messagebox.showinfo(
                    "Booking Successful",
                    f"Your ride has been booked successfully!\n\n"
                    f"Booking ID: {booking_id}\n"
                    f"Seats Booked: {seats}\n"
                    f"Total Amount: ₹{amount:.2f}\n"
                    f"Payment Mode: {mode}\n"
                    f"Payment Status: {payment_status}"
                )

                booking_window.destroy()
                self.search_rides()

            except Exception as e:
                messagebox.showerror(
                    "Booking Failed",
                    f"Could not book the ride.\n\n{e}"
                )

        # Buttons frame
        button_frame = tk.Frame(booking_window, bg="white")
        button_frame.pack(pady=10)

        # Confirm Booking button
        tk.Button(
            button_frame,
            text="Confirm Booking",
            command=confirm_booking,
            bg="#2563EB",
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=8,
            cursor="hand2"
        ).pack(side="left", padx=8)

        # Cancel button
        tk.Button(
            button_frame,
            text="Cancel",
            command=booking_window.destroy,
            bg="#E5E7EB",
            fg="#1F2937",
            font=("Segoe UI", 10),
            padx=12,
            pady=8,
            cursor="hand2"
        ).pack(side="left", padx=8)

           
        # Buttons
        button_frame = tk.Frame(booking_window, bg="white")
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Confirm Booking",
            command=confirm_booking
        ).pack(side="left", padx=8)

        ttk.Button(
            button_frame,
            text="Cancel",
            command=booking_window.destroy
        ).pack(side="left", padx=8)