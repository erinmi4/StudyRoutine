from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QListWidget, QLabel, QListWidgetItem, QHBoxLayout)
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
        
        # 添加任务按钮 - 修改样式
        add_button = QPushButton("添加任务")
        add_button.setIcon(self.icons["add"])
        add_button.setIconSize(QSize(24, 24))
        add_button.setFixedHeight(40)
        add_button.setFixedWidth(200)  # 设置固定宽度
        # 更新按钮样式
        add_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 5px;
                text-align: center;  /* 文字居中 */
                margin: 0 auto;      /* 按钮水平居中 */
            }
        """)
        # 创建水平布局来居中放置按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(add_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
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
