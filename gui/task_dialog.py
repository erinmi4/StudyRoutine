from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                            QComboBox, QDateEdit, QLabel, QPushButton)
from PyQt6.QtCore import Qt, QDate

class TaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新任务")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 任务名称
        name_layout = QHBoxLayout()
        name_label = QLabel("任务名称:")
        self.name_edit = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # 优先级
        priority_layout = QHBoxLayout()
        priority_label = QLabel("优先级:")
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["高", "中", "低"])
        priority_layout.addWidget(priority_label)
        priority_layout.addWidget(self.priority_combo)
        layout.addLayout(priority_layout)
        
        # 截止日期
        date_layout = QHBoxLayout()
        date_label = QLabel("截止日期:")
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        layout.addLayout(date_layout)
        
        # 确认按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def get_task_data(self):
        """获取任务数据并进行基本验证"""
        name = self.name_edit.text().strip()
        if not name:
            print("任务名称不能为空")
            return None
            
        return {
            "name": name,
            "priority": self.priority_combo.currentText(),
            "deadline": self.date_edit.date().toString("yyyy-MM-dd")
        }

    def accept(self):
        """重写accept方法，添加验证"""
        if self.name_edit.text().strip():
            super().accept()
        else:
            print("请输入任务名称")
