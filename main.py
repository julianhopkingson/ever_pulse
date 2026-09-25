import sys
import os
import traceback
import datetime
from PySide6.QtWidgets import QApplication

# 确保无论开机自启还是双击启动，工作目录永久锁定至应用所在物理目录
if getattr(sys, 'frozen', False):
    app_dir = os.path.dirname(os.path.abspath(sys.executable))
else:
    app_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(app_dir)

from ui.main_window import MainWindow
from core.single_instance import SingleInstance
from core.config_mgr import ConfigManager

# Global Exception Handler
def exception_hook(exctype, value, tb):
    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    print(error_msg) # Print to console
    
    # Write to file
    with open("crash_log.txt", "w", encoding='utf-8') as f:
        f.write(f"Timestamp: {datetime.datetime.now()}\n")
        f.write(error_msg)
        
    sys.exit(1)

sys.excepthook = exception_hook

def main():
    # 开机自启按周排程过滤守门
    if "--autostart" in sys.argv:
        config_mgr = ConfigManager(app_dir)
        today_iso = datetime.date.today().isoweekday() # 1: Mon, ..., 7: Sun
        schedule = config_mgr.get_autostart_days()
        if not schedule[today_iso - 1]:
            print(f"Today (ISO {today_iso}) is not scheduled for autostart. Exiting cleanly...")
            sys.exit(0)

    app = QApplication(sys.argv)
    
    # 确保应用程序唯一实例
    single_instance = SingleInstance()
    if single_instance.check():
        print("Another instance is already running. Exiting...")
        sys.exit(0)
    
    # 设置应用级别属性
    app.setStyle("Fusion") 
    
    window = MainWindow()
    
    # 连接唤醒信号以激活窗口
    single_instance.request_activate.connect(lambda: (window.showNormal(), window.activateWindow(), window.raise_()))

    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
