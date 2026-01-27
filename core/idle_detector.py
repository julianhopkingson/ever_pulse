import ctypes
from ctypes import windll, Structure, c_uint, byref

class LASTINPUTINFO(Structure):
    _fields_ = [("cbSize", c_uint), ("dwTime", c_uint)]

def get_idle_duration():
    """返回自上次用户输入（鼠标/键盘）以来的空闲秒数"""
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    try:
        windll.user32.GetLastInputInfo(byref(lii))    # 获取最后一次输入的 TickCount
        elapsed = windll.kernel32.GetTickCount() - lii.dwTime  # 系统启动后经过的毫秒数减去上次输入时刻
        return elapsed / 1000.0  # 转为秒
    except Exception:
        return 0.0
