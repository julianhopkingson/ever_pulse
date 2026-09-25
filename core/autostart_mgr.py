import sys
import os
import winreg

class AutoStartManager:
    APP_NAME = "EverPulse"
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

    @staticmethod
    def get_executable_command():
        """
        获取当前程序启动命令，附加 --autostart 参数。
        兼容 PyInstaller 单文件打包模式与 Python 源码开发模式。
        """
        if getattr(sys, 'frozen', False):
            exe_path = os.path.abspath(sys.executable)
            return f'"{exe_path}" --autostart'
        else:
            python_exe = os.path.abspath(sys.executable)
            script_path = os.path.abspath(sys.argv[0])
            return f'"{python_exe}" "{script_path}" --autostart'

    @classmethod
    def is_autostart_enabled(cls):
        """ 检测当前是否已在注册表中开启开机自启 """
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REG_PATH, 0, winreg.KEY_READ) as key:
                val, _ = winreg.QueryValueEx(key, cls.APP_NAME)
                return bool(val)
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error checking autostart: {e}")
            return False

    @classmethod
    def set_autostart(cls, enable: bool):
        """
        设置或取消开机自启动。
        Returns:
            (bool, str): (是否成功, 错误信息若有)
        """
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REG_PATH, 0, winreg.KEY_SET_VALUE) as key:
                if enable:
                    cmd = cls.get_executable_command()
                    winreg.SetValueEx(key, cls.APP_NAME, 0, winreg.REG_SZ, cmd)
                else:
                    try:
                        winreg.DeleteValue(key, cls.APP_NAME)
                    except FileNotFoundError:
                        pass
            return True, None
        except Exception as e:
            return False, str(e)

    @classmethod
    def sync_path_if_moved(cls):
        """
        如果已开启开机自启，检查注册表中的路径与当前运行的实际路径是否一致。
        若不一致（例如用户移动了单文件 EXE），自动更新注册表中的路径。
        """
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REG_PATH, 0, winreg.KEY_ALL_ACCESS) as key:
                val, _ = winreg.QueryValueEx(key, cls.APP_NAME)
                current_cmd = cls.get_executable_command()
                if val != current_cmd:
                    winreg.SetValueEx(key, cls.APP_NAME, 0, winreg.REG_SZ, current_cmd)
                    print("Autostart registry path updated to current executable path.")
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error syncing autostart path: {e}")
