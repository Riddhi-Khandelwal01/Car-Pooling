import tkinter as tk
from tkinter import ttk, messagebox

from gui.db import fetch_all, call_proc


class VehiclesScreen:

    def __init__(self, parent, student):
        self.parent = parent
        self.student = student

        self.frame = tk.Frame(parent, bg="#F3F6FB")
        self.frame.pack(fill="both", expand=True)

        self.setup_ui()
        self.refresh_vehicles()

    def setup_ui(self):

        # Page heading
        tk.Label(
            self.frame,
            text="My Vehicles",
            font=("Segoe UI", 24, "bold"),
            bg="#F3F6FB",
            fg="#19345F"
        ).pack(anchor="w", padx=30, pady=(25, 5))

        tk.Label(
            self.frame,
            text="Add and manage your registered vehicles",
            font=("Segoe UI", 11),
            bg="#F3F6FB",
            fg="#64748B"
        ).pack(anchor="w", padx=30, pady=(0, 20))

        # Add vehicle form
        form = tk.Frame(
            self.frame,
            bg="white",
            highlightbackground="#E2E8F0",
            highlightthickness=1
        )
        form.pack(fill="x", padx=30, pady=5)

        tk.Label(
            form,
            text="Add New Vehicle",
            font=("Segoe UI", 15, "bold"),
            bg="white",
            fg="#19345F"
        ).grid(row=0, column=0, columnspan=4,
                sticky="w", padx=20, pady=(15, 10))

        # Vehicle number
        tk.Label(
            form,
            text="Vehicle Number",
            bg="white"
        ).grid(row=1, column=0, sticky="w", padx=20, pady=5)

        self.number_entry = ttk.Entry(form, width=22)
        self.number_entry.grid(row=2, column=0, padx=20, pady=(0, 15))

        # Model
        tk.Label(
            form,
            text="Vehicle Model",
            bg="white"
        ).grid(row=1, column=1, sticky="w", padx=10, pady=5)

        self.model_entry = ttk.Entry(form, width=22)
        self.model_entry.grid(row=2, column=1, padx=10, pady=(0, 15))

        # Vehicle type
        tk.Label(
            form,
            text="Vehicle Type",
            bg="white"
        ).grid(row=1, column=2, sticky="w", padx=10, pady=5)

        self.type_combo = ttk.Combobox(
            form,
            values=["Car", "Bike", "Scooter", "Other"],
            state="readonly",
            width=19
        )
        self.type_combo.grid(row=2, column=2, padx=10, pady=(0, 15))
        self.type_combo.set("Car")

        # Capacity
        tk.Label(
            form,
            text="Seating Capacity",
            bg="white"
        ).grid(row=1, column=3, sticky="w", padx=10, pady=5)

        self.capacity_entry = ttk.Entry(form, width=15)
        self.capacity_entry.grid(row=2, column=3, padx=10, pady=(0, 15))

        # Add button
        tk.Button(
            form,
            text="Add Vehicle",
            font=("Segoe UI", 10, "bold"),
            bg="#2457C5",
            fg="white",
            activebackground="#1945A3",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.add_vehicle
        ).grid(row=3, column=0, columnspan=4,
               padx=20, pady=(0, 18), sticky="ew")

        # Table heading + refresh
        table_header = tk.Frame(self.frame, bg="#F3F6FB")
        table_header.pack(fill="x", padx=30, pady=(25, 10))

        tk.Label(
            table_header,
            text="Registered Vehicles",
            font=("Segoe UI", 15, "bold"),
            bg="#F3F6FB",
            fg="#19345F"
        ).pack(side="left")

        tk.Button(
            table_header,
            text="Refresh",
            command=self.refresh_vehicles,
            cursor="hand2"
        ).pack(side="right")

        # Table container
        table_frame = tk.Frame(self.frame, bg="white")
        table_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        columns = (
            "Vehicle_ID",
            "Vehicle_Number",
            "Vehicle_Model",
            "Vehicle_Type",
            "Seating_Capacity"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "Vehicle_ID": "ID",
            "Vehicle_Number": "Vehicle Number",
            "Vehicle_Model": "Model",
            "Vehicle_Type": "Type",
            "Seating_Capacity": "Capacity"
        }

        widths = {
            "Vehicle_ID": 60,
            "Vehicle_Number": 150,
            "Vehicle_Model": 150,
            "Vehicle_Type": 120,
            "Seating_Capacity": 100
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def add_vehicle(self):

        vehicle_number = self.number_entry.get().strip().upper()
        model = self.model_entry.get().strip()
        vehicle_type = self.type_combo.get()
        capacity_text = self.capacity_entry.get().strip()

        # Empty field validation
        if not all([vehicle_number, model, vehicle_type, capacity_text]):
            messagebox.showwarning(
                "Missing Information",
                "Please fill in all vehicle details."
            )
            return

        # Capacity validation
        try:
            capacity = int(capacity_text)

            if capacity <= 0:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "Invalid Capacity",
                "Seating capacity must be a positive whole number."
            )
            return

        student_id = self.student["Student_ID"]

        try:
            call_proc(
                "sp_add_vehicle",
                (
                    student_id,
                    vehicle_number,
                    model,
                    vehicle_type,
                    capacity
                )
            )

            messagebox.showinfo(
                "Success",
                "Vehicle added successfully!"
            )

            # Clear fields
            self.number_entry.delete(0, tk.END)
            self.model_entry.delete(0, tk.END)
            self.type_combo.set("Car")
            self.capacity_entry.delete(0, tk.END)

            self.refresh_vehicles()

        except Exception as e:
            messagebox.showerror(
                "Vehicle Registration Failed",
                str(e)
            )

    def refresh_vehicles(self):

        # Clear existing table rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        student_id = self.student["Student_ID"]

        try:
            vehicles = fetch_all(
                "SELECT Vehicle_ID, Vehicle_Number, Vehicle_Model, "
                "Vehicle_Type, Seating_Capacity "
                "FROM Vehicle WHERE Student_ID = %s",
                (student_id,)
            )

            for vehicle in vehicles:
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        vehicle["Vehicle_ID"],
                        vehicle["Vehicle_Number"],
                        vehicle["Vehicle_Model"],
                        vehicle["Vehicle_Type"],
                        vehicle["Seating_Capacity"]
                    )
                )

        except Exception as e:
            messagebox.showerror(
                "Loading Vehicles Failed",
                str(e)
            )