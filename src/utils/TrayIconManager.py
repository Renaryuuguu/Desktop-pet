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
        # 加载图标图像
        icon_image = Image.open(self.icon_path)
        
        # 创建处理退出操作的函数
        def exit_action(icon, item):
            self.stop_event.set()
            icon.stop()
        
        # 创建菜单
        menu = pystray.Menu(
            pystray.MenuItem("退出", exit_action)
        )
        
        # 创建并运行托盘图标
        self.tray_icon = pystray.Icon("desktop_pet", icon_image, "桌面宠物", menu)
        self.tray_icon.run()

    def start(self):
        # 在单独的线程中启动托盘图标
        self.thread = threading.Thread(target=self.create_tray_icon, daemon=True)
        self.thread.start()
        
    def stop(self):
        # 停止托盘图标
        if self.tray_icon:
            self.tray_icon.stop()
        # 如果线程仍在运行，则等待其结束
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)