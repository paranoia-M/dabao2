from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class DeviceStatusPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("设备实时状态监控")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24pt; font-weight: bold;")
        layout.addWidget(label)