from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import numpy as np

class StatisticsDialog(QDialog):
    def __init__(self, stats, parent=None):
        super().__init__(parent)
        self.setWindowTitle("任务统计")
        self.setMinimumSize(600, 500)
        self.stats = stats
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 添加标题
        title = QLabel("任务完成情况统计")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 创建统计图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))
        
        # 饼图数据
        labels = ['已完成', '进行中', '待开始']
        sizes = [
            self.stats['completed'],
            self.stats['in_progress'],
            self.stats['pending']
        ]
        colors = ['#4CAF50', '#FFC107', '#F44336']
        
        # 绘制饼图
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                startangle=90)
        ax1.set_title('任务状态分布')
        
        # 绘制柱状图
        x = np.arange(len(labels))
        ax2.bar(x, sizes, color=colors)
        ax2.set_title('任务数量统计')
        ax2.set_xticks(x)
        ax2.set_xticklabels(labels)
        
        # 添加到布局
        canvas = FigureCanvasQTAgg(fig)
        layout.addWidget(canvas)
        
        # 添加统计信息
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_layout.addWidget(QLabel(f"总任务数: {self.stats['total']}"))
        stats_layout.addWidget(QLabel(f"已完成: {self.stats['completed']}"))
        stats_layout.addWidget(QLabel(f"进行中: {self.stats['in_progress']}"))
        stats_layout.addWidget(QLabel(f"待开始: {self.stats['pending']}"))
        
        layout.addWidget(stats_frame)
