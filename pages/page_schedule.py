# pages/page_schedule.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class PageSchedule(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("生产排程中心页面")
        label.setAlignment(Qt.AlignCenter)
        font = label.font()
        font.setPointSize(28)
        font.setBold(True)
        label.setFont(font)
        layout.addWidget(label)