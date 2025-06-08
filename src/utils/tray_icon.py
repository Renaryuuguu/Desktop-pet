from PIL import Image
import pystray
import threading
import os

class TrayIconManager:
    def __init__(self, stop_event, icon_path):
        self.stop_event = stop_event
        self.icon_path = icon_path
        self.tray_icon = None
        self.thread = None

    def create_tray_icon(self):
        # Load the icon image
        icon_image = Image.open(self.icon_path)
        
        # Create a function to handle the exit action
        def exit_action(icon, item):
            self.stop_event.set()
            icon.stop()
        
        # Create the menu
        menu = pystray.Menu(
            pystray.MenuItem("退出", exit_action)
        )
        
        # Create and run the icon
        self.tray_icon = pystray.Icon("desktop_pet", icon_image, "Desktop Pet", menu)
        self.tray_icon.run()

    def start(self):
        # Start the tray icon in a separate thread
        self.thread = threading.Thread(target=self.create_tray_icon, daemon=True)
        self.thread.start()
        
    def stop(self):
        if self.tray_icon:
            self.tray_icon.stop()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)