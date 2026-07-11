# Taxi Warning Vision - Driver Monitoring System
# Entry point for the application

import customtkinter as ctk
from src.ui_display import MainDashboard

if __name__ == "__main__":
    root = ctk.CTk()
    app = MainDashboard(root)
    root.mainloop()