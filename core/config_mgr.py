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
        if os.path.exists(self.config_path):
            try:
                self.config.read(self.config_path, encoding='utf-8')
            except Exception:
                pass
        
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
            'auto_close_delay_seconds': '0'
        }
        
        for key, value in defaults.items():
            if key not in self.config['Settings']:
                self.config['Settings'][key] = value

    def get(self, key, type_func=str):
        try:
            val = self.config['Settings'].get(key)
            return type_func(val)
        except:
            return None

    def set(self, key, value):
        self.config['Settings'][key] = str(value)

    def save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
        except Exception as e:
            print(f"Error saving config: {e}")
