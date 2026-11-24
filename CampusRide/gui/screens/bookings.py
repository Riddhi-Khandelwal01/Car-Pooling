import tkinter as tk
from tkinter import ttk, messagebox
from gui.db import fetch_all


class BookingsScreen:
    def __init__(self, parent, student):
        self.parent = parent
        self.student = student

        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(fill="both", expand=True)

        # Title
        title = tk.Label(
            self.frame,
            text="My Bookings",
            font=("Arial", 20, "bold"),
            bg="white"
        )
        title.pack(pady=(20, 5))

        subtitle = tk.Label(
            self.frame,
            text="View your booked rides and payment details",
            font=("Arial", 11),
            bg="white",
            fg="gray"
        )
        subtitle.pack(pady=(0, 15))

        # Refresh button
        refresh_btn = tk.Button(
            self.frame,
            text="Refresh Bookings",
            command=self.load_bookings,
            bg="#2563eb",
            fg="white",
            font=("Arial", 10, "bold")
        )
        refresh_btn.pack(pady=5)

        # Table container
        table_frame = tk.Frame(self.frame, bg="white")
        table_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Table columns
        columns = (
            "Booking ID",
            "Driver",
            "Vehicle",
            "Pickup",
            "Drop",
            "Ride Date",
            "Seats",
            "Amount",
            "Booking Status",
            "Payment Status"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        # Column headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        self.tree.column("Booking ID", width=80)
        self.tree.column("Driver", width=130)
        self.tree.column("Vehicle", width=140)
        self.tree.column("Pickup", width=150)
        self.tree.column("Drop", width=150)
        self.tree.column("Ride Date", width=100)
        self.tree.column("Seats", width=60)
        self.tree.column("Amount", width=100)
        self.tree.column("Booking Status", width=110)
        self.tree.column("Payment Status", width=110)

        # Vertical scrollbar
        vertical_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
    )

        # Horizontal scrollbar
        horizontal_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview
        )

        self.tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set
    )

        self.tree.pack(side="top", fill="both", expand=True)
        vertical_scrollbar.pack(side="right", fill="y")
        horizontal_scrollbar.pack(side="bottom", fill="x")

        # Load booking data
        self.load_bookings()

    def load_bookings(self):

        # Clear existing table data
        for row in self.tree.get_children():
            self.tree.delete(row)

        query = """
            SELECT
                b.Booking_ID,
                r.Driver_Name,
                CONCAT(r.Vehicle_Model, ' (', r.Vehicle_Number, ')') AS Vehicle,
                r.Pickup_Location,
                r.Drop_Location,
                r.Ride_Date,
                b.Seats_Booked,
                p.Amount,
                b.Booking_Status,
                p.Payment_Status

            FROM Booking b

            JOIN vw_ride_details r
                ON b.Ride_ID = r.Ride_ID

            LEFT JOIN Payment p
                ON b.Booking_ID = p.Booking_ID

            WHERE b.Passenger_ID = %s

            ORDER BY b.Booking_ID DESC
        """

        try:
            bookings = fetch_all(
                query,
                (self.student["Student_ID"],)
            )

            for booking in bookings:
                values = (
                    booking["Booking_ID"],
                    booking["Driver_Name"],
                    booking["Vehicle"],
                    booking["Pickup_Location"],
                    booking["Drop_Location"],
                    booking["Ride_Date"],
                    booking["Seats_Booked"],
                    booking["Amount"],
                    booking["Booking_Status"],
                    booking["Payment_Status"]
                )

                self.tree.insert("", "end", values=values)

            if not bookings:
                messagebox.showinfo(
                    "My Bookings",
                    "You haven't booked any rides yet."
                )

        except Exception as e:
            messagebox.showerror(
                "Database Error",
                f"Could not load bookings:\n{e}"
            )