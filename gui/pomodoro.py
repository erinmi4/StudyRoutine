from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, 
                           QLabel, QProgressBar, QHBoxLayout, QComboBox, QMessageBox)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon
import os

class PomodoroDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("番茄钟")
        self.setMinimumSize(400, 300)
        
        # 初始化变量
        self.time_left = 25 * 60
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.is_break = False
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 模式选择
        mode_layout = QHBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["25分钟", "45分钟", "60分钟"])
        self.mode_combo.currentTextChanged.connect(self.change_mode)
        mode_layout.addWidget(QLabel("工作时长:"))
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)
        
        # 时间显示
        self.time_label = QLabel("25:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("""
            font-size: 48px;
            color: #2196F3;
            margin: 20px;
        """)
        layout.addWidget(self.time_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(25 * 60)
        self.progress_bar.setValue(25 * 60)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                width: 10px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # 控制按钮布局
        button_layout = QHBoxLayout()
        
        # 开始/暂停按钮
        self.start_button = QPushButton("开始")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.start_button.clicked.connect(self.start_timer)
        button_layout.addWidget(self.start_button)
        
        # 重置按钮
        reset_button = QPushButton("重置")
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                padding: 10px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        reset_button.clicked.connect(self.reset_timer)
        button_layout.addWidget(reset_button)
        
        layout.addLayout(button_layout)
    
    def change_mode(self, text):
        minutes = int(text.replace("分钟", ""))
        self.time_left = minutes * 60
        self.progress_bar.setMaximum(self.time_left)
        self.progress_bar.setValue(self.time_left)
        self.update_display()
        
    def start_timer(self):
        if self.start_button.text() == "开始":
            self.timer.start(1000)
            self.start_button.setText("暂停")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFC107;
                    color: black;
                    border-radius: 5px;
                    padding: 10px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #FFA000;
                }
            """)
        else:
            self.timer.stop()
            self.start_button.setText("开始")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 5px;
                    padding: 10px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            
    def update_timer(self):
        self.time_left -= 1
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        self.progress_bar.setValue(self.time_left)
        
        if self.time_left <= 0:
            self.timer.stop()
            self.handle_timer_complete()
    
    def handle_timer_complete(self):
        """处理计时完成事件"""
        if not self.is_break:
            reply = QMessageBox.question(self, '休息提醒', 
                                       '工作时间结束，是否开始休息？\n(5分钟)',
                                       QMessageBox.StandardButton.Yes | 
                                       QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.is_break = True
                self.time_left = 5 * 60  # 5分钟休息
                self.progress_bar.setMaximum(5 * 60)
                self.progress_bar.setValue(self.time_left)
                self.timer.start(1000)
                self.setStyleSheet("background-color: #E8F5E9;")  # 休息时背景变绿
            else:
                self.reset_timer()
        else:
            QMessageBox.information(self, '提醒', '休息时间结束，继续工作吧！')
            self.is_break = False
            self.reset_timer()
            self.setStyleSheet("")  # 恢复默认背景
            
    def reset_timer(self):
        self.timer.stop()
        self.time_left = 25 * 60
        self.progress_bar.setValue(self.time_left)
        self.update_display()
        self.start_button.setText("开始")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
    def update_display(self):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
