# pages/widgets/snapshot_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QDialogButtonBox, QLabel)

class SnapshotDialog(QDialog):
    def __init__(self, parent=None, snapshot_data=None):
        super().__init__(parent)
        self.setWindowTitle("生产过程快照")
        
        layout = QFormLayout(self)
        
        if snapshot_data:
            for key, value in snapshot_data.items():
                # 使用 readonly QLineEdit 来显示数据，方便复制
                field = QLineEdit(str(value))
                field.setReadOnly(True)
                layout.addRow(QLabel(f"<b>{key}:</b>"))
                layout.addRow(field)
        else:
            layout.addRow(QLabel("没有可用的快照数据。"))
            
        # 只保留一个关闭按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.button(QDialogButtonBox.Ok).setText("关闭")
        button_box.accepted.connect(self.accept)
        
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(layout)
        main_layout.addWidget(button_box)