# pages/page_orders.py
from functools import partial
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QProgressBar, QDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

# 导入共享的模拟器线程和新的弹窗
from device_simulator import LineSimulatorThread
from .widgets.snapshot_dialog import SnapshotDialog

class PageOrders(QWidget):
    def __init__(self):
        super().__init__()
        
        self.orders_data = self._create_mock_data()
        self.active_order_id = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 顶部控制栏
        controls_layout = QHBoxLayout()
        add_button = QPushButton("＋ 创建模拟工单")
        add_button.clicked.connect(self._add_new_order)
        controls_layout.addWidget(add_button)
        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["工单ID", "产品名称", "计划数量", "完成进度", "状态", "关联设备", "操作"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        main_layout.addWidget(self.table)
        
        # 连接到同一个模拟器实例 (注意: 这是一个简化的单例模式)
        # 在真实应用中，应该有一个全局的管理器来提供这个实例
        # 这里我们为演示方便，每次都创建一个新的
        self.simulator = LineSimulatorThread(self)
        self.simulator.data_updated.connect(self._update_from_simulator)
        self.simulator.start()

        self._populate_table()

    def _update_from_simulator(self, data):
        """核心逻辑：根据模拟器状态实时更新工单进度"""
        line_status = data.get('line_status')
        
        if line_status == 'running':
            # 如果产线在运行，激活一个待处理的工单
            if not self.active_order_id:
                pending_order = next((o for o in self.orders_data if o['status'] == '待处理'), None)
                if pending_order:
                    self.active_order_id = pending_order['id']
                    pending_order['status'] = '生产中'
                    # 捕获开始生产时的快照
                    pending_order['snapshot'] = {
                        "开始时间": data['timestamp'],
                        "挤出机温度": f"{data['devices']['extruder']['temp']:.2f} °C",
                        "挤出机压力": f"{data['devices']['extruder']['pressure']:.2f} MPa",
                        "牵引速度": f"{data['devices']['tractor']['speed']:.2f} m/min"
                    }

            # 更新正在生产的工单进度
            active_order = next((o for o in self.orders_data if o['id'] == self.active_order_id), None)
            if active_order:
                # 模拟产量增加
                production_per_tick = data['devices']['tractor']['speed'] / 60 * 10 # 假设速度单位是m/min，每秒产量
                active_order['quantity_done'] = min(active_order['quantity_plan'], active_order['quantity_done'] + production_per_tick)
                
                if active_order['quantity_done'] >= active_order['quantity_plan']:
                    active_order['status'] = '已完成'
                    self.active_order_id = None # 生产完成，重置激活工单
                    
        elif line_status in ['idle', 'stopped', 'fault']:
            # 如果产线停止，则暂停当前工单
            if self.active_order_id:
                active_order = next((o for o in self.orders_data if o['id'] == self.active_order_id), None)
                if active_order and active_order['status'] == '生产中':
                    active_order['status'] = '已暂停' if line_status != 'fault' else '故障暂停'
                self.active_order_id = None # 重置激活工an Dan

        self._populate_table() # 每次接收到数据都刷新表格

    def _populate_table(self):
        self.table.setRowCount(len(self.orders_data))
        status_colors = {
            "待处理": QColor("#B0BEC5"), "生产中": QColor("#00BCD4"), 
            "已完成": QColor("#4CAF50"), "已取消": QColor("#F44336"),
            "已暂停": QColor("#FFC107"), "故障暂停": QColor("#D32F2F"),
        }
        
        for row, order in enumerate(self.orders_data):
            # ... (填充前几列)
            self.table.setItem(row, 0, QTableWidgetItem(order["id"]))
            self.table.setItem(row, 1, QTableWidgetItem(order["product"]))
            self.table.setItem(row, 2, QTableWidgetItem(f"{order['quantity_plan']} 米"))
            
            progress = QProgressBar(); 
            percentage = (order["quantity_done"] / order["quantity_plan"]) * 100 if order["quantity_plan"] > 0 else 0
            progress.setValue(int(percentage))
            progress.setFormat(f"{int(order['quantity_done'])} / {order['quantity_plan']}")
            progress.setAlignment(Qt.AlignCenter); 
            self.table.setCellWidget(row, 3, progress)
            
            status_item = QTableWidgetItem(order["status"])
            status_item.setBackground(status_colors.get(order["status"], QColor("white")))
            self.table.setItem(row, 4, status_item)
            
            self.table.setItem(row, 5, QTableWidgetItem(order["device_id"]))
            
            # 操作按钮
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            snapshot_button = QPushButton("生产快照")
            cancel_button = QPushButton("取消工单")
            
            snapshot_button.clicked.connect(partial(self._show_snapshot, order["id"]))
            cancel_button.clicked.connect(partial(self._cancel_order, order["id"]))
            
            actions_layout.addWidget(snapshot_button)
            actions_layout.addWidget(cancel_button)
            actions_layout.setContentsMargins(0,0,0,0)
            self.table.setCellWidget(row, 6, actions_widget)


    def _show_snapshot(self, order_id):
        order = next((o for o in self.orders_data if o['id'] == order_id), None)
        if order and 'snapshot' in order:
            dialog = SnapshotDialog(self, snapshot_data=order['snapshot'])
            dialog.exec_()
        else:
            QMessageBox.information(self, "无快照", "该工单尚未开始生产，没有可用的过程快照。")

    def _cancel_order(self, order_id):
        order = next((o for o in self.orders_data if o['id'] == order_id), None)
        if order and order['status'] not in ['已完成', '已取消']:
            reply = QMessageBox.question(self, "确认取消", f"确定要取消工单 {order_id} 吗?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                order['status'] = '已取消'
                if self.active_order_id == order_id:
                    self.active_order_id = None
                self._populate_table()

    def _add_new_order(self):
        # 简化版的新建工单
        new_id = f"WO-SIM-{len(self.orders_data) + 1:03d}"
        self.orders_data.append({
            "id": new_id, "product": "5mm 滴灌管 (模拟)", "quantity_plan": 5000, 
            "quantity_done": 0, "status": "待处理", "device_id": "LINE-A"
        })
        self._populate_table()

    def _create_mock_data(self):
        return [
            {"id": "WO-SIM-001", "product": "5mm 滴灌管", "quantity_plan": 10000, "quantity_done": 0, "status": "待处理", "device_id": "LINE-A"},
            {"id": "WO-SIM-002", "product": "8mm PE管", "quantity_plan": 8000, "quantity_done": 0, "status": "待处理", "device_id": "LINE-A"},
        ]
        
    def closeEvent(self, event):
        self.simulator.stop()
        super().closeEvent(event)