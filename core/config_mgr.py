import configparser
import os
import sys

def resource_path(relative_path):
    """ 获取资源的绝对路径，兼容 Dev 和 PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class ConfigManager:
    def __init__(self, app_path):
        self.app_path = app_path
        self.config_dir = os.path.join(self.app_path, "config")
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        self.config_path = os.path.join(self.config_dir, "config.ini")
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        """
        Returns:
            str: status key ('status_config_loaded', 'status_config_created', or 'status_config_failed')
            str: error message if failed, else None
        """
        status_key = "status_config_loaded"
        error_msg = None
        
        if os.path.exists(self.config_path):
            try:
                self.config.read(self.config_path, encoding='utf-8')
            except Exception as e:
                status_key = "status_config_failed"
                error_msg = str(e)
        else:
             status_key = "status_config_created"
        
        if 'Settings' not in self.config:
            self.config['Settings'] = {}
            
        # 设置默认值
        defaults = {
            'start_hour': '09', 'start_minute': '00', 'start_second': '00',
            'end_hour': '18', 'end_minute': '00', 'end_second': '00',
            'interval': '60', 'direction': 'Left', 'pixels': '1',
            'language': '中文',
            'activity_threshold': '5',
            'theme': 'Light', # 新增：主题设置
            'auto_close_enabled': 'False',
            'auto_close_delay_seconds': '10',
            'autostart': 'False',
            'autostart_days': '1,2,3,4,5',
            'window_x': '200', 'window_y': '200'
        }
        
        for key, value in defaults.items():
            if key not in self.config['Settings']:
                self.config['Settings'][key] = value
                
        return status_key, error_msg

    def get_autostart_days(self):
        """
        获取自启动计划配置，返回长度为 7 的布尔列表 [Mon, Tue, Wed, Thu, Fri, Sat, Sun]。
        兼容 1,2,3,4,5 索引与 1,1,1,1,1,0,0 布尔格式。
        """
        raw = self.get('autostart_days') or "1,2,3,4,5"
        days_bool = [False] * 7
        try:
            parts = [p.strip() for p in raw.split(',') if p.strip()]
            if len(parts) == 7 and all(p in ('0', '1', 'True', 'False', 'true', 'false') for p in parts):
                days_bool = [p in ('1', 'True', 'true') for p in parts]
            else:
                for p in parts:
                    val = int(p)
                    if 1 <= val <= 7:
                        days_bool[val - 1] = True
        except Exception:
            days_bool = [True, True, True, True, True, False, False]
        return days_bool

    def set_autostart_days(self, days_list):
        """
        保存自启动排程。支持传入长度为 7 的 bool 列表或 int 集合。
        格式化为 1,2,3,4,5 字符串保存。
        """
        if isinstance(days_list, (list, tuple)) and len(days_list) == 7:
            active_iso_days = [str(i + 1) for i, is_on in enumerate(days_list) if is_on]
            self.set('autostart_days', ",".join(active_iso_days))
        elif isinstance(days_list, (set, list, tuple)):
            active_iso_days = sorted([str(d) for d in days_list if 1 <= int(d) <= 7], key=int)
            self.set('autostart_days', ",".join(active_iso_days))

    def get(self, key, type_func=str):
        try:
            val = self.config['Settings'].get(key)
            return type_func(val)
        except:
            return None

    def set(self, key, value):
        self.config['Settings'][key] = str(value)

    def save(self):
        # Allow exception to propagate to UI
        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)
