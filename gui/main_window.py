from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QListWidget, QLabel)
from PyQt6.QtCore import Qt, QPropertyAnimation
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("任务管理器")
        self.setMinimumSize(800, 600)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 添加任务列表
        self.task_list = QListWidget()
        layout.addWidget(self.task_list)
        
        # 添加按钮
        add_button = QPushButton("添加任务")
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
        """添加新任务"""
        # TODO: 实现添加任务对话框
        pass
