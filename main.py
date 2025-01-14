import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from models.database import Database
from sync.webdav_sync import WebDAVSync

def main():
    # 初始化数据库
    db = Database()
    
    # 初始化应用
    app = QApplication(sys.argv)
    
    # 创建主窗口，传入数据库实例
    window = MainWindow(db)
    window.show()
    
    # 启动应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
