from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QListWidget, QLabel, QListWidgetItem, 
                           QHBoxLayout, QMessageBox, QMenu, QProgressBar)
from PyQt6.QtCore import Qt, QPropertyAnimation, QSize, QTimer, QEasingCurve, QPoint
from PyQt6.QtGui import QIcon, QPixmap
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
        
        # 图片资源路径
        self.image_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
        
        # 加载图标
        self.icons = {
            "high": QIcon(os.path.join(self.image_dir, "high_priority.png")),
            "medium": QIcon(os.path.join(self.image_dir, "medium_priority.png")), 
            "low": QIcon(os.path.join(self.image_dir, "low_priority.png")),
            "add": QIcon(os.path.join(self.image_dir, "add_task.png")),
            "sync": QIcon(os.path.join(self.image_dir, "sync_icon.png")),
            "stats": QIcon(os.path.join(self.image_dir, "stats_icon.png")),
            "pomodoro": QIcon(os.path.join(self.image_dir, "pomodoro_icon.png"))
        }
        
        # 动画相关
        self.animations = {}
        self.setup_ui()
        self.load_tasks()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        # 统计按钮
        stats_button = QPushButton()
        stats_button.setIcon(self.icons["stats"])
        stats_button.setIconSize(QSize(24, 24))
        stats_button.setToolTip("查看任务统计")
        stats_button.clicked.connect(self.show_statistics)
        self.add_button_animation(stats_button)
        toolbar_layout.addWidget(stats_button)
        
        # 番茄钟按钮
        pomodoro_button = QPushButton()
        pomodoro_button.setIcon(self.icons["pomodoro"])
        pomodoro_button.setIconSize(QSize(24, 24))
        pomodoro_button.setToolTip("启动番茄钟")
        pomodoro_button.clicked.connect(self.show_pomodoro)
        self.add_button_animation(pomodoro_button)
        toolbar_layout.addWidget(pomodoro_button)
        
        # 同步按钮
        sync_button = QPushButton()
        sync_button.setIcon(self.icons["sync"])
        sync_button.setIconSize(QSize(24, 24))
        sync_button.setToolTip("手动同步任务")
        sync_button.clicked.connect(self.manual_sync)
        self.add_button_animation(sync_button)
        toolbar_layout.addWidget(sync_button)
        
        # 同步状态
        self.sync_status = QLabel("同步状态：未连接")
        self.sync_status.setStyleSheet("color: gray;")
        toolbar_layout.addWidget(self.sync_status)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # 任务列表
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget {
                background-color: #f5f5f5;
                border-radius: 5px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #ddd;
                min-height: 80px;
                background-color: white;  /* 添加默认背景色 */
            }
            QListWidget::item:hover {
                background-color: #e0f7fa;
            }
            QListWidget::item:selected {
                background-color: #e0f7fa;  /* 选中时的背景色 */
            }
            QListWidget::item:focus {
                background-color: white;  /* 失去焦点时恢复原色 */
                outline: none;  /* 移除焦点边框 */
            }
        """)
        self.task_list.itemClicked.connect(self.handle_item_click)  # 添加点击处理
        layout.addWidget(self.task_list)
        
        # 添加任务按钮
        add_button = QPushButton("添加任务")
        add_button.setIcon(self.icons["add"])
        add_button.setIconSize(QSize(24, 24))
        add_button.setFixedHeight(40)
        add_button.setFixedWidth(200)
        add_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 5px;
                text-align: center;
                margin: 0 auto;
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_button.clicked.connect(self.add_task)  # 直接连接，不使用动画
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(add_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
    def add_button_animation(self, button):
        """为按钮添加点击动画"""
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(100)
        animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        def animate():
            original = button.geometry()
            animation.setStartValue(original)
            animation.setEndValue(original.adjusted(-2, -2, 2, 2))
            animation.start()
            
        button.clicked.connect(animate)
        self.animations[button] = animation
        
    def load_tasks(self):
        """加载任务列表并添加动画"""
        self.task_list.clear()
        tasks = self.db.get_all_tasks()
        
        for task in tasks:
            item = QListWidgetItem()
            
            # 创建主容器
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(5, 5, 5, 5)
            
            # 创建任务内容widget
            content_widget = QWidget()
            content_widget.setAutoFillBackground(True)
            content_widget.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border-radius: 8px;
                    border: 1px solid #e0e0e0;
                    padding: 12px;
                }
                QWidget:hover {
                    background-color: #f5f5f5;
                    border-color: #bdbdbd;
                }
            """)
            
            # 任务内容布局
            layout = QHBoxLayout(content_widget)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(15)
            
            # 左侧信息布局
            left_layout = QVBoxLayout()
            left_layout.setSpacing(8)
            left_layout.setContentsMargins(0, 0, 0, 0)
            
            # 任务标题和优先级
            title_layout = QHBoxLayout()
            title_layout.setSpacing(12)
            title_layout.setContentsMargins(0, 0, 0, 0)
            
            # 优先级图标
            priority_icon = QLabel()
            priority_icon.setFixedSize(28, 28)
            if task[2] == "高":
                priority_icon.setPixmap(self.icons["high"].pixmap(28, 28))
            elif task[2] == "中":
                priority_icon.setPixmap(self.icons["medium"].pixmap(28, 28))
            else:
                priority_icon.setPixmap(self.icons["low"].pixmap(28, 28))
            title_layout.addWidget(priority_icon)
            
            # 任务名称
            task_name = QLabel(task[1])
            task_name.setStyleSheet("""
                font-size: 16px;
                font-weight: 500;
                color: #212121;
            """)
            title_layout.addWidget(task_name, 1)
            left_layout.addLayout(title_layout)
            
            # 截止日期
            deadline = QLabel(f"⏰ {task[3]}")
            deadline.setStyleSheet("""
                color: #757575;
                font-size: 13px;
                padding-left: 40px;
            """)
            left_layout.addWidget(deadline)
            
            layout.addLayout(left_layout, 1)
            
            # 右侧进度条布局
            right_layout = QVBoxLayout()
            right_layout.setSpacing(6)
            right_layout.setContentsMargins(0, 0, 0, 0)
            
            # 进度条
            progress = QProgressBar()
            progress.setValue(task[4])
            progress.setFixedWidth(180)
            progress.setFixedHeight(24)
            progress.setStyleSheet("""
                QProgressBar {
                    background-color: #f5f5f5;
                    border: 1px solid #e0e0e0;
                    border-radius: 12px;
                    text-align: center;
                    font-size: 12px;
                    color: #616161;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 12px;
                    border: 1px solid #43A047;
                }
            """)
            
            # 进度文本
            progress_text = QLabel(f"进度：{task[4]}%")
            progress_text.setStyleSheet("""
                color: #616161;
                font-size: 13px;
                font-weight: 500;
            """)
            progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            right_layout.addWidget(progress)
            right_layout.addWidget(progress_text)
            right_layout.addStretch()
            
            layout.addLayout(right_layout)
            
            # 设置最小高度
            content_widget.setMinimumHeight(100)
            
            # 将内容添加到容器
            container_layout.addWidget(content_widget)
            
            # 设置列表项属性
            item.setSizeHint(container.sizeHint())
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, container)
            
            # 添加动画效果
            animation = QPropertyAnimation(content_widget, b"pos")
            animation.setDuration(300)
            animation.setStartValue(content_widget.pos() - QPoint(content_widget.width(), 0))
            animation.setEndValue(content_widget.pos())
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            animation.start()
            
    def show_statistics(self):
        """显示统计对话框"""
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
        """显示番茄钟对话框"""
        try:
            dialog = PomodoroDialog(self)
            dialog.exec()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"打开番茄钟时出错: {str(e)}")
    
    def manual_sync(self):
        """手动同步任务"""
        try:
            if not self.sync.connected:
                reply = QMessageBox.question(
                    self,
                    "同步设置",
                    "需要设置WebDAV同步吗？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # TODO: 添加WebDAV设置对话框
                    pass
                return
                
            reply = QMessageBox.question(
                self,
                "确认同步",
                "确定要同步任务数据吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.sync.sync_tasks():
                    self.sync_status.setText("同步状态：已同步")
                    self.sync_status.setStyleSheet("color: green;")
                    self.load_tasks()  # 刷新任务列表
                else:
                    self.sync_status.setText("同步状态：同步失败")
                    self.sync_status.setStyleSheet("color: red;")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"同步任务时出错: {str(e)}")
    
    def add_task(self):
        """添加新任务"""
        try:
            dialog = TaskDialog(self)
            if dialog.exec():
                task_data = dialog.get_task_data()
                if task_data and task_data["name"].strip():
                    task_id = self.db.add_task(task_data)
                    if task_id:
                        self.load_tasks()
                        self.sync_status.setText("同步状态：待同步")
                        self.sync_status.setStyleSheet("color: orange;")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"添加任务时出错: {str(e)}")

    def contextMenuEvent(self, event):
        """右键菜单事件"""
        item = self.task_list.itemAt(self.task_list.mapFromGlobal(event.globalPos()))
        if item is not None:
            menu = QMenu(self)
            
            delete_action = menu.addAction("删除任务")
            delete_action.triggered.connect(lambda: self.delete_task(item))
            
            complete_action = menu.addAction("标记为完成")
            complete_action.triggered.connect(lambda: self.mark_task_complete(item))
            
            edit_action = menu.addAction("编辑任务")
            edit_action.triggered.connect(lambda: self.edit_task(item))
            
            menu.exec(event.globalPos())
    
    def delete_task(self, item):
        """删除任务"""
        try:
            index = self.task_list.row(item)
            task_id = self.db.get_all_tasks()[index][0]
            reply = QMessageBox.question(
                self,
                "确认删除",
                "确定要删除这个任务吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
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
            dialog = TaskDialog(
                self,
                edit_mode=True,
                task_data={
                    'id': task[0],
                    'name': task[1],
                    'priority': task[2],
                    'deadline': task[3]
                }
            )
            if dialog.exec():
                updated_data = dialog.get_task_data()
                if updated_data:
                    self.db.update_task(updated_data)
                    self.load_tasks()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"编辑任务时出错: {str(e)}")
    
    def handle_item_click(self, item):
        """处理任务项点击事件"""
        # 清除其他项的选中状态
        for i in range(self.task_list.count()):
            other_item = self.task_list.item(i)
            if other_item != item:
                other_item.setSelected(False)
        
        # 设置当前项的选中状态
        item.setSelected(True)
