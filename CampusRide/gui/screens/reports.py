
import tkinter as tk
from tkinter import ttk, messagebox
from gui.db import fetch_all


class ReportsScreen:
    def __init__(self, parent, student):
        self.parent = parent
        self.student = student

        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(fill="both", expand=True)

        # Title
        title = tk.Label(
            self.frame,
            text="CampusRide Reports",
            font=("Segoe UI", 22, "bold"),
            bg="white",
            fg="#19345F"
        )
        title.pack(pady=(30, 10))

        # Subtitle
        subtitle = tk.Label(
            self.frame,
            text="Database insights and ride statistics",
            font=("Segoe UI", 11),
            bg="white",
            fg="#64748B"
        )
        subtitle.pack(pady=5)

        # Load report data
        data = self.load_report_data()

        # Summary Cards Container
        cards_frame = tk.Frame(self.frame, bg="white")
        cards_frame.pack(fill="x", padx=35, pady=25)

        cards = [
            ("Total Rides", data["total_rides"], "#DCEBFF"),
            ("Total Bookings", data["total_bookings"], "#DDF3E4"),
            ("Completed Rides", data["completed_rides"], "#FFF0DA"),
            ("Cancelled Bookings", data["cancelled_bookings"], "#FCE1E1")
        ]

        for title, value, color in cards:
            card = tk.Frame(
                cards_frame,
                bg=color,
                padx=20,
                pady=20,
                highlightthickness=1,
                highlightbackground="#E2E8F0"
            )
            card.pack(side="left", fill="both", expand=True, padx=8)

            tk.Label(
                card,
                text=title,
                font=("Segoe UI", 10, "bold"),
                bg=color,
                fg="#19345F"
            ).pack()

            tk.Label(
                card,
                text=value,
                font=("Segoe UI", 24, "bold"),
                bg=color,
                fg="#19345F"
            ).pack(pady=(8, 0))

    def load_report_data(self):
        queries = {
            "total_rides": "SELECT COUNT(*) AS total FROM Ride",
            "total_bookings": "SELECT COUNT(*) AS total FROM Booking",
            "completed_rides": """
                SELECT COUNT(*) AS total
                FROM Ride
                WHERE Ride_Status = 'Completed'
            """,
            "cancelled_bookings": """
                SELECT COUNT(*) AS total
                FROM Booking
                WHERE Booking_Status = 'Cancelled'
            """
        }

        data = {}

        for key, query in queries.items():
            result = fetch_all(query)
            data[key] = result[0]["total"] if result else 0

        return data
