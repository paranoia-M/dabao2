# pages/page_health_diagnosis.py
import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
                             QGraphicsTextItem, QGraphicsLineItem, QSplitter)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QBrush, QPen, QFont
import pyqtgraph as pg

class ComponentNode(QGraphicsEllipseItem):
    """设备拓扑图中的一个部件节点"""
    def __init__(self, name, data, parent=None):
        super().__init__(-30, -30, 60, 60, parent)
        self.setBrush(QBrush(Qt.gray))
        self.name = name
        self.data = data # 存储关联的传感器数据
        self.health_score = 100

        self.label = QGraphicsTextItem(name, self)
        self.label.setDefaultTextColor(Qt.white)
        self.label.setPos(-self.label.boundingRect().width() / 2, -10)
        
        self.setAcceptHoverEvents(True)
    
    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(Qt.cyan))
        self.setCursor(Qt.PointingHandCursor)
    
    def hoverLeaveEvent(self, event):
        self.update_health_color() # 恢复原来的颜色
    
    def update_health_color(self):
        if self.health_score > 80: color = QColor("#4CAF50") # 健康
        elif self.health_score > 50: color = QColor("#FFC107") # 警告
        else: color = QColor("#D32F2F") # 危险
        self.setBrush(QBrush(color))

class PageHealthDiagnosis(QWidget):
    def __init__(self):
        super().__init__()
        self._create_mock_data()

        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(15, 15, 15, 15)
        title = QLabel("挤出机健康诊断与预测性维护"); title.setStyleSheet("font-size: 18pt;")
        main_layout.addWidget(title)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：设备拓扑图
        topology_panel = self._create_topology_panel()
        # 右侧：详细分析面板
        details_panel = self._create_details_panel()

        splitter.addWidget(topology_panel)
        splitter.addWidget(details_panel)
        splitter.setSizes([int(self.width() * 0.4), int(self.width() * 0.6)])
        main_layout.addWidget(splitter)
        
        # 初始计算并显示健康度
        self._calculate_all_health()

    def _create_topology_panel(self):
        panel = QFrame(); panel.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("设备结构拓扑"))
        
        self.scene = QGraphicsScene(); self.scene.setBackgroundBrush(QBrush(QColor("#263238")))
        view = QGraphicsView(self.scene)
        
        # 创建节点
        self.nodes = {
            'motor': ComponentNode("驱动电机", self.db['motor_current']),
            'gearbox': ComponentNode("减速箱", self.db['gearbox_vibration']),
            'heater': ComponentNode("加热器", self.db['heater_temp']),
        }
        self.nodes['motor'].setPos(0, 0)
        self.nodes['gearbox'].setPos(-100, 100)
        self.nodes['heater'].setPos(100, 100)
        
        # 创建连接线
        self.scene.addItem(QGraphicsLineItem(0, 0, -100, 100))
        self.scene.addItem(QGraphicsLineItem(0, 0, 100, 100))
        
        for node in self.nodes.values():
            self.scene.addItem(node)
            node.mousePressEvent = lambda event, n=node: self._on_node_clicked(n)
            
        layout.addWidget(view)
        return panel

    def _create_details_panel(self):
        panel = QFrame(); panel.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(panel)
        
        self.details_title = QLabel("请选择一个部件进行分析")
        self.details_title.setStyleSheet("font-size: 14pt;")
        
        self.health_plot = pg.PlotWidget()
        self.health_plot.setBackground('#263238')
        
        self.rul_label = QLabel("<b>预测剩余寿命 (RUL):</b> N/A")
        self.suggestion_label = QLabel("<b>维护建议:</b> N/A")
        
        layout.addWidget(self.details_title)
        layout.addWidget(self.health_plot)
        layout.addWidget(self.rul_label)
        layout.addWidget(self.suggestion_label)
        return panel

    def _calculate_all_health(self):
        """遍历所有部件并计算健康度"""
        for node in self.nodes.values():
            score = self._calculate_health_score(node.name, node.data)
            node.health_score = score
            node.update_health_color()

    def _calculate_health_score(self, component_name, data):
        """核心算法 1: 健康度评估引擎"""
        score = 100.0
        
        # 1. 趋势分析 (移动平均)
        window_size = 50
        moving_avg = np.convolve(data, np.ones(window_size)/window_size, mode='valid')
        if len(moving_avg) > 1 and moving_avg[-1] > moving_avg[0] * 1.1: # 如果近期平均值比早期高10%
            score -= 20
            
        # 2. 波动性分析 (标准差)
        std_dev = np.std(data)
        if component_name == 'gearbox' and std_dev > 0.8: # 减速箱振动过大
            score -= 30
            
        # 3. 峰值检测
        max_val = np.max(data)
        if component_name == 'heater' and max_val > 105: # 加热器曾经过热
            score -= 25
        if component_name == 'motor' and max_val > 15: # 电机电流过载
            score -= 25
        
        return max(0, score)

    def _on_node_clicked(self, node):
        """当点击拓扑图节点时，更新右侧面板"""
        self.details_title.setText(f"{node.name} - 详细分析")
        
        # --- 核心算法 2: RUL 预测 (线性回归) ---
        # 模拟历史健康度（假设健康度随时间线性下降）
        time_points = np.arange(10)
        historical_scores = np.linspace(node.health_score + random.randint(5, 15), node.health_score, 10)
        
        # 简单线性回归: y = mx + c
        x = time_points
        y = historical_scores
        m, c = np.polyfit(x, y, 1)

        rul_days = "N/A"
        if m < 0: # 只有在下降趋势时才预测
            fault_threshold = 20 # 假设健康度低于20为故障
            days_to_fault = (fault_threshold - c) / m
            remaining_days = days_to_fault - len(time_points)
            if remaining_days > 0:
                rul_days = f"{remaining_days:.1f} 天"
        
        self.rul_label.setText(f"<b>预测剩余寿命 (RUL):</b> {rul_days}")

        # 更新图表
        self.health_plot.clear()
        self.health_plot.setTitle(f"{node.name} 历史健康度趋势")
        self.health_plot.plot(x, y, pen='c', symbol='o', name='历史健康度')
        if m < 0: # 绘制预测趋势线
            predict_x = np.arange(int(days_to_fault) + 1)
            predict_y = m * predict_x + c
            self.health_plot.plot(predict_x, predict_y, pen=pg.mkPen('r', style=Qt.DotLine), name='预测趋势')
        self.health_plot.addLegend()

        # 生成维护建议
        if node.health_score < 50:
            suggestion = "立即检查，计划更换"
        elif node.health_score < 80:
            suggestion = "增加检查频率，注意异常"
        else:
            suggestion = "状态良好，按计划维护"
        self.suggestion_label.setText(f"<b>维护建议:</b> {suggestion}")

    def _create_mock_data(self):
        """模拟设备各部件在过去一段时间的传感器数据"""
        n_points = 1000
        self.db = {
            # 驱动电机电流 (A)，正常10A，后期有上升趋势
            'motor_current': 10 + np.linspace(0, 3, n_points) + np.random.randn(n_points) * 0.5,
            # 减速箱振动 (mm/s)，正常<0.5，后期波动变大
            'gearbox_vibration': 0.3 + np.linspace(0, 0.8, n_points)**2 + np.random.randn(n_points) * 0.2,
            # 加热器温度 (°C)，正常90°C，有几次过热峰值
            'heater_temp': 90 + np.random.randn(n_points) * 1.5
        }
        # 制造峰值
        self.db['heater_temp'][300] = 108
        self.db['heater_temp'][700] = 106
      