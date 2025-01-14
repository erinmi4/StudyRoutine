from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QListWidget, QLabel, QListWidgetItem, 
                           QHBoxLayout, QMessageBox, QMenu, QProgressBar)
from PyQt6.QtCore import Qt, QPropertyAnimation, QSize, QTimer
from PyQt6.QtGui import QIcon
from .task_dialog import TaskDialog
from .statistics_dialog import StatisticsDialog
from .pomodoro import PomodoroDialog
from sync.webdav_sync import WebDAVSync
import os
import sys

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.sync = WebDAVSync(db)
        self.setWindowTitle("任务管理器")
        self.setMinimumSize(800, 600)
        
        # 同步相关初始化
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.auto_sync)
        self.sync_timer.start(300000)  # 每5分钟自动同步
        
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
        
        # 添加工具栏
        toolbar_layout = QHBoxLayout()
        
        # 统计按钮
        stats_button = QPushButton("任务统计")
        stats_button.setFixedWidth(100)
        stats_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        stats_button.clicked.connect(self.show_statistics)
        toolbar_layout.addWidget(stats_button)
        
        # 番茄钟按钮
        pomodoro_button = QPushButton("番茄钟")
        pomodoro_button.setFixedWidth(100)
        pomodoro_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        pomodoro_button.clicked.connect(self.show_pomodoro)
        toolbar_layout.addWidget(pomodoro_button)
        
        # 添加同步按钮
        sync_button = QPushButton("同步")
        sync_button.setFixedWidth(100)
        sync_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        sync_button.clicked.connect(self.manual_sync)
        toolbar_layout.addWidget(sync_button)
        
        # 添加同步状态指示器
        self.sync_status = QLabel("同步状态：未连接")
        self.sync_status.setStyleSheet("color: gray;")
        toolbar_layout.addWidget(self.sync_status)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
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
    
    def show_statistics(self):
        try:
            stats = self.db.get_task_statistics()
            if stats['total'] == 0:
                QMessageBox.information(self, "提示", "当前没有任务数据可供统计")
                return
            dialog = StatisticsDialog(stats, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"显示统计信息时出错: {str(e)}")
    
    def show_pomodoro(self):
        try:
            dialog = PomodoroDialog(self)
            dialog.exec()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"打开番茄钟时出错: {str(e)}")

    def contextMenuEvent(self, event):
        """右键菜单"""
        item = self.task_list.itemAt(self.task_list.mapFromGlobal(event.globalPos()))
        if item is not None:
            menu = QMenu(self)
            
            # 添加菜单项
            delete_action = menu.addAction("删除任务")
            complete_action = menu.addAction("标记完成")
            edit_action = menu.addAction("编辑任务")
            
            # 设置动作触发
            delete_action.triggered.connect(lambda: self.delete_task(item))
            complete_action.triggered.connect(lambda: self.mark_task_complete(item))
            edit_action.triggered.connect(lambda: self.edit_task(item))
            
            menu.exec(event.globalPos())
    
    def delete_task(self, item):
        """删除任务"""
        try:
            index = self.task_list.row(item)
            task_id = self.db.get_all_tasks()[index][0]
            reply = QMessageBox.question(self, '确认删除', 
                                       '确定要删除这个任务吗？',
                                       QMessageBox.StandardButton.Yes | 
                                       QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.db.delete_task(task_id)
                self.load_tasks()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"删除任务时出错: {str(e)}")
    
    def mark_task_complete(self, item):
        """标记任务为完成"""
        try:
            index = self.task_list.row(item)
            task_id = self.db.get_all_tasks()[index][0]
            self.db.update_task_progress(task_id, 100)
            self.load_tasks()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"更新任务状态时出错: {str(e)}")
    
    def edit_task(self, item):
        """编辑任务"""
        try:
            index = self.task_list.row(item)
            task = self.db.get_all_tasks()[index]
            dialog = TaskDialog(self, edit_mode=True, task_data={
                'id': task[0],
                'name': task[1],
                'priority': task[2],
                'deadline': task[3]
            })
            if dialog.exec():
                self.load_tasks()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"编辑任务时出错: {str(e)}")

    def auto_sync(self):
        """自动同步任务数据"""
        try:
            self.sync_status.setText("同步状态：同步中...")
            self.sync_status.setStyleSheet("color: orange;")
            
            # 执行同步
            result = self.sync.sync_tasks()
            
            if result["status"] == "success":
                self.sync_status.setText("同步状态：已同步")
                self.sync_status.setStyleSheet("color: green;")
                self.load_tasks()  # 刷新任务列表
            else:
                self.sync_status.setText("同步状态：同步失败")
                self.sync_status.setStyleSheet("color: red;")
                QMessageBox.warning(self, "同步错误", result["message"])
                
        except Exception as e:
            self.sync_status.setText("同步状态：同步错误")
            self.sync_status.setStyleSheet("color: red;")
            QMessageBox.critical(self, "同步错误", f"同步过程中发生错误: {str(e)}")

    def manual_sync(self):
        """手动同步任务数据"""
        self.auto_sync()  # 复用自动同步逻辑
