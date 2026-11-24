import tkinter as tk
from gui.screens.login import LoginScreen

def main():
    root = tk.Tk()
    LoginScreen(root)
    root.mainloop()

if __name__ == "__main__":
    main()