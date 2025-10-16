# pages/widgets/digital_twin_widgets.py
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QPen

class MachineItem(QGraphicsRectItem):
    """代表生产线上的一个设备，能根据状态改变颜色"""
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setBrush(QBrush(QColor("#B0BEC5"))) # 默认颜色
        self.setPen(QPen(Qt.NoPen))
        self.setToolTip(name)
        
        # 添加设备名称标签
        self.label = QGraphicsTextItem(name, self)
        self.label.setDefaultTextColor(Qt.white)
        # 居中标签
        label_rect = self.label.boundingRect()
        rect = self.rect()
        self.label.setPos(rect.x() + (rect.width() - label_rect.width()) / 2, 
                          rect.y() + (rect.height() - label_rect.height()) / 2)
                          
        self.status_colors = {
            'running': QColor("#4CAF50"),  # 绿色
            'idle': QColor("#FFC107"),     # 黄色
            'fault': QColor("#D32F2F"),      # 红色
        }

    def set_status(self, status):
        """根据状态更新颜色"""
        color = self.status_colors.get(status, QColor("#B0BEC5"))
        self.setBrush(QBrush(color))