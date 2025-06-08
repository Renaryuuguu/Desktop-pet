from PIL import Image
import pystray
import threading
import os
import win32gui

class TrayIconManager:
    def __init__(self, stop_event, icon_path, hwnd=None):
        self.stop_event = stop_event
        self.icon_path = icon_path
        self.tray_icon = None
        self.thread = None
        self.hwnd = hwnd  # Store window handle

    def create_tray_icon(self):
        # Load the icon image
        icon_image = Image.open(self.icon_path)
        
        # Create a function to handle the exit action
        def exit_action(icon, item):
            self.stop_event.set()
            icon.stop()
            
        # Create a function to show the pet window
        def show_pet_action(icon, item):
            if self.hwnd:
                # Bring window to foreground without making it topmost
                win32gui.SetForegroundWindow(self.hwnd)
        
        # Create the menu with new option
        menu = pystray.Menu(
            pystray.MenuItem("显示宠物", show_pet_action),
            pystray.MenuItem("退出", exit_action)
        )
        
        # Create and run the icon
        self.tray_icon = pystray.Icon("desktop_pet", icon_image, "Desktop Pet", menu)
        self.tray_icon.run()

    def update_hwnd(self, hwnd):
        """Update the window handle if it changes"""
        self.hwnd = hwnd

    def start(self):
        # Start the tray icon in a separate thread
        self.thread = threading.Thread(target=self.create_tray_icon, daemon=True)
        self.thread.start()
        
    def stop(self):
        if self.tray_icon:
            self.tray_icon.stop()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)