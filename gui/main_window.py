from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QListWidget, QLabel, QListWidgetItem)
from PyQt6.QtCore import Qt, QPropertyAnimation, QSize
from PyQt6.QtGui import QIcon
from .task_dialog import TaskDialog
import os
import sys

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("任务管理器")
        self.setMinimumSize(800, 600)
        
        # 获取当前文件所在目录的根目录
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 加载图标（使用绝对路径）
        self.icons = {
            "high": QIcon(os.path.join(root_dir, "images", "high_priority.png")),
            "medium": QIcon(os.path.join(root_dir, "images", "medium_priority.png")),
            "low": QIcon(os.path.join(root_dir, "images", "low_priority.png")),
            "add": QIcon(os.path.join(root_dir, "images", "add_task.png"))
        }
        
        self.setup_ui()
        self.load_tasks()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 任务列表
        self.task_list = QListWidget()
        layout.addWidget(self.task_list)
        
        # 添加任务按钮
        add_button = QPushButton()
        add_button.setIcon(self.icons["add"])
        add_button.setIconSize(QSize(32, 32))
        add_button.clicked.connect(self.add_task)
        layout.addWidget(add_button)
        
        self.setup_animations()
    
    def setup_animations(self):
        """设置界面动画"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(250)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        
    def add_task(self):
        try:
            dialog = TaskDialog(self)
            if dialog.exec():
                task_data = dialog.get_task_data()
                if task_data["name"].strip():  # 确保任务名不为空
                    task_id = self.db.add_task(task_data)
                    self.load_tasks()
        except Exception as e:
            print(f"添加任务时出错: {str(e)}")
    
    def load_tasks(self):
        """从数据库加载任务列表"""
        self.task_list.clear()
        tasks = self.db.get_all_tasks()
        
        for task in tasks:
            item = QListWidgetItem()
            if task[2] == "高":
                item.setIcon(self.icons["high"])
            elif task[2] == "中":
                item.setIcon(self.icons["medium"])
            else:
                item.setIcon(self.icons["low"])
                
            item.setText(f"{task[1]} - 截止日期: {task[3]}")
            self.task_list.addItem(item)
