# pages/page_quality_vision.py
import random
from datetime import datetime
from functools import partial
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                             QHeaderView, QPushButton, QSplitter, QGraphicsView, QGraphicsScene, 
                             QMessageBox, QDialog)
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QColor, QBrush, QPen

from .widgets.defect_dialog import DefectDialog

class PageQualityVision(QWidget):
    def __init__(self):
        super().__init__()
        self.defects_data = self._create_mock_data()
        self.next_defect_id = len(self.defects_data) + 1
        
        main_layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Vertical)
        
        # 顶部：实时视觉区域
        vision_panel = self._create_vision_panel()
        # 底部：缺陷管理工作台
        workbench_panel = self._create_workbench_panel()
        
        splitter.addWidget(vision_panel)
        splitter.addWidget(workbench_panel)
        splitter.setSizes([int(self.height() * 0.4), int(self.height() * 0.6)])
        main_layout.addWidget(splitter)
        
        # 启动模拟器
        self.sim_timer = QTimer(self)
        self.sim_timer.timeout.connect(self._simulate_vision_feed)
        self.sim_timer.start(2000) # 每2秒模拟一次检测

    def _create_vision_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        title = QLabel("在线视觉检测"); title.setStyleSheet("font-size: 16pt;")
        
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor("#263238")))
        self.view = QGraphicsView(self.scene)
        
        layout.addWidget(title); layout.addWidget(self.view)
        return panel

    def _create_workbench_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("缺陷样本管理工作台"))
        controls_layout.addStretch()
        add_button = QPushButton("＋ 手动添加样本"); add_button.clicked.connect(self._add_defect)
        controls_layout.addWidget(add_button)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "时间", "类型", "状态", "备注", "操作"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemClicked.connect(self._highlight_defect_in_vision)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.table)
        self._populate_table()
        return panel

    def _simulate_vision_feed(self):
        """核心逻辑：模拟实时视觉流和缺陷检测"""
        self.scene.clear()
        
        # 模拟产品图像 (一个灰色长方形)
        pipe_image = self.scene.addRect(0, 0, 400, 100, brush=QBrush(Qt.gray))
        
        # 随机决定是否生成缺陷
        if random.random() < 0.3: # 30%的概率产生缺陷
            defect_x = random.randint(50, 350)
            defect_y = random.randint(20, 80)
            defect_size = random.randint(10, 20)
            
            # 在图像上绘制红色标记框
            defect_box = self.scene.addRect(defect_x, defect_y, defect_size, defect_size, pen=QPen(Qt.red, 3))
            
            # 自动添加一条新的缺陷记录
            new_defect = {
                "id": f"DEF-{self.next_defect_id:04d}",
                "time": datetime.now().strftime("%H:%M:%S"),
                "type": random.choice(["划痕", "斑点", "凹陷"]),
                "status": "待复判",
                "desc": "系统自动检测",
                "pos": (defect_x, defect_y, defect_size) # 存储位置信息
            }
            self.defects_data.insert(0, new_defect)
            self.next_defect_id += 1
            self._populate_table()
            
    def _populate_table(self):
        self.table.setRowCount(len(self.defects_data))
        status_colors = {"待复判": QColor("#FFC107"), "已确认": QColor("#4CAF50"), "已忽略": QColor("#9E9E9E")}
        
        for row, defect in enumerate(self.defects_data):
            self.table.setItem(row, 0, QTableWidgetItem(defect["id"]))
            self.table.setItem(row, 1, QTableWidgetItem(defect["time"]))
            self.table.setItem(row, 2, QTableWidgetItem(defect["type"]))
            
            status_item = QTableWidgetItem(defect["status"])
            status_item.setBackground(status_colors.get(defect["status"], QColor("white")))
            self.table.setItem(row, 3, status_item)
            
            self.table.setItem(row, 4, QTableWidgetItem(defect["desc"]))
            self._create_action_buttons(row, defect)

    def _create_action_buttons(self, row, defect):
        widget = QWidget()
        layout = QHBoxLayout(widget); layout.setContentsMargins(0,0,0,0)
        
        edit_button = QPushButton("编辑"); edit_button.clicked.connect(partial(self._edit_defect, defect["id"]))
        delete_button = QPushButton("删除"); delete_button.clicked.connect(partial(self._delete_defect, defect["id"]))
        
        # 核心业务逻辑：状态流转
        confirm_button = QPushButton("确认"); confirm_button.clicked.connect(partial(self._change_status, defect["id"], "已确认"))
        ignore_button = QPushButton("忽略"); ignore_button.clicked.connect(partial(self._change_status, defect["id"], "已忽略"))
        
        layout.addWidget(edit_button); layout.addWidget(delete_button)
        # 只有“待复判”状态下才显示确认和忽略按钮
        if defect["status"] == "待复判":
            layout.addWidget(confirm_button); layout.addWidget(ignore_button)
            
        self.table.setCellWidget(row, 5, widget)

    def _highlight_defect_in_vision(self, item):
        """数据与图像联动"""
        row = item.row()
        defect = self.defects_data[row]
        self._simulate_vision_feed() # 重绘场景
        if "pos" in defect:
            x, y, size = defect["pos"]
            self.scene.addRect(x, y, size, size, pen=QPen(Qt.cyan, 5)) # 用更醒目的颜色高亮

    def _add_defect(self):
        dialog = DefectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            new_defect = {
                "id": data["id"] or f"MAN-{self.next_defect_id:04d}",
                "time": datetime.now().strftime("%H:%M:%S"),
                "type": data["type"],
                "status": "已确认", # 手动添加的默认为已确认
                "desc": data["desc"]
            }
            self.defects_data.insert(0, new_defect)
            self.next_defect_id += 1
            self._populate_table()

    def _edit_defect(self, defect_id):
        defect = next((d for d in self.defects_data if d["id"] == defect_id), None)
        if not defect: return
        dialog = DefectDialog(self, defect_data=defect)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            defect.update(data)
            self._populate_table()
            
    def _delete_defect(self, defect_id):
        reply = QMessageBox.question(self, "确认删除", f"确定删除样本 {defect_id}？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.defects_data = [d for d in self.defects_data if d["id"] != defect_id]
            self._populate_table()

    def _change_status(self, defect_id, new_status):
        defect = next((d for d in self.defects_data if d["id"] == defect_id), None)
        if defect:
            defect["status"] = new_status
            self._populate_table()
            
    def _create_mock_data(self):
        return [
            {"id": "DEF-0001", "time": "10:30:15", "type": "划痕", "status": "已确认", "desc": "换料时操作不当导致"},
            {"id": "DEF-0002", "time": "10:32:45", "type": "斑点", "status": "已忽略", "desc": "传感器上的灰尘，已清理"},
        ]
        
    def closeEvent(self, event):
        self.sim_timer.stop()
        super().closeEvent(event)