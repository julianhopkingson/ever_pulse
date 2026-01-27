
import ctypes
from ctypes import wintypes

class WindowEffect:
    def __init__(self):
        self.dwmapi = ctypes.windll.dwmapi
        
    def set_title_bar_color(self, hwnd, color_hex):
        """
        Set the title bar color of a window.
        
        Args:
            hwnd: Window handle (int) or QWindow.winId()
            color_hex: Color in hex string format (e.g. "#FF0000") or None to reset
        """
        # CONSTANTS
        DWMWA_CAPTION_COLOR = 35
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWMWA_WINDOW_CORNER_PREFERENCE = 33

        if not color_hex:
             # Reset to default
             # Use -1 or default system color logic if needed, 
             # but usually passing the default light/dark color is safer.
             # Here we just return if None passed, caller should pass specific color.
             return

        # 1. Parse Hex to COLORREF (0x00BBGGRR)
        color_hex = color_hex.lstrip('#')
        if len(color_hex) == 6:
            r = int(color_hex[0:2], 16)
            g = int(color_hex[2:4], 16)
            b = int(color_hex[4:6], 16)
            colorref = ctypes.c_int(b << 16 | g << 8 | r)
        else:
            return

        # 2. Set Caption Color
        c_bool = ctypes.c_int
        
        # Determine if it's a dark color (simple heuristic)
        # If color is dark, we likely want light text (which Windows handles auto if we set dark mode correctly)
        is_dark = (r * 0.299 + g * 0.587 + b * 0.114) < 128
        
        # Set Dark Mode preference (changes caption text color to white if dark mode is on)
        use_dark_mode = c_bool(1 if is_dark else 0)
        self.dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(int(hwnd)),
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(use_dark_mode),
            ctypes.sizeof(use_dark_mode)
        )

        # Set the background color of the title bar
        self.dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(int(hwnd)),
            DWMWA_CAPTION_COLOR,
            ctypes.byref(colorref),
            ctypes.sizeof(colorref)
        )

window_effect = WindowEffect()
