import traceback
import tkinter as tk
from tkinter import ttk, messagebox

from gui.db import fetch_all, call_proc


class LoginScreen:

    def __init__(self, root):
        self.root = root

        # Clear the previous screen
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title("CampusRide | Student Carpooling")
        self.root.geometry("850x550")
        self.root.resizable(False, False)
        self.root.configure(bg="#F2F5FA")

        self.setup_styles()
        self.create_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TEntry",
            padding=8,
            font=("Segoe UI", 11)
        )

        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=10,
            background="#2457C5",
            foreground="white"
        )

        style.map(
            "Primary.TButton",
            background=[("active", "#1945A3")]
        )

    def create_ui(self):

        # Main container
        main_frame = tk.Frame(
            self.root,
            bg="#F2F5FA"
        )
        main_frame.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=30
        )

        # Left branding panel
        left_frame = tk.Frame(
            main_frame,
            bg="#19345F",
            width=320
        )
        left_frame.pack(
            side="left",
            fill="both"
        )
        left_frame.pack_propagate(False)

        tk.Label(
            left_frame,
            text="CampusRide",
            font=("Segoe UI", 27, "bold"),
            bg="#19345F",
            fg="white"
        ).pack(pady=(80, 10))

        tk.Label(
            left_frame,
            text="Ride together.\nReach together.",
            font=("Segoe UI", 17),
            bg="#19345F",
            fg="#D9E7FF",
            justify="center"
        ).pack(pady=15)

        tk.Label(
            left_frame,
            text="A smarter way to travel\naround your campus.",
            font=("Segoe UI", 11),
            bg="#19345F",
            fg="#B7C8E5",
            justify="center"
        ).pack(pady=10)

        # Right panel
        right_frame = tk.Frame(
            main_frame,
            bg="white"
        )
        right_frame.pack(
            side="right",
            fill="both",
            expand=True
        )

        tk.Label(
            right_frame,
            text="Welcome!",
            font=("Segoe UI", 23, "bold"),
            bg="white",
            fg="#19345F"
        ).pack(pady=(45, 5))

        tk.Label(
            right_frame,
            text="Login or create your student account",
            font=("Segoe UI", 10),
            bg="white",
            fg="#64748B"
        ).pack(pady=(0, 20))

        # Login form
        self.login_frame = tk.Frame(
            right_frame,
            bg="white"
        )
        self.login_frame.pack(
            fill="x",
            padx=35
        )

        tk.Label(
            self.login_frame,
            text="College Email",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#334155"
        ).pack(anchor="w")

        self.email_entry = ttk.Entry(
            self.login_frame,
            width=30
        )
        self.email_entry.pack(
            fill="x",
            pady=(5, 15)
        )

        ttk.Button(
            self.login_frame,
            text="Login",
            style="Primary.TButton",
            command=self.login
        ).pack(fill="x", pady=5)

        tk.Label(
            self.login_frame,
            text="New to CampusRide?",
            font=("Segoe UI", 10),
            bg="white",
            fg="#64748B"
        ).pack(pady=(18, 3))

        ttk.Button(
            self.login_frame,
            text="Create Student Account",
            command=self.show_register
        ).pack(fill="x", pady=5)

        self.email_entry.focus()

    def login(self):

        email = self.email_entry.get().strip()

        if not email:
            messagebox.showwarning(
                "Missing Information",
                "Please enter your email."
            )
            return

        try:
            students = fetch_all(
            "SELECT Student_ID, Student_Name AS Name, Email "
            "FROM Student WHERE Email = %s",
            (email,)
            )

            if students:
                student = students[0]

                from gui.screens.dashboard import DashboardScreen

                DashboardScreen(self.root, student)


            else:
                messagebox.showerror(
                    "Login Failed",
                    "Student not found. Please register first."
                )

        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Database Error", str(e))

    def show_register(self):

        register_window = tk.Toplevel(self.root)
        register_window.title("CampusRide | Register")
        register_window.geometry("420x520")
        register_window.configure(bg="white")
        register_window.resizable(False, False)

        tk.Label(
            register_window,
            text="Student Registration",
            font=("Segoe UI", 20, "bold"),
            bg="white",
            fg="#19345F"
        ).pack(pady=(25, 5))

        tk.Label(
            register_window,
            text="Enter your details to get started",
            font=("Segoe UI", 10),
            bg="white",
            fg="#64748B"
        ).pack(pady=(0, 15))

        form = tk.Frame(
            register_window,
            bg="white"
        )
        form.pack(
            fill="x",
            padx=35
        )

        self.reg_entries = {}

        fields = [
            ("Name", "name"),
            ("Email", "email"),
            ("Phone", "phone"),
            ("Department", "department"),
            ("Year", "year")
        ]

        for label_text, key in fields:

            tk.Label(
                form,
                text=label_text,
                font=("Segoe UI", 10, "bold"),
                bg="white",
                fg="#334155"
            ).pack(anchor="w", pady=(5, 0))

            entry = ttk.Entry(form)
            entry.pack(fill="x", pady=(3, 5))

            self.reg_entries[key] = entry

        ttk.Button(
            form,
            text="Register",
            style="Primary.TButton",
            command=lambda: self.register(register_window)
        ).pack(fill="x", pady=(18, 5))

    def register(self, window):

        data = {
            key: entry.get().strip()
            for key, entry in self.reg_entries.items()
        }

        # Check empty fields
        if any(not value for value in data.values()):
            messagebox.showwarning(
                "Missing Information",
                "Please fill in all fields."
            )
            return

        # Simple email validation
        if "@" not in data["email"] or "." not in data["email"]:
            messagebox.showwarning(
                "Invalid Email",
                "Please enter a valid email address."
            )
            return

        # Validate phone digits
        if not data["phone"].isdigit():
            messagebox.showwarning(
                "Invalid Phone",
                "Phone must contain only digits."
            )
            return

        try:
            # Call registration procedure
            call_proc(
                "sp_register_student",
                (
                    data["name"],
                    data["email"],
                    data["phone"],
                    data["department"],
                    data["year"]
                )
            )

            messagebox.showinfo(
                "Registration Successful",
                "Your student account has been created!"
            )

            window.destroy()

        except Exception as e:
            messagebox.showerror(
                "Registration Failed",
                str(e)
            )