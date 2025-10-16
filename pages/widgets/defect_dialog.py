# pages/widgets/defect_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QComboBox, QDialogButtonBox, QTextEdit)

class DefectDialog(QDialog):
    def __init__(self, parent=None, defect_data=None):
        super().__init__(parent)
        self.setWindowTitle("缺陷样本信息")
        
        self.defect_id_input = QLineEdit()
        self.defect_type_input = QComboBox()
        self.defect_type_input.addItems(["划痕", "斑点", "凹陷", "壁厚不均", "其他"])
        self.description_input = QTextEdit()
        
        form_layout = QFormLayout()
        form_layout.addRow("样本ID:", self.defect_id_input)
        form_layout.addRow("缺陷类型:", self.defect_type_input)
        form_layout.addRow("备注:", self.description_input)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        if defect_data:
            self.defect_id_input.setText(defect_data.get("id", ""))
            self.defect_id_input.setReadOnly(True)
            self.defect_type_input.setCurrentText(defect_data.get("type", "其他"))
            self.description_input.setText(defect_data.get("desc", ""))

    def get_data(self):
        return {
            "id": self.defect_id_input.text(),
            "type": self.defect_type_input.currentText(),
            "desc": self.description_input.toPlainText(),
        }