# pages/page_consumption_model.py
import pyqtgraph as pg
import numpy as np
from functools import partial
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QGridLayout, QGroupBox, QPushButton, QDoubleSpinBox, 
                             QFormLayout)
from PyQt5.QtCore import Qt, QTimer, QRectF # <-- 确保 QRectF 已导入
from PyQt5.QtGui import QColor, QBrush, QPen, QPainterPath

from device_simulator import LineSimulatorThread

# (SankeyNode 类保持不变)
class SankeyNode(pg.GraphicsObject):
    def __init__(self, label, value=0):
        super().__init__()
        self.label = label
        self.value = value
        self.setAcceptHoverEvents(True)
        self.picture = pg.QtGui.QPicture()
        self._generate_picture()
        
    def update_value(self, value):
        self.value = value; self.setToolTip(f"{self.label}: {self.value:.2f} kW"); self._generate_picture(); self.update()
    def _generate_picture(self):
        self.picture = pg.QtGui.QPicture(); painter = pg.QtGui.QPainter(self.picture)
        painter.setPen(pg.mkPen(None)); painter.setBrush(pg.mkBrush(69, 90, 100))
        painter.drawRect(self.boundingRect()); font = pg.QtGui.QFont(); font.setPointSize(10)
        painter.setFont(font); painter.setPen(pg.mkPen('w')); painter.drawText(self.boundingRect(), Qt.AlignCenter, self.label)
        painter.end()
    def boundingRect(self): return QRectF(0, -15, 120, 30)
    def paint(self, p, *args): p.drawPicture(0, 0, self.picture)

class SankeyFlow(pg.GraphicsObject):
    def __init__(self, start_pos, end_pos, width, color, value=0):
        super().__init__()
        self.start_pos, self.end_pos, self.width, self.color, self.value = start_pos, end_pos, width, color, value
        self.setToolTip(f"流量: {self.value:.2f} kW")
        self.picture = pg.QtGui.QPicture()
        if self.width > 0.1: self._generate_picture()

    def _generate_picture(self):
        self.picture = pg.QtGui.QPicture(); painter = pg.QtGui.QPainter(self.picture); path = QPainterPath(); path.moveTo(self.start_pos)
        c1, c2 = self.start_pos + pg.QtCore.QPointF(100, 0), self.end_pos - pg.QtCore.QPointF(100, 0)
        path.cubicTo(c1, c2, self.end_pos); pen = QPen(self.color, self.width); pen.setCapStyle(Qt.FlatCap)
        painter.setPen(pen); painter.drawPath(path); painter.end()

    # --- 核心修正点 ---
    def boundingRect(self): 
        if self.picture.isNull(): 
            return QRectF()
        # 将 QPicture 返回的 QRect 转换为 QRectF
        return QRectF(self.picture.boundingRect()) 

    def paint(self, p, *args): 
        if not self.picture.isNull():
            p.drawPicture(0, 0, self.picture)

