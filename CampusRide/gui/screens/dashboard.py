import tkinter as tk
from tkinter import ttk
from gui.db import fetch_all

class DashboardScreen:

    def __init__(self, root, student):
        self.root = root
        self.student = student

        # Clear previous screen
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title("CampusRide | Dashboard")
        self.root.geometry("1100x700")
        self.root.configure(bg="#F3F6FB")
        self.root.minsize(900, 600)

        self.setup_styles()
        self.create_layout()
        self.show_page("Dashboard")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Nav.TButton",
            font=("Segoe UI", 11),
            padding=10,
            background="#19345F",
            foreground="white",
            anchor="w"
        )

        style.map(
            "Nav.TButton",
            background=[("active", "#2B4D7E")]
        )

    def create_layout(self):

        # Main layout
        self.main_frame = tk.Frame(
            self.root,
            bg="#F3F6FB"
        )
        self.main_frame.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(
            self.main_frame,
            bg="#19345F",
            width=230
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        tk.Label(
            self.sidebar,
            text="CampusRide",
            font=("Segoe UI", 22, "bold"),
            bg="#19345F",
            fg="white"
        ).pack(pady=(30, 5))

        tk.Label(
            self.sidebar,
            text="STUDENT CARPOOLING",
            font=("Segoe UI", 8, "bold"),
            bg="#19345F",
            fg="#9DB7DF"
        ).pack(pady=(0, 25))

        # Navigation buttons
        nav_items = [
            "Dashboard",
            "My Vehicles",
            "Offer Ride",
            "Find Ride",
            "My Bookings",
            "Ratings",
            "Reports"
        ]

        for item in nav_items:
            ttk.Button(
                self.sidebar,
                text="   " + item,
                style="Nav.TButton",
                command=lambda page=item: self.show_page(page)
            ).pack(fill="x", padx=12, pady=4)

        # Logout button
        ttk.Button(
            self.sidebar,
            text="   Logout",
            style="Nav.TButton",
            command=self.logout
        ).pack(side="bottom", fill="x", padx=12, pady=20)

        # Main content area
        self.content = tk.Frame(
            self.main_frame,
            bg="#F3F6FB"
        )
        self.content.pack(side="right", fill="both", expand=True)

    def show_page(self, page_name):

        # Clear previous content
        for widget in self.content.winfo_children():
            widget.destroy()

        if page_name == "Dashboard":
            self.show_dashboard()

        elif page_name == "My Vehicles":
            from gui.screens.vehicles import VehiclesScreen
            VehiclesScreen(self.content, self.student)

        elif page_name == "Offer Ride":
            from gui.screens.offer_ride import OfferRideScreen
            OfferRideScreen(self.content, self.student)

        elif page_name == "Find Ride":
            from gui.screens.find_ride import FindRideScreen
            FindRideScreen(self.content, self.student)

        elif page_name == "My Bookings":
            from gui.screens.bookings import BookingsScreen
            BookingsScreen(self.content, self.student)

        elif page_name == "Ratings":
            from gui.screens.ratings import RatingsScreen
            RatingsScreen(self.content, self.student)

        elif page_name == "Reports":
            from gui.screens.reports import ReportsScreen
            ReportsScreen(self.content, self.student)

        else:
            self.show_placeholder(page_name)    

    def show_dashboard(self):

        name = self.student.get("Name", "Student")
        # Fetch student's vehicle count
        vehicle_data = fetch_all(
            "SELECT COUNT(*) AS total FROM Vehicle WHERE Student_ID = %s",
            (self.student["Student_ID"],)
        )

        vehicle_count = vehicle_data[0]["total"]

        # Fetch currently bookable rides
        ride_data = fetch_all(
            """
            SELECT COUNT(*) AS total
            FROM Ride
            WHERE Ride_Status = 'Scheduled'
            AND Available_Seats > 0
            """
        )

        available_ride_count = ride_data[0]["total"]

        # Fetch student's booking count
        booking_data = fetch_all(
            "SELECT COUNT(*) AS total FROM Booking WHERE Passenger_ID = %s",
            (self.student["Student_ID"],)
        )

        booking_count = booking_data[0]["total"]

        # Header
        header = tk.Frame(
            self.content,
            bg="#F3F6FB"
        )
        header.pack(fill="x", padx=35, pady=(30, 15))

        tk.Label(
            header,
            text=f"Welcome, {name}!",
            font=("Segoe UI", 24, "bold"),
            bg="#F3F6FB",
            fg="#19345F"
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Your campus carpooling dashboard",
            font=("Segoe UI", 11),
            bg="#F3F6FB",
            fg="#64748B"
        ).pack(anchor="w", pady=5)

        # Refresh Dashboard Button
        tk.Button(
            self.content,
            text="↻ Refresh Dashboard",
            font=("Segoe UI", 10, "bold"),
            bg="#19345F",
            fg="white",
            activebackground="#2B4D7E",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=15,
            pady=8,
            command=lambda: self.show_page("Dashboard")
        ).pack(anchor="e", padx=35, pady=(0, 5))
        
        # Summary cards
        cards_frame = tk.Frame(
            self.content,
            bg="#F3F6FB"
        )
        cards_frame.pack(fill="x", padx=35, pady=15)

        cards = [
            ("My Vehicles", vehicle_count, "#DCEBFF"),
            ("My Bookings", booking_count, "#DDF3E4"),
            ("Available Rides", available_ride_count, "#FFF0DA")
        ]

        for title, value, color in cards:

            card = tk.Frame(
                cards_frame,
                bg="white",
                highlightbackground="#E2E8F0",
                highlightthickness=1
            )
            card.pack(side="left", fill="both", expand=True, padx=7)

            tk.Label(
                card,
                text=title,
                font=("Segoe UI", 11),
                bg="white",
                fg="#64748B"
            ).pack(pady=(18, 5))

            tk.Label(
                card,
                text=value,
                font=("Segoe UI", 24, "bold"),
                bg="white",
                fg="#19345F"
            ).pack(pady=(0, 18))

        # Quick actions
        actions_frame = tk.Frame(
            self.content,
            bg="#F3F6FB"
        )
        actions_frame.pack(fill="x", padx=40, pady=25)

        tk.Label(
            actions_frame,
            text="Quick Actions",
            font=("Segoe UI", 17, "bold"),
            bg="#F3F6FB",
            fg="#19345F"
        ).pack(anchor="w", pady=(5, 15))

        actions = [
            ("Offer a Ride", "Offer Ride"),
            ("Find a Ride", "Find Ride"),
            ("My Bookings", "My Bookings"),
            ("Manage Vehicles", "My Vehicles")
        ]

        for label, page in actions:

            btn = tk.Button(
                actions_frame,
                text=label,
                font=("Segoe UI", 11, "bold"),
                bg="white",
                fg="#2457C5",
                activebackground="#E7F0FF",
                relief="flat",
                bd=0,
                padx=20,
                pady=15,
                cursor="hand2",
                command=lambda p=page: self.show_page(p)
            )

            btn.pack(fill="x", pady=5)

        # Bottom note
        tk.Label(
            self.content,
            text="CampusRide • Ride together. Reach together.",
            font=("Segoe UI", 9),
            bg="#F3F6FB",
            fg="#94A3B8"
        ).pack(side="bottom", pady=15)

    def show_placeholder(self, page_name):

        tk.Label(
            self.content,
            text=page_name,
            font=("Segoe UI", 24, "bold"),
            bg="#F3F6FB",
            fg="#19345F"
        ).pack(pady=(60, 15))

        tk.Label(
            self.content,
            text=f"The {page_name} module will be connected in the next stages.",
            font=("Segoe UI", 11),
            bg="#F3F6FB",
            fg="#64748B"
        ).pack(pady=5)

    def logout(self):

        from gui.screens.login import LoginScreen

        LoginScreen(self.root)
        