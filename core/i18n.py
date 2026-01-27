import configparser
import os
from core.config_mgr import resource_path

class I18n:
    def __init__(self, assets_dir):
        self.languages = {}
        self.current_language = "中文"
        self.language_file_path = resource_path(os.path.join(assets_dir, "language.ini"))
        self.load_language_file()

    def load_language_file(self):
        if not os.path.exists(self.language_file_path):
             # Default fallback if file missing
             return

        try:
            config = configparser.ConfigParser()
            config.read(self.language_file_path, encoding='utf-8')
            for section in config.sections():
                self.languages[section] = dict(config[section])
        except Exception as e:
            print(f"Error loading language file: {e}")

    def get(self, key):
        if self.current_language in self.languages:
            return self.languages[self.current_language].get(key, key)
        return key

    def set_language(self, language):
        if language in self.languages:
            self.current_language = language
            return True
        return False
    
    def get_available_languages(self):
        return list(self.languages.keys())
