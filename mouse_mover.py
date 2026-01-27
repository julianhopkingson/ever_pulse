import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import datetime
import sys
import os
import configparser
import ctypes
from ctypes import windll, Structure, c_long, byref, c_uint


class LASTINPUTINFO(Structure):
    _fields_ = [("cbSize", c_uint), ("dwTime", c_uint)]



def resource_path(relative_path):
    """ 获取资源的绝对路径，兼容 Dev 和 PyInstaller """
    try:
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_idle_duration():
    """返回自上次用户输入（鼠标/键盘）以来的空闲秒数"""
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    windll.user32.GetLastInputInfo(byref(lii))    # 获取最后一次输入的 TickCount
    elapsed = windll.kernel32.GetTickCount() - lii.dwTime  # 系统启动后经过的毫秒数减去上次输入时刻
    return elapsed / 1000.0  # 转为秒


# 使用win32api替代PyAutoGUI
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
        steps = int(duration * 100)  # 根据持续时间计算步数

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


# 多语言支持
class Translations:
    def __init__(self, app_path):
        self.languages = {}
        self.current_language = "中文"  # 默认语言
        self.current_language = "中文"  # 默认语言
        # 修改：从内嵌资源读取 language.ini
        self.language_file_path = resource_path(os.path.join("assets", "language.ini"))

        # 加载语言文件
        self.load_language_file()

    def load_language_file(self):
        """从外部文件加载语言配置"""
        # 如果语言文件不存在，创建默认语言文件
        if not os.path.exists(self.language_file_path):
            self.create_default_language_file()

        # 读取语言文件
        try:
            config = configparser.ConfigParser()
            config.read(self.language_file_path, encoding='utf-8')

            # 获取所有语言部分
            for section in config.sections():
                if section not in self.languages:
                    self.languages[section] = {}

                # 获取此语言的所有键值对
                for key in config[section]:
                    self.languages[section][key] = config[section][key]
        except Exception as e:
            print(f"加载语言文件出错: {str(e)}")

    def create_default_language_file(self):
        """创建默认语言文件"""
        config = configparser.ConfigParser()

        # 中文配置
        config['中文'] = {
            "app_title": "定时鼠标移动工具",
            "settings": "设置",
            "start_time": "开始时间 (HH:MM):",
            "end_time": "结束时间 (HH:MM):",
            "interval": "间隔时间 (秒):",
            "inactivity_time": "空闲时间 (秒):",
            "mouse_movement": "鼠标移动",
            "direction": "移动方向:",
            "pixels": "移动像素:",
            "up": "上",
            "down": "下",
            "left": "左",
            "right": "右",
            "start": "开始",
            "stop": "停止",
            "status_not_running": "状态: 未运行",
            "status_running": "状态: 运行中",
            "status_stopped": "状态: 已停止",
            "status_waiting": "状态: 等待中 - 当前时间不在工作时间范围内",
            "status_last_move": "状态: 运行中 - 上次移动: {}",
            "status_config_loaded": "状态: 已加载配置",
            "status_config_created": "状态: 已创建默认配置文件",
            "status_config_failed": "状态: 配置加载失败 - {}",
            "status_skipped": "状态: 检测到用户活动（空闲{}秒），跳过移动",
            "status_aligning_first_move": "状态: 等待 {} 秒钟，使首次移动的秒钟对齐到 {:02d}",
            "error": "错误",
            "error_hour": "小时必须在0-23之间",
            "error_minute": "分钟必须在0-59之间",
            "error_interval": "间隔时间必须大于0",
            "error_pixels": "像素数必须大于0",
            "error_invalid_value": "请输入有效的数值",
            "error_save_failed": "保存配置失败: {}",
            "language": "语言:",
            "log_title": "日志",
            "auto_close_message": "已到达结束时间，程序将在 {} 秒后自动关闭...",
            "error_time_range": "结束时间不能早于开始时间",
            "status_work_period_ended": "状态: 工作时间已结束，请重新设置时间",
        }

        # 英文配置
        config['English'] = {
            "app_title": "Mouse Movement Timer",
            "settings": "Settings",
            "start_time": "Start Time (HH:MM):",
            "end_time": "End Time (HH:MM):",
            "interval": "Interval (seconds):",
            "inactivity_time": "Idle Time (seconds):",
            "mouse_movement": "Mouse Movement",
            "direction": "Direction:",
            "pixels": "Pixels:",
            "up": "Up",
            "down": "Down",
            "left": "Left",
            "right": "Right",
            "start": "Start",
            "stop": "Stop",
            "status_not_running": "Status: Not Running",
            "status_running": "Status: Running",
            "status_stopped": "Status: Stopped",
            "status_waiting": "Status: Waiting - Current time is outside working hours",
            "status_last_move": "Status: Running - Last moved: {}",
            "status_config_loaded": "Status: Configuration loaded",
            "status_config_created": "Status: Default configuration created",
            "status_config_failed": "Status: Failed to load configuration - {}",
            "status_skipped": "Status: User active (idle {}s), skipping move",
            "status_aligning_first_move": "Status: Waiting {}s to align first move second to {:02d}",
            "error": "Error",
            "error_hour": "Hours must be between 0-23",
            "error_minute": "Minutes must be between 0-59",
            "error_interval": "Interval must be greater than 0",
            "error_pixels": "Pixels must be greater than 0",
            "error_invalid_value": "Please enter valid values",
            "error_save_failed": "Failed to save configuration: {}",
            "language": "Language:",
            "log_title": "Log",
            "auto_close_message": "End time reached. Closing in {} seconds...",
            "error_time_range": "End time cannot be earlier than start time",
            "status_work_period_ended": "Status: Work period has ended, please reset time",
        }

        try:
            with open(self.language_file_path, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
        except Exception as e:
            print(f"创建语言文件出错: {str(e)}")

    def get(self, key):
        """获取当前语言的键值"""
        if self.current_language in self.languages and key in self.languages[self.current_language]:
            return self.languages[self.current_language][key]
        return key

    def set_language(self, language):
        """设置当前语言"""
        if language in self.languages:
            self.current_language = language
            return True
        return False

    def get_direction_values(self):
        """获取当前语言的方向值列表"""
        return [self.get("up"), self.get("down"), self.get("left"), self.get("right")]

    def get_language_values(self):
        """获取所有可用语言列表"""
        return list(self.languages.keys())

    def get_direction_index(self, current_direction):
        """获取方向的索引值"""
        chinese_directions = ["上", "下", "左", "右"]
        english_directions = ["Up", "Down", "Left", "Right"]

        if current_direction in chinese_directions:
            return chinese_directions.index(current_direction)
        elif current_direction in english_directions:
            return english_directions.index(current_direction)
        return 0

    def get_direction_key(self, localized_direction):
        """获取方向的标准键值"""
        chinese_directions = ["上", "下", "左", "右"]
        english_directions = ["Up", "Down", "Left", "Right"]

        if localized_direction in chinese_directions:
            index = chinese_directions.index(localized_direction)
            return chinese_directions[index] if self.current_language == "中文" else english_directions[index]
        elif localized_direction in english_directions:
            index = english_directions.index(localized_direction)
            return chinese_directions[index] if self.current_language == "中文" else english_directions[index]

        return localized_direction


class MouseMoverApp:
    def __init__(self, root):
        self.root = root

        # 配置文件路径
        if getattr(sys, 'frozen', False):
            self.app_path = os.path.dirname(os.path.abspath(sys.executable))
        else:
            self.app_path = os.path.dirname(os.path.abspath(__file__))

        # 修改：用户配置存放在 config 子目录
        self.config_dir = os.path.join(self.app_path, "config")
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        self.config_path = os.path.join(self.config_dir, "config.ini")

        # 初始化翻译系统
        self.translations = Translations(self.app_path)

        # 先加载配置，确定语言设置和窗口位置
        self.pre_load_config()

        # 设置窗口位置
        self.set_window_position()

        # 根据语言设置初始化UI
        self.init_ui()

        # 加载完整配置
        self.load_config()

    def timestamped(self, text):
        """返回带当前时刻前缀的文本，如 “[09:55:56] 文本”"""
        now = datetime.datetime.now().strftime("%H:%M:%S")  # 获取当前时间字符串
        return f"[{now}] {text}"

    def log_message(self, message_text):
        """将带时间戳的消息记录到消息框中"""
        full_message = self.timestamped(message_text) + "\n"
        self.message_box.config(state=tk.NORMAL)  # 允许编辑以插入文本
        self.message_box.insert(tk.END, full_message)
        self.message_box.config(state=tk.DISABLED) # 禁止用户编辑
        self.message_box.see(tk.END)  # 滚动到最新消息

    def pre_load_config(self):
        """从配置文件中预先加载语言设置和窗口位置"""
        config = configparser.ConfigParser()

        self.window_x = None
        self.window_y = None

        if os.path.exists(self.config_path):
            try:
                config.read(self.config_path, encoding='utf-8')
                if 'Settings' in config:
                    # 加载语言设置
                    if 'language' in config['Settings']:
                        language = config['Settings']['language']
                        if language in self.translations.get_language_values():
                            self.translations.set_language(language)

                    # 加载窗口位置
                    if 'window_x' in config['Settings'] and 'window_y' in config['Settings']:
                        try:
                            self.window_x = int(config['Settings']['window_x'])
                            self.window_y = int(config['Settings']['window_y'])
                        except ValueError:
                            self.window_x = None
                            self.window_y = None
            except:
                pass

    def set_window_position(self):
        """设置窗口位置"""
        # 设置窗口初始大小和不可调整属性
        self.window_width = 450
        self.window_height = 620  # 调整窗口高度以容纳消息框
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.resizable(False, False)

        # 如果有保存的窗口位置，则使用它
        if self.window_x is not None and self.window_y is not None:
            # 获取屏幕尺寸，确保窗口不会在屏幕外
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            # 调整x, y确保窗口完全在屏幕内
            if self.window_x < 0:
                self.window_x = 0
            if self.window_y < 0:
                self.window_y = 0
            if self.window_x > screen_width - self.window_width:
                self.window_x = screen_width - self.window_width
            if self.window_y > screen_height - self.window_height:
                self.window_y = screen_height - self.window_height

            # 设置窗口位置
            self.root.geometry(f"{self.window_width}x{self.window_height}+{self.window_x}+{self.window_y}")
        else:
            # 否则居中显示
            self.center_window()

    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def init_ui(self):
        """初始化用户界面"""
        self.root.title(self.translations.get("app_title"))

        # 设置窗口图标
        # 设置窗口图标
        icon_path = resource_path(os.path.join("assets", "mouse-mover.ico")) # 使用 resource_path 获取内嵌或外部资源
        # if os.path.exists(icon_path): # 内嵌资源必然存在（如果打包正确），或者在Dev模式下存在
        try:
            self.root.iconbitmap(icon_path)
        except Exception:
            pass # 如果图标加载失败，不影响程序运行

        # 创建标题标签
        title_label = tk.Label(self.root, text=self.translations.get("app_title"), font=("", 16, "bold"))
        title_label.pack(pady=10)

        # 语言选择框
        language_frame = ttk.Frame(self.root)
        language_frame.pack(padx=20, pady=5, fill="x")

        self.language_label = ttk.Label(language_frame, text=self.translations.get("language"))
        self.language_label.pack(side=tk.LEFT, padx=5)

        self.language_var = tk.StringVar(value=self.translations.current_language)
        self.language_combo = ttk.Combobox(language_frame,
                                           textvariable=self.language_var,
                                           values=self.translations.get_language_values(),
                                           state="readonly",
                                           width=10)
        self.language_combo.pack(side=tk.LEFT, padx=5)
        self.language_combo.bind("<<ComboboxSelected>>", self.on_language_change)

        # 创建一个框架来容纳所有设置
        self.settings_frame = ttk.LabelFrame(self.root, text=self.translations.get("settings"))
        # 修改pack选项：在垂直方向上不扩展 (expand=False)，仅水平填充 (fill="x")
        self.settings_frame.pack(padx=20, pady=10, fill="x", expand=False)

        # 时间设置
        time_frame = ttk.Frame(self.settings_frame)
        time_frame.pack(padx=10, pady=10, fill="x")

        # 开始时间
        self.start_time_label = ttk.Label(time_frame, text=self.translations.get("start_time"))
        self.start_time_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        start_time_frame = ttk.Frame(time_frame)
        start_time_frame.grid(row=0, column=1, padx=5, pady=5)

        self.start_hour = ttk.Spinbox(start_time_frame, from_=0, to=23, width=3, format="%02.0f")
        self.start_hour.insert(0, "09")
        self.start_hour.pack(side=tk.LEFT)

        ttk.Label(start_time_frame, text=":").pack(side=tk.LEFT)
        self.start_minute = ttk.Spinbox(start_time_frame, from_=0, to=59, width=3, format="%02.0f")
        self.start_minute.insert(0, "00")
        self.start_minute.pack(side=tk.LEFT)

        ttk.Label(start_time_frame, text=":").pack(side=tk.LEFT)
        self.start_second = ttk.Spinbox(start_time_frame, from_=0, to=59, width=3, format="%02.0f")
        self.start_second.insert(0, "00")
        self.start_second.pack(side=tk.LEFT)

        # 结束时间
        self.end_time_label = ttk.Label(time_frame, text=self.translations.get("end_time"))
        self.end_time_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        end_time_frame = ttk.Frame(time_frame)
        end_time_frame.grid(row=1, column=1, padx=5, pady=5)

        self.end_hour = ttk.Spinbox(end_time_frame, from_=0, to=23, width=3, format="%02.0f")
        self.end_hour.insert(0, "18")
        self.end_hour.pack(side=tk.LEFT)

        ttk.Label(end_time_frame, text=":").pack(side=tk.LEFT)
        self.end_minute = ttk.Spinbox(end_time_frame, from_=0, to=59, width=3, format="%02.0f")
        self.end_minute.insert(0, "00")
        self.end_minute.pack(side=tk.LEFT)

        ttk.Label(end_time_frame, text=":").pack(side=tk.LEFT)
        self.end_second = ttk.Spinbox(end_time_frame, from_=0, to=59, width=3, format="%02.0f")
        self.end_second.insert(0, "00")
        self.end_second.pack(side=tk.LEFT)

        # 间隔时间
        self.interval_label = ttk.Label(time_frame, text=self.translations.get("interval"))
        self.interval_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.interval = ttk.Spinbox(time_frame, from_=1, to=3600, width=10)
        self.interval.insert(0, "60")
        self.interval.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # 空闲时间阈值
        self.threshold_label = ttk.Label(time_frame, text=self.translations.get("inactivity_time"))
        self.threshold_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.threshold = ttk.Spinbox(time_frame, from_=1, to=600, width=10)  # 最多设 600s
        self.threshold.insert(0, "5")
        self.threshold.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # 鼠标移动设置
        self.mouse_frame = ttk.LabelFrame(self.settings_frame, text=self.translations.get("mouse_movement"))
        self.mouse_frame.pack(padx=10, pady=10, fill="x")

        # 移动方向
        self.direction_label = ttk.Label(self.mouse_frame, text=self.translations.get("direction"))
        self.direction_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.direction = ttk.Combobox(self.mouse_frame,
                                      values=self.translations.get_direction_values(),
                                      state="readonly",
                                      width=10)
        self.direction.current(0)
        self.direction.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # 移动像素
        self.pixels_label = ttk.Label(self.mouse_frame, text=self.translations.get("pixels"))
        self.pixels_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.pixels = ttk.Spinbox(self.mouse_frame, from_=1, to=1000, width=10)
        self.pixels.insert(0, "50")
        self.pixels.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # 控制按钮
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=20, fill="x") # fill="x" 使得按钮框水平填充

        self.start_button = ttk.Button(control_frame,
                                       text=self.translations.get("start"),
                                       command=self.start_automation,
                                       width=15)
        self.start_button.pack(side=tk.LEFT, padx=20, expand=True, fill="x") # 让按钮也参与水平空间的分配

        self.stop_button = ttk.Button(control_frame,
                                      text=self.translations.get("stop"),
                                      command=self.stop_automation,
                                      width=15,
                                      state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT, padx=20, expand=True, fill="x") # 让按钮也参与水平空间的分配

        # 消息日志区域
        self.log_frame_container = ttk.LabelFrame(self.root, text=self.translations.get("log_title"))
        self.log_frame_container.pack(padx=20, pady=10, fill="both", expand=True)

        # 包含文本框和滚动条的内层框架
        self.message_frame = ttk.Frame(self.log_frame_container)
        self.message_frame.pack(fill="both", expand=True, padx=5, pady=5)  # 在 LabelFrame 内部，控件的 pack 通常需要一些额外的 padding 来避免紧贴边框

        self.message_box = tk.Text(self.message_frame, height=12, state=tk.DISABLED, wrap=tk.WORD, font=("", 9))
        self.message_scrollbar = ttk.Scrollbar(self.message_frame, orient=tk.VERTICAL, command=self.message_box.yview)
        self.message_box.config(yscrollcommand=self.message_scrollbar.set)

        self.message_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.message_box.pack(side=tk.LEFT, fill="both", expand=True)

        # 初始化线程控制变量
        self.running = False
        self.thread = None
        self.first_actual_move_done = False  # 用于跟踪第一次鼠标移动是否已精确执行

        # 自动关闭相关变量
        self.auto_close_enabled = False
        self.auto_close_delay_seconds = 0

        # 在关闭窗口时保存配置
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 绑定窗口移动事件
        self.root.bind("<Configure>", self.on_window_configure)

    def on_window_configure(self, event):
        """窗口配置改变事件处理"""
        # 只有在窗口移动时才更新位置
        if event.widget == self.root and (event.x != 0 or event.y != 0):
            self.window_x = self.root.winfo_x()
            self.window_y = self.root.winfo_y()

    def update_ui_language(self):
        """更新UI上的文本为当前语言"""
        self.root.title(self.translations.get("app_title"))

        # 更新标题
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(text=self.translations.get("app_title"))
                break

        # 更新语言标签
        self.language_label.config(text=self.translations.get("language"))

        # 更新设置框标题
        self.settings_frame.config(text=self.translations.get("settings"))

        # 更新日志标题标签
        if hasattr(self, 'log_frame_container'): # 确保 LabelFrame 已创建
            self.log_frame_container.config(text=self.translations.get("log_title"))

        # 更新标签文本
        self.start_time_label.config(text=self.translations.get("start_time"))
        self.end_time_label.config(text=self.translations.get("end_time"))
        self.interval_label.config(text=self.translations.get("interval"))
        self.threshold_label.config(text=self.translations.get("inactivity_time"))
        self.mouse_frame.config(text=self.translations.get("mouse_movement"))
        self.direction_label.config(text=self.translations.get("direction"))
        self.pixels_label.config(text=self.translations.get("pixels"))

        # 更新下拉菜单值
        current_direction = self.direction.get()
        self.direction.config(values=self.translations.get_direction_values())

        # 尝试保持当前选中的方向
        direction_index = self.translations.get_direction_index(current_direction)
        self.direction.current(direction_index)

        # 更新按钮文本
        self.start_button.config(text=self.translations.get("start"))
        self.stop_button.config(text=self.translations.get("stop"))

        self.log_message(self.translations.get("status_change_language"))

    def on_language_change(self, event):
        """当语言选择改变时调用"""
        new_language = self.language_var.get()
        if self.translations.set_language(new_language):
            self.update_ui_language()
            self.save_config()  # 保存语言配置

    def load_config(self):
        """从配置文件加载设置"""
        config = configparser.ConfigParser()

        # 检查配置文件是否存在
        if os.path.exists(self.config_path):
            try:
                config.read(self.config_path, encoding='utf-8')

                if 'Settings' in config:
                    # 加载时间设置
                    if 'start_hour' in config['Settings']:
                        self.start_hour.delete(0, tk.END)
                        self.start_hour.insert(0, config['Settings']['start_hour'])

                    if 'start_minute' in config['Settings']:
                        self.start_minute.delete(0, tk.END)
                        self.start_minute.insert(0, config['Settings']['start_minute'])

                    if 'start_second' in config['Settings']:
                        self.start_second.delete(0, tk.END)
                        self.start_second.insert(0, config['Settings']['start_second'])

                    if 'end_hour' in config['Settings']:
                        self.end_hour.delete(0, tk.END)
                        self.end_hour.insert(0, config['Settings']['end_hour'])

                    if 'end_minute' in config['Settings']:
                        self.end_minute.delete(0, tk.END)
                        self.end_minute.insert(0, config['Settings']['end_minute'])

                    if 'interval' in config['Settings']:
                        self.interval.delete(0, tk.END)
                        self.interval.insert(0, config['Settings']['interval'])

                    if 'end_second' in config['Settings']:
                        self.end_second.delete(0, tk.END)
                        self.end_second.insert(0, config['Settings']['end_second'])

                    # 加载鼠标移动设置
                    if 'direction' in config['Settings']:
                        direction = config['Settings']['direction']
                        # 尝试根据存储的方向值设置方向选择框
                        if direction in ["上", "下", "左", "右", "Up", "Down", "Left", "Right"]:
                            index = self.translations.get_direction_index(direction)
                            self.direction.current(index)

                    if 'pixels' in config['Settings']:
                        self.pixels.delete(0, tk.END)
                        self.pixels.insert(0, config['Settings']['pixels'])

                    # 加载语言设置
                    if 'language' in config['Settings']:
                        language = config['Settings']['language']
                        if language in self.translations.get_language_values():
                            self.language_var.set(language)
                            self.translations.set_language(language)
                            self.update_ui_language()

                    # 加载activity_threshold，默认为 5 秒
                    if 'activity_threshold' in config['Settings']:
                        self.threshold.delete(0, tk.END)
                        self.threshold.insert(0, config['Settings']['activity_threshold'])

                    # 加载自动关闭设置
                    if 'auto_close_enabled' in config['Settings']:
                        self.auto_close_enabled = config['Settings'].getboolean('auto_close_enabled')
                    if 'auto_close_delay_seconds' in config['Settings']:
                        try:
                            self.auto_close_delay_seconds = int(config['Settings']['auto_close_delay_seconds'])
                        except ValueError:
                            self.auto_close_delay_seconds = 0 # 确保是整数

                self.log_message(self.translations.get("status_config_loaded"))
            except Exception as e:
                self.log_message(self.translations.get("status_config_failed").format(str(e)))
        else:
            # 如果配置文件不存在，使用默认值并创建配置文件
            self.save_config()
            self.log_message(self.translations.get("status_config_created"))

    def save_config(self):
        """保存设置到配置文件"""
        config = configparser.ConfigParser()

        # 获取当前方向值
        direction_value = self.direction.get()
        direction_key = self.translations.get_direction_key(direction_value)

        config['Settings'] = {
            'start_hour': self.start_hour.get(),
            'start_minute': self.start_minute.get(),
            'start_second': self.start_second.get(),
            'end_hour': self.end_hour.get(),
            'end_minute': self.end_minute.get(),
            'end_second': self.end_second.get(),
            'interval': self.interval.get(),
            'direction': direction_key,
            'pixels': self.pixels.get(),
            'language': self.translations.current_language,
            'window_x': str(self.window_x) if self.window_x is not None else '',
            'window_y': str(self.window_y) if self.window_y is not None else '',
            'activity_threshold': self.threshold.get(),
            'auto_close_enabled': str(self.auto_close_enabled),
            'auto_close_delay_seconds': str(self.auto_close_delay_seconds)
        }

        try:
            with open(self.config_path, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
        except Exception as e:
            messagebox.showerror(self.translations.get("error"),
                                 self.timestamped(self.translations.get("error_save_failed").format(str(e))))

    def on_closing(self):
        """窗口关闭时的处理函数"""
        # 停止自动化
        if self.running:
            self.stop_automation()

        # 保存配置
        self.save_config()

        # 关闭窗口
        self.root.destroy()

    def start_automation(self):
        try:
            # 获取时间设置
            start_hour = int(self.start_hour.get())
            start_minute = int(self.start_minute.get())
            start_second = int(self.start_second.get())
            end_hour = int(self.end_hour.get())
            end_minute = int(self.end_minute.get())
            interval_seconds = int(self.interval.get())
            end_second = int(self.end_second.get())

            # 获取鼠标移动设置
            direction = self.direction.get()
            pixels = int(self.pixels.get())

            # 验证输入
            if not (0 <= start_hour <= 23 and 0 <= end_hour <= 23):
                messagebox.showerror(self.translations.get("error"),
                                     self.timestamped(self.translations.get("error_hour")))
                return

            if not (0 <= start_minute <= 59 and 0 <= end_minute <= 59):
                messagebox.showerror(self.translations.get("error"),
                                     self.timestamped(self.translations.get("error_minute")))
                return

            if not (0 <= start_second <= 59 and 0 <= end_second <= 59):
                messagebox.showerror(self.translations.get("error"),
                                     self.timestamped(self.translations.get("error_second")))
                return

            if interval_seconds <= 0:
                messagebox.showerror(self.translations.get("error"),
                                     self.timestamped(self.translations.get("error_interval")))
                return

            if pixels <= 0:
                messagebox.showerror(self.translations.get("error"),
                                     self.timestamped(self.translations.get("error_pixels")))
                return

            # --- 新增验证 1：结束时间不能早于开始时间 ---
            start_time_obj_validation = datetime.time(start_hour, start_minute, start_second)
            end_time_obj_validation = datetime.time(end_hour, end_minute, end_second)

            if end_time_obj_validation < start_time_obj_validation:
                messagebox.showerror(self.translations.get("error"),
                                     self.timestamped(self.translations.get("error_time_range")))
                return

            # --- 新增验证 2：在启动线程前进行初始时间范围检查，并细化消息 ---
            now_initial_check = datetime.datetime.now()
            current_time_initial_check = now_initial_check.time()

            start_time_obj_check = datetime.time(start_hour, start_minute, start_second)
            end_time_obj_check = datetime.time(end_hour, end_minute, end_second)

            # 仅当时间已经超过结束时间时，才阻止启动
            if current_time_initial_check > end_time_obj_check:
                # 已经过了结束时间
                self.log_message(self.translations.get("status_work_period_ended"))

                # 恢复UI到未运行状态
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
                return # 提前返回，不启动自动化线程
            
            # 如果在工作时间或还未到工作时间，都允许启动
            if start_time_obj_check <= current_time_initial_check <= end_time_obj_check:
                self.log_message(self.translations.get("status_running"))
            else: # current_time_initial_check < start_time_obj_check
                self.log_message(self.translations.get("status_waiting"))

            # 更新UI状态
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            try:
                self.activity_threshold = int(self.threshold.get())
            except ValueError:
                self.activity_threshold = 5

            # 每次开始时重置标志
            self.first_actual_move_done = False

            # 设置运行标志
            self.running = True

            # 保存当前设置
            self.save_config()

            # 启动自动化线程
            self.thread = threading.Thread(target=self.automation_worker,
                                           args=(start_hour, start_minute, start_second,
                                                 end_hour, end_minute, end_second,
                                                 interval_seconds, direction, pixels))
            self.thread.daemon = True
            self.thread.start()

        except ValueError:
            messagebox.showerror(self.translations.get("error"),
                                 self.timestamped(self.translations.get("error_invalid_value")))

    def stop_automation(self):
        # 停止自动化
        self.running = False

        # 更新UI状态
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_message(self.translations.get("status_stopped"))

    def automation_worker(self, start_hour, start_minute, start_second, end_hour, end_minute, end_second, interval_seconds, direction, pixels):
        while self.running:
            try:
                idle = get_idle_duration()
                if idle < self.activity_threshold:
                    self.log_message(self.translations.get("status_skipped").format(f"{idle:.1f}"))
                    # 在跳过时，也应该使用循环等待，以便能及时响应停止信号
                    for _ in range(interval_seconds):
                        if not self.running: break
                        time.sleep(1)
                    if not self.running: break
                    continue

                now_for_check = datetime.datetime.now()
                current_time_for_check = now_for_check.time()
                start_time_obj = datetime.time(start_hour, start_minute, start_second)
                end_time_obj = datetime.time(end_hour, end_minute, end_second)

                time_of_actual_move = now_for_check

                if start_time_obj <= current_time_for_check <= end_time_obj:
                    if not self.first_actual_move_done:
                        wait_for_second_alignment = 0
                        current_second_of_minute = now_for_check.second
                        target_s = start_second # 开始时间的秒钟

                        if current_second_of_minute < target_s:
                            wait_for_second_alignment = target_s - current_second_of_minute
                        elif current_second_of_minute > target_s:
                            wait_for_second_alignment = (60 - current_second_of_minute) + target_s

                        if wait_for_second_alignment > 0:
                            self.log_message(self.translations.get("status_aligning_first_move").format(wait_for_second_alignment, target_s))
                            for _ in range(wait_for_second_alignment):
                                if not self.running: break
                                time.sleep(1)

                            if not self.running: continue

                            time_of_actual_move = datetime.datetime.now()
                            current_time_for_check = time_of_actual_move.time()

                    if start_time_obj <= current_time_for_check <= end_time_obj:
                        current_x, current_y = get_mouse_position()
                        direction_lower = direction.lower()

                        if direction == self.translations.get("up") or direction_lower == "up":
                            set_mouse_position(current_x, current_y - pixels, duration=0.25)
                            set_mouse_position(current_x, current_y, duration=0.25)
                        elif direction == self.translations.get("down") or direction_lower == "down":
                            set_mouse_position(current_x, current_y + pixels, duration=0.25)
                            set_mouse_position(current_x, current_y, duration=0.25)
                        elif direction == self.translations.get("left") or direction_lower == "left":
                            set_mouse_position(current_x - pixels, current_y, duration=0.25)
                            set_mouse_position(current_x, current_y, duration=0.25)
                        elif direction == self.translations.get("right") or direction_lower == "right":
                            set_mouse_position(current_x + pixels, current_y, duration=0.25)
                            set_mouse_position(current_x, current_y, duration=0.25)

                        self.log_message(self.translations.get("status_last_move").format(time_of_actual_move.strftime('%H:%M:%S')))

                        if not self.first_actual_move_done:
                            self.first_actual_move_done = True
                    else:
                        # 如果等待后超出了工作时间
                        self.log_message(self.translations.get("status_waiting"))
                # 新增：将原来的 else 拆分为两种情况
                elif current_time_for_check < start_time_obj:
                    # 情况一：还未到开始时间，进入“主动侦察”模式
                    self.log_message(self.translations.get("status_waiting"))
                    # 休眠interval_seconds秒，然后立即开始下一次循环检查
                    time.sleep(interval_seconds)
                    continue # 使用 continue 直接进入下一次 while 循环
                else: # current_time_for_check > end_time_obj
                    # 情况二：已经过了结束时间，维持原逻辑
                    self.log_message(self.translations.get("status_waiting"))

                    # 自动关闭逻辑
                    if self.auto_close_enabled:
                        auto_close_message = self.translations.get("auto_close_message").format(self.auto_close_delay_seconds)
                        self.log_message(auto_close_message)
                        self.running = False # 停止自动化线程
                        # 在主线程中调度关闭应用程序
                        self.root.after(self.auto_close_delay_seconds * 1000, self.root.destroy)
                        break # 立即退出循环
                
                # 在工作时间或结束后，才需要等待一个完整的间隔周期
                for _ in range(interval_seconds):
                    if not self.running:
                        break
                    time.sleep(1)

            except Exception as e:
                # 从工作线程安全地记录错误并停止
                error_message = str(e)
                self.log_message(self.translations.get("error") + f": {error_message}")
                if self.root and hasattr(self.root, 'after'):
                    self.root.after(0, self.stop_automation)
                else:
                    self.running = False # Fallback
                break


def main():
    # 确保应用不会被系统DPI缩放设置影响
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass  # 如果失败就忽略

    root = tk.Tk()
    app = MouseMoverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()