class PageConsumptionModel(QWidget):
    def __init__(self):
        super().__init__()
        self.costs = {'electricity_price': 0.8, 'material_price': 12.5}
        
        self.simulator = LineSimulatorThread(self)
        self.simulator.start()
        
        main_layout = QGridLayout(self); main_layout.setContentsMargins(20, 20, 20, 20); main_layout.setSpacing(20)
        kpi_panel = self._create_kpi_panel()
        sankey_panel = self._create_sankey_panel()
        console_panel = self._create_console_panel()

        main_layout.addWidget(kpi_panel, 0, 0, 1, 2)
        main_layout.addWidget(sankey_panel, 1, 0)
        main_layout.addWidget(console_panel, 1, 1)
        main_layout.setColumnStretch(0, 3); main_layout.setColumnStretch(1, 2)
        
        self.timer = QTimer(self); self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)
        self.update_data()
    
    # ... (之后的所有方法都保持不变)
    def _create_kpi_panel(self):
        panel = QFrame(); panel.setFrameShape(QFrame.StyledPanel); layout = QHBoxLayout(panel)
        self.unit_elec_cost_label = self._create_kpi_card("单位电能成本", "0.000", "元 / 米")
        self.unit_mat_cost_label = self._create_kpi_card("单位物料成本", "0.000", "元 / 米")
        self.total_power_label = self._create_kpi_card("总实时功率", "0.0", "kW")
        layout.addWidget(self.unit_elec_cost_label); layout.addWidget(self.unit_mat_cost_label); layout.addWidget(self.total_power_label)
        return panel

    def _create_kpi_card(self, title, value, unit):
        box = QGroupBox(title); layout = QVBoxLayout(box)
        val_label = QLabel(value); val_label.setAlignment(Qt.AlignCenter); val_label.setStyleSheet("font-size: 24pt; font-weight: bold;")
        unit_label = QLabel(unit); unit_label.setAlignment(Qt.AlignCenter); unit_label.setStyleSheet("color: #B0BEC5;")
        layout.addWidget(val_label); layout.addWidget(unit_label)
        return box

    def _create_sankey_panel(self):
        box = QGroupBox("实时能量流模型 (桑基图)")
        self.sankey_view = pg.GraphicsView(); self.sankey_view.setBackgroundBrush(QBrush(QColor("#263238")))
        self.sankey_scene = pg.GraphicsScene(); self.sankey_view.setScene(self.sankey_scene)
        layout = QVBoxLayout(box); layout.addWidget(self.sankey_view)
        return box
        
    def _create_console_panel(self):
        panel = QWidget(); layout = QVBoxLayout(panel)
        pareto_panel = self._create_pareto_panel()
        cost_editor_panel = self._create_cost_editor_panel()
        scenario_panel = self._create_scenario_panel()
        layout.addWidget(pareto_panel); layout.addWidget(cost_editor_panel); layout.addWidget(scenario_panel); layout.addStretch()
        return panel
        
    def _create_pareto_panel(self):
        box = QGroupBox("成本构成帕累托分析")
        self.pareto_plot = pg.PlotWidget(); self.pareto_plot.setBackground('#263238'); self.pareto_plot.showGrid(y=True, alpha=0.3); self.pareto_plot.addLegend(offset=(1,1))
        self.pareto_bars = pg.BarGraphItem(x=[], height=[], width=0.6, brush='c', name='成本 (元/小时)')
        self.pareto_curve = pg.PlotDataItem(pen='y', name='累计占比 (%)')
        p2 = pg.ViewBox(); self.pareto_plot.scene().addItem(p2); self.pareto_plot.getAxis('right').linkToView(p2); p2.setYRange(0, 100); p2.addItem(self.pareto_curve)
        self.pareto_plot.addItem(self.pareto_bars)
        def update_views(): p2.setGeometry(self.pareto_plot.getViewBox().sceneBoundingRect())
        self.pareto_plot.getViewBox().sigResized.connect(update_views)
        layout = QVBoxLayout(box); layout.addWidget(self.pareto_plot)
        return box
        
    def _create_cost_editor_panel(self):
        box = QGroupBox("成本参数设置 (What-If分析)")
        layout = QFormLayout(box)
        self.elec_price_input = QDoubleSpinBox(); self.elec_price_input.setDecimals(3); self.elec_price_input.setValue(self.costs['electricity_price'])
        self.mat_price_input = QDoubleSpinBox(); self.mat_price_input.setDecimals(3); self.mat_price_input.setValue(self.costs['material_price'])
        update_button = QPushButton("更新成本"); update_button.clicked.connect(self._update_costs)
        layout.addRow("电价 (元/kWh):", self.elec_price_input); layout.addRow("原料单价 (元/kg):", self.mat_price_input); layout.addRow(update_button)
        return box

    def _create_scenario_panel(self):
        box = QGroupBox("生产模式仿真")
        layout = QHBoxLayout(box)
        modes = {"节能模式": "energy_saving", "常规模式": "normal", "高速模式": "high_speed"}
        for text, mode in modes.items():
            btn = QPushButton(text); btn.clicked.connect(partial(self.simulator.set_mode, mode)); layout.addWidget(btn)
        return box
        
    def _update_costs(self):
        self.costs['electricity_price'] = self.elec_price_input.value()
        self.costs['material_price'] = self.mat_price_input.value()
        self.update_data()

    def update_data(self):
        data = {'line_status': self.simulator.line_status, 'devices': self.simulator.devices}
        mode = self.simulator.mode; power_multiplier = 1.3 if mode == 'high_speed' else 0.75 if mode == 'energy_saving' else 1.0
        power_data = {
            '挤出机': 25 if data['devices']['extruder']['status'] == 'running' else 1, '牵引机': 5 if data['devices']['tractor']['status'] == 'running' else 0.5,
            '收卷机': 3 if data['devices']['winder']['status'] == 'running' else 0.5, '冷却系统': 2, '照明': 1, '热损耗': 4
        }
        power_data['挤出机'] *= power_multiplier; power_data['牵引机'] *= power_multiplier
        total_power = sum(power_data.values())
        speed_mps = data['devices']['tractor']['speed'] / 60.0; material_consumption_kgps = (speed_mps / 100) if speed_mps > 0 else 0
        if speed_mps > 0:
            elec_cost_per_sec = total_power * (self.costs['electricity_price'] / 3600); unit_elec_cost = elec_cost_per_sec / speed_mps
            mat_cost_per_sec = material_consumption_kgps * self.costs['material_price']; unit_mat_cost = mat_cost_per_sec / speed_mps
        else: unit_elec_cost = unit_mat_cost = 0; mat_cost_per_sec = 0
        self.unit_elec_cost_label.findChild(QLabel).setText(f"{unit_elec_cost:.3f}")
        self.unit_mat_cost_label.findChild(QLabel).setText(f"{unit_mat_cost:.3f}")
        self.total_power_label.findChild(QLabel).setText(f"{total_power:.1f}")
        self._update_sankey(power_data)
        self._update_pareto(power_data, mat_cost_per_sec)

    def _update_sankey(self, power_data):
        self.sankey_scene.clear(); scale = 1.5
        nodes = {'in': SankeyNode("总输入"), 'extruder': SankeyNode("挤出机"), 'tractor': SankeyNode("牵引机"), 'other': SankeyNode("其他"), 'loss': SankeyNode("损耗")}
        nodes['in'].setPos(50, 150); nodes['extruder'].setPos(300, 50); nodes['tractor'].setPos(300, 120); nodes['other'].setPos(300, 190); nodes['loss'].setPos(300, 260)
        flows_data = [
            ('in', 'extruder', power_data['挤出机'], QColor(255,170,0,180)), ('in', 'tractor', power_data['牵引机'], QColor(0,170,255,180)),
            ('in', 'other', power_data['收卷机'] + power_data['冷却系统'] + power_data['照明'], QColor(0,255,170,180)),
            ('in', 'loss', power_data['热损耗'], QColor(200,200,200,120)),
        ]
        total_power = sum(d[2] for d in flows_data); nodes['in'].update_value(total_power)
        for _, dst_key, val, _ in flows_data: nodes[dst_key].update_value(val)
        for node in nodes.values(): self.sankey_scene.addItem(node)
        current_y = nodes['in'].y() - sum(d[2] for d in flows_data) * scale / 2
        for src_key, dst_key, width, color in flows_data:
            start_y_pos = current_y + (width * scale / 2)
            flow = SankeyFlow(pg.QtCore.QPointF(nodes[src_key].x() + nodes[src_key].boundingRect().width(), start_y_pos), 
                              pg.QtCore.QPointF(nodes[dst_key].x(), nodes[dst_key].y()), width * scale, color, value=width)
            self.sankey_scene.addItem(flow)
            current_y += width * scale

    def _update_pareto(self, power_data, mat_cost_per_sec):
        elec_cost_per_hour = {k: v * self.costs['electricity_price'] for k, v in power_data.items()}; all_costs = elec_cost_per_hour
        all_costs['原料'] = mat_cost_per_sec * 3600
        sorted_costs = sorted(all_costs.items(), key=lambda item: item[1], reverse=True)
        labels = [item[0] for item in sorted_costs]; values = [item[1] for item in sorted_costs]
        total_cost = sum(values)
        if total_cost == 0: cumulative_percentage = np.zeros(len(values))
        else: cumulative_percentage = np.cumsum(values) / total_cost * 100
        self.pareto_bars.setOpts(x=np.arange(len(labels)), height=values, width=0.6)
        self.pareto_curve.setData(np.arange(len(labels)), cumulative_percentage)
        self.pareto_plot.getAxis('bottom').setTicks([list(enumerate(labels))]); self.pareto_plot.getAxis('bottom').setTextPen('w')
        
    def closeEvent(self, event):
        self.timer.stop()
        if hasattr(self, 'simulator'): self.simulator.stop()
        super().closeEvent(event)