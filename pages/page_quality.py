# pages/page_quality.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class PageQuality(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("产品质量追溯页面")
        label.setAlignment(Qt.AlignCenter)
        font = label.font()
        font.setPointSize(28)
        font.setBold(True)
        label.setFont(font)
        layout.addWidget(label)