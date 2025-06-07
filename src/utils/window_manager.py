import win32gui
import win32con

class WindowManager:
    @staticmethod
    def set_transparent(hwnd):
        styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles | win32con.WS_EX_LAYERED)
        # 设置透明色为纯黑色 (0,0,0)
        win32gui.SetLayeredWindowAttributes(hwnd, 0x000000, 0, win32con.LWA_COLORKEY)

    @staticmethod
    def set_topmost(hwnd, topmost=True):
        flag = win32con.HWND_TOPMOST if topmost else win32con.HWND_NOTOPMOST
        win32gui.SetWindowPos(
            hwnd, flag, 
            0, 0, 0, 0, 
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )
        
    @staticmethod
    def set_always_interactive(hwnd):
        # 设置窗口为始终可交互但不抢占焦点
        styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        new_styles = styles | win32con.WS_EX_NOACTIVATE
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_styles)