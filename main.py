import sys
import traceback
import datetime
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.single_instance import SingleInstance

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
