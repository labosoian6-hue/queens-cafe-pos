"""
app.py - Entry point for CAFE POS System
Compatible: Windows 10 (Build 14393+), 2 GB RAM, touch screen
"""
import tkinter as tk
import sys, os

sys.path.insert(0, os.path.dirname(__file__))

# Enable DPI awareness so UI is sharp on all screens (Windows 8.1+)
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

import database
import pos as pos_module

SCREENS = {
    "login":    pos_module.LoginScreen,
    "pos":      pos_module.POSScreen,
    "menu":     pos_module.MenuManagementScreen,
    "tables":   pos_module.TableManagementScreen,
    "orders":   pos_module.OrderHistoryScreen,
    "reports":  pos_module.ReportsScreen,
    "staff":    pos_module.StaffManagementScreen,
    "settings": pos_module.SettingsScreen,
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        database.initialize_db()
        pos_module._style()

        cafe_name = database.get_setting("cafe_name", "CAFE POS")
        self.title(cafe_name)
        self.configure(bg="#1a1a2e")

        # Fullscreen kiosk mode
        self.attributes("-fullscreen", True)
        self.resizable(False, False)
        self.overrideredirect(True)   # Remove title bar and window chrome

        # Block Alt+F4, Alt+Tab, Win key attempts
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        self.bind("<Alt-F4>", lambda e: "break")
        self.bind("<Alt-Tab>", lambda e: "break")
        self.bind("<Super_L>", lambda e: "break")
        self.bind("<Super_R>", lambda e: "break")
        self.lift()
        self.focus_force()

        self.current_frame = None
        self.show_screen("login")

    def show_screen(self, name, **kwargs):
        if self.current_frame:
            self.current_frame.destroy()

        cls = SCREENS.get(name)
        if cls:
            self.current_frame = cls(self, self, **kwargs)
        else:
            import tkinter.messagebox as mb
            mb.showerror("Error", f"Unknown screen: {name}")

    def _exit_app(self):
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
