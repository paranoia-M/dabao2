# pages/page_equipment.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class PageEquipment(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("生产线设备监控页面")
        label.setAlignment(Qt.AlignCenter)
        font = label.font()
        font.setPointSize(28)
        font.setBold(True)
        label.setFont(font)
        layout.addWidget(label)