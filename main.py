import sys
import traceback
import datetime
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

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
    
    # 设置应用级别属性
    app.setStyle("Fusion") 
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
