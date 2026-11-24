import tkinter as tk
from tkinter import ttk, messagebox
from gui.db import fetch_all, connect

class RatingsScreen:

    def __init__(self, parent, student):

        self.parent = parent
        self.student = student

        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(fill="both", expand=True)

        # Title
        tk.Label(
            self.frame,
            text="Ratings & Reviews",
            font=("Segoe UI", 22, "bold"),
            bg="white",
            fg="#19345F"
        ).pack(pady=(30, 10))

        tk.Label(
            self.frame,
            text="Rate your carpooling experience",
            font=("Segoe UI", 11),
            bg="white",
            fg="#64748B"
        ).pack(pady=5)

        # Rating form
        form = tk.Frame(self.frame, bg="white")
        form.pack(fill="x", padx=50, pady=25)

        # Ride selection
        tk.Label(
            form,
            text="Select Completed Ride",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#19345F"
        ).pack(anchor="w", pady=(10, 5))

        self.ride_var = tk.StringVar()

        self.ride_dropdown = ttk.Combobox(
            form,
            textvariable=self.ride_var,
            state="readonly",
            font=("Segoe UI", 10)
        )

        self.ride_dropdown.pack(fill="x", pady=5)
        
        self.ride_map = {}
        self.load_completed_rides()

        # Star rating
        tk.Label(
            form,
            text="Your Rating",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#19345F"
        ).pack(anchor="w", pady=(20, 5))

        self.rating_var = tk.IntVar(value=5)

        stars_frame = tk.Frame(form, bg="white")
        stars_frame.pack(anchor="w")

        for i in range(1, 6):

            tk.Radiobutton(
                stars_frame,
                text=f"{i} ★",
                variable=self.rating_var,
                value=i,
                font=("Segoe UI", 11),
                bg="white",
                fg="#E6A817",
                selectcolor="white"
            ).pack(side="left", padx=8)

        # Review box
        tk.Label(
            form,
            text="Write a Review (Optional)",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#19345F"
        ).pack(anchor="w", pady=(20, 5))

        self.review_text = tk.Text(
            form,
            height=4,
            font=("Segoe UI", 10),
            wrap="word",
            relief="solid",
            bd=1
        )

        self.review_text.pack(fill="x", pady=5)

        # Submit button
        tk.Button(
            form,
            text="Submit Rating",
            font=("Segoe UI", 11, "bold"),
            bg="#19345F",
            fg="white",
            activebackground="#2B4D7E",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=10,
            command=self.submit_rating
        ).pack(pady=25)

    def load_completed_rides(self):
        query = """
            SELECT
                b.Booking_ID,
                b.Ride_ID,
                r.Driver_ID
            FROM Booking b
            JOIN Ride r ON b.Ride_ID = r.Ride_ID
            LEFT JOIN Rating rt
                ON rt.Ride_ID = b.Ride_ID
                AND rt.Passenger_ID = b.Passenger_ID
            WHERE b.Passenger_ID = %s
            AND b.Booking_Status = 'Completed'
            AND r.Ride_Status = 'Completed'
            AND rt.Rating_ID IS NULL
            ORDER BY b.Ride_ID
        """

        try:
            rides = fetch_all(query, (self.student["Student_ID"],))
            
            print("Logged-in student:", self.student)
            print("Completed rides fetched:", rides)

            ride_options = []

            for ride in rides:

                ride_label = (
                    f"Ride #{ride['Ride_ID']} - "
                    f"Driver ID: {ride['Driver_ID']} "
                    f"(Booking #{ride['Booking_ID']})"
                )

                ride_options.append(ride_label)

                self.ride_map[ride_label] = {
                    "Ride_ID": ride["Ride_ID"],
                    "Driver_ID": ride["Driver_ID"],
                    "Booking_ID": ride["Booking_ID"]
                }

            self.ride_dropdown["values"] = ride_options

            if ride_options:
                self.ride_dropdown.current(0)
            else:
                self.ride_var.set("No completed rides available")

        except Exception as e:
            messagebox.showerror(
                "Database Error",
                f"Could not load completed rides:\n{e}"
            )
        
        
    def submit_rating(self):
        selected_ride = self.ride_var.get()

        if not selected_ride or selected_ride not in self.ride_map:
            messagebox.showwarning("Warning", "Please select a completed ride.")
            return

        ride_data = self.ride_map[selected_ride]

        rating_value = self.rating_var.get()
        review_text = self.review_text.get("1.0", "end-1c").strip()

        conn = None
        cursor = None

        try:
            conn = connect()
            cursor = conn.cursor()

            query = """
                INSERT INTO Rating
                (Ride_ID, Passenger_ID, Driver_ID, Rating, Review)
                VALUES (%s, %s, %s, %s, %s)
            """

            values = (
                ride_data["Ride_ID"],
                self.student["Student_ID"],
                ride_data["Driver_ID"],
                rating_value,
                review_text if review_text else None
            )

            cursor.execute(query, values)
            conn.commit()

            messagebox.showinfo(
                "Success",
                "Your rating has been submitted successfully!"
            )

            # Clear review box after successful submission
            self.review_text.delete("1.0", tk.END)

        except Exception as e:
            if conn:
                conn.rollback()

            messagebox.showerror(
                "Rating Error",
                f"Could not submit rating:\n{e}"
            )

        finally:
            if cursor:
                cursor.close()

            if conn:
                conn.close()