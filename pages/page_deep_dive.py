# pages/page_deep_dive.py
import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QComboBox, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt
import pyqtgraph as pg

class PageDeepDive(QWidget):
    def __init__(self):
        super().__init__()
        
        # --- 存储当前的数据 ---
        self.current_data = {}

        # --- UI 布局 ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        filters_widget = self._create_filters_widget()
        main_layout.addWidget(filters_widget)
        
        content_layout = QHBoxLayout()
        self.plots_widget = self._create_plots_widget()
        self.stats_widget = self._create_stats_widget()
        
        content_layout.addWidget(self.plots_widget, 3)
        content_layout.addWidget(self.stats_widget, 1)
        main_layout.addLayout(content_layout)

        # --- 默认加载数据 ---
        self._load_data()

    def _create_filters_widget(self):
        widget = QFrame(); widget.setFrameShape(QFrame.StyledPanel)
        layout = QHBoxLayout(widget)
        
        layout.addWidget(QLabel("选择设备:"))
        self.device_selector = QComboBox()
        self.device_selector.addItems(["挤出机", "牵引机", "收卷机"])
        
        load_button = QPushButton("加载历史数据")
        load_button.clicked.connect(self._load_data)
        
        layout.addWidget(self.device_selector)
        layout.addWidget(load_button)
        layout.addStretch()
        return widget

    def _create_plots_widget(self):
        win = pg.GraphicsLayoutWidget()
        win.setBackground('#263238')
        
        self.plots = {}
        self.curves = {}
        param_config = {
            'p1': {'title': "参数 1", 'pen': 'y'},
            'p2': {'title': "参数 2", 'pen': 'c'},
            'p3': {'title': "参数 3", 'pen': 'g'},
        }
        
        for i, (key, config) in enumerate(param_config.items()):
            plot = win.addPlot(row=i, col=0, title=config['title'])
            if i > 0:
                plot.setXLink(list(self.plots.values())[0]) # 同步X轴
            self.plots[key] = plot
            self.curves[key] = plot.plot(pen=config['pen'])
            
        # --- 核心逻辑 2 & 3: 区域分析与十字光标 ---
        self.region = pg.LinearRegionItem()
        self.region.setZValue(10)
        self.plots['p1'].addItem(self.region, ignoreBounds=True)
        self.region.sigRegionChanged.connect(self._update_stats_from_region)
        
        self.v_lines = [pg.InfiniteLine(angle=90, movable=False) for _ in self.plots]
        self.data_labels = [pg.TextItem(color='w') for _ in self.plots]
        for i, p in enumerate(self.plots.values()):
            p.addItem(self.v_lines[i], ignoreBounds=True)
            p.addItem(self.data_labels[i], ignoreBounds=True)
        
        # 创建一个代理来连接所有绘图区域的鼠标移动事件
        proxy = pg.SignalProxy(self.plots['p1'].scene().sigMouseMoved, rateLimit=60, slot=self._mouse_moved)
        self.plots['p1'].scene().proxy = proxy # 防止被垃圾回收
        
        return win

    def _create_stats_widget(self):
        box = QGroupBox("区域统计分析")
        layout = QGridLayout(box)
        layout.setHorizontalSpacing(15)
        
        headers = ["", "最大值", "最小值", "平均值", "标准差"]
        self.param_names_labels = []
        self.stat_labels = []

        for col, header in enumerate(headers):
            layout.addWidget(QLabel(f"<b>{header}</b>"), 0, col, Qt.AlignRight)
            
        for row in range(3): # 最多显示3个参数
            name_label = QLabel(f"<b>参数 {row+1}</b>"); self.param_names_labels.append(name_label)
            layout.addWidget(name_label, row + 1, 0)
            row_labels = []
            for col in range(len(headers) - 1):
                label = QLabel("N/A"); label.setAlignment(Qt.AlignRight); row_labels.append(label)
                layout.addWidget(label, row + 1, col + 1)
            self.stat_labels.append(row_labels)
        
        return box

    def _load_data(self):
        """根据选择的设备加载不同的模拟数据"""
        device = self.device_selector.currentText()
        n_points = 5000
        time_data = np.arange(n_points)
        self.current_data = {'time': time_data}

        # 清除旧的事件标记
        for p in self.plots.values():
            for item in p.items[:]: # 复制列表以安全地移除
                if isinstance(item, (pg.InfiniteLine, pg.TextItem)) and not item in self.v_lines + self.data_labels:
                    p.removeItem(item)

        if device == "挤出机":
            self.current_data['temp'] = 85 + np.random.randn(n_points) * 2
            self.current_data['pressure'] = 1.8 + np.random.randn(n_points) * 0.1
            self.current_data['power'] = 25 + np.random.randn(n_points) * 0.5
            
            # 模拟事件
            fault_start, fault_end = 2000, 2200
            self.current_data['temp'][fault_start:fault_end] += np.linspace(0, 10, fault_end - fault_start)
            self.current_data['pressure'][fault_start:fault_end] += np.linspace(0, 0.8, fault_end - fault_start)
            events = {1000: "换料开始", fault_start: "压力过载报警"}
            
            self._update_plots(['temp', 'pressure', 'power'], 
                               ["温度 (°C)", "压力 (MPa)", "功率 (kW)"])
        
        elif device == "牵引机":
            self.current_data['speed'] = 50 + np.random.randn(n_points) * 1.5
            self.current_data['torque'] = 120 + np.random.randn(n_points) * 5
            self.current_data['vibration'] = 0.1 + np.random.rand(n_points) * 0.05
            
            # 模拟事件
            fault_start, fault_end = 3000, 3100
            self.current_data['speed'][fault_start:fault_end] = 0
            self.current_data['torque'][fault_start:fault_end] *= 1.5
            events = {1500: "速度调整", fault_start: "电机堵转"}
            
            self._update_plots(['speed', 'torque', 'vibration'],
                               ["速度 (m/min)", "扭矩 (N·m)", "振动 (mm/s)"])

        # 添加事件标记
        for timestamp, label in events.items():
            line = pg.InfiniteLine(angle=90, movable=False, pen='r')
            line.setPos(timestamp)
            text = pg.TextItem(label, color='r', anchor=(0, 1))
            text.setPos(timestamp, self.plots['p1'].vb.viewRange()[1][1])
            self.plots['p1'].addItem(line); self.plots['p1'].addItem(text)
            
        self.region.setRegion([n_points * 0.4, n_points * 0.5])
        self._update_stats_from_region() # 加载后立即计算一次初始区域的统计

    def _update_plots(self, data_keys, titles):
        """更新所有图表的标题和数据"""
        for i, key in enumerate(data_keys):
            plot_key = f'p{i+1}'
            self.plots[plot_key].setTitle(titles[i])
            self.curves[plot_key].setData(self.current_data['time'], self.current_data[key])
            self.param_names_labels[i].setText(f"<b>{titles[i].split(' ')[0]}</b>")
        
        # 隐藏未使用的图表和标签
        for i in range(len(data_keys), 3):
            self.plots[f'p{i+1}'].hide()
            self.param_names_labels[i].hide()
            for label in self.stat_labels[i]: label.hide()
        
        for i in range(len(data_keys)):
            self.plots[f'p{i+1}'].show()
            self.param_names_labels[i].show()
            for label in self.stat_labels[i]: label.show()

    def _update_stats_from_region(self):
        minX, maxX = self.region.getRegion()
        time_data = self.current_data.get('time', np.array([]))
        if len(time_data) == 0: return

        idx1, idx2 = np.searchsorted(time_data, [minX, maxX])
        if idx1 == idx2: return

        for i, (param_label, stat_row) in enumerate(zip(self.param_names_labels, self.stat_labels)):
            if not param_label.isVisible(): continue
            
            # 从图表标题获取数据key
            param_key = list(self.current_data.keys())[i+1] # 简单映射
            data_slice = self.current_data[param_key][idx1:idx2]
            
            if len(data_slice) > 0:
                stats = [np.max(data_slice), np.min(data_slice), np.mean(data_slice), np.std(data_slice)]
                for j, label in enumerate(stat_row):
                    label.setText(f"{stats[j]:.2f}")
            else:
                for label in stat_row: label.setText("N/A")
                
    def _mouse_moved(self, evt):
        pos = evt[0]
        for i, p in enumerate(self.plots.values()):
            if p.sceneBoundingRect().contains(pos):
                mouse_point = p.vb.mapSceneToView(pos)
                index = int(mouse_point.x())
                if 0 <= index < len(self.current_data['time']):
                    # 更新所有垂直线的位置
                    for v_line in self.v_lines: v_line.setPos(mouse_point.x())
                    
                    # 更新所有数据标签
                    for j, (key, curve) in enumerate(self.curves.items()):
                        if self.plots[key].isVisible():
                            y_val = curve.yData[index]
                            self.data_labels[j].setText(f"{y_val:.2f}")
                            self.data_labels[j].setPos(mouse_point.x(), y_val)