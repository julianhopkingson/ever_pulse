import ctypes
from ctypes import windll, Structure, c_long, byref
import time

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def get_mouse_position():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return pt.x, pt.y

def set_mouse_position(x, y, duration=0.0):
    if duration > 0:
        # 平滑移动
        orig_x, orig_y = get_mouse_position()
        steps = int(duration * 100)  # 根据持续时间计算步数  (e.g. 0.1s -> 10 steps)

        if steps > 0:
            x_step = (x - orig_x) / steps
            y_step = (y - orig_y) / steps

            for i in range(steps):
                new_x = int(orig_x + (x_step * (i+1)))
                new_y = int(orig_y + (y_step * (i+1)))
                windll.user32.SetCursorPos(new_x, new_y)
                time.sleep(duration / steps)
    else:
        # 直接移动
        windll.user32.SetCursorPos(x, y)

def move_relative(dx, dy, duration=0.0):
    """
    相对当前位置移动
    """
    x, y = get_mouse_position()
    set_mouse_position(x + dx, y + dy, duration)
