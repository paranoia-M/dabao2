# pages/page_dashboard.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QGraphicsView, QGraphicsScene, QGridLayout, QListWidget)
from PyQt5.QtCore import Qt
from collections import deque
import pyqtgraph as pg

from device_simulator import LineSimulatorThread
from .widgets.digital_twin_widgets import MachineItem

class PageDashboard(QWidget):
    def __init__(self):
        super().__init__()
        
        # 数据存储
        self.max_data_points = 60
        self.temp_data = deque(maxlen=self.max_data_points)
        self.pressure_data = deque(maxlen=self.max_data_points)

        # UI 布局
        main_layout = QGridLayout(self)
        main_layout.setSpacing(20)

        twin_box = self._create_twin_visualization()
        main_layout.addWidget(twin_box, 0, 0, 1, 2)

        charts_box = self._create_live_charts()
        main_layout.addWidget(charts_box, 1, 0)

        status_box = self._create_status_log()
        main_layout.addWidget(status_box, 1, 1)

        main_layout.setColumnStretch(0, 3)
        main_layout.setColumnStretch(1, 2)

        # 启动后台模拟器
        self.simulator = LineSimulatorThread(self)
        self.simulator.data_updated.connect(self.update_ui)
        self.simulator.start()
        
    def _create_twin_visualization(self):
        box = QFrame(); box.setFrameShape(QFrame.StyledPanel); layout = QVBoxLayout(box)
        title = QLabel("生产线数字孪生模型"); title.setStyleSheet("font-size: 16pt;")
        scene = QGraphicsScene(); scene.setSceneRect(0, 0, 800, 150)
        self.twin_view = QGraphicsView(scene)
        self.machine_items = {
            'extruder': MachineItem("挤出机", 50, 25, 120, 100), 'cooling_tank': MachineItem("冷却水槽", 220, 50, 200, 50),
            'tractor': MachineItem("牵引机", 470, 50, 100, 50), 'winder': MachineItem("收卷机", 620, 25, 120, 100),
        }
        for item in self.machine_items.values(): scene.addItem(item)
        scene.addRect(170, 65, 50, 20, brush=pg.mkBrush(0.5)); scene.addRect(420, 65, 50, 20, brush=pg.mkBrush(0.5)); scene.addRect(570, 65, 50, 20, brush=pg.mkBrush(0.5))
        layout.addWidget(title); layout.addWidget(self.twin_view)
        return box
        
    def _create_live_charts(self):
        box = QFrame(); box.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(box)
        
        title = QLabel("关键参数实时曲线"); title.setStyleSheet("font-size: 14pt;")
        layout.addWidget(title)

        # --- 1. 修改：在这里创建并持有 PlotWidget 的引用 ---
        self.temp_plot_widget = pg.PlotWidget()
        self.pressure_plot_widget = pg.PlotWidget()

        # --- 2. 修改：将 PlotWidget 传递给 setup 函数，并只接收返回的 curve ---
        self.temp_plot_curve = self._setup_plot(self.temp_plot_widget, "挤出机温度 (°C)", (80, 95))
        self.pressure_plot_curve = self._setup_plot(self.pressure_plot_widget, "挤出机压力 (MPa)", (0, 2.5))
        
        # --- 3. 修改：将 PlotWidget (画布) 而不是 curve 添加到布局中 ---
        layout.addWidget(self.temp_plot_widget)
        layout.addWidget(self.pressure_plot_widget)
        
        return box

    def _setup_plot(self, plot_widget, title, y_range):
        """此方法现在接收一个 PlotWidget，并在其上绘图后，返回曲线对象"""
        plot_widget.setBackground('#263238')
        plot_widget.setTitle(title, color="#B0BEC5", size="12pt")
        plot_widget.setYRange(*y_range)
        plot_widget.showGrid(x=True, y=True, alpha=0.3)
        # 只返回 PlotDataItem (曲线)
        return plot_widget.plot(pen=pg.mkPen(color='#00BCD4', width=2))

    def _create_status_log(self):
        box = QFrame(); box.setFrameShape(QFrame.StyledPanel); layout = QVBoxLayout(box)
        title = QLabel("状态与事件日志"); title.setStyleSheet("font-size: 14pt;")
        self.line_status_label = QLabel("生产线状态: <b style='color:#FFC107;'>初始化中...</b>")
        self.output_label = QLabel("今日产量: 0 米")
        self.log_list = QListWidget()
        layout.addWidget(title); layout.addWidget(self.line_status_label); layout.addWidget(self.output_label); layout.addWidget(self.log_list)
        return box
        
    def update_ui(self, data):
        devices_data = data['devices']
        for key, item in self.machine_items.items():
            item.set_status(devices_data[key]['status'])
            
        status_map = {'running': '运行中', 'idle': '待机', 'fault': '故障', 'stopped': '已停止'}
        color_map = {'running': '#4CAF50', 'idle': '#FFC107', 'fault': '#D32F2F', 'stopped': 'gray'}
        line_status_text = status_map.get(data['line_status'], '未知')
        line_status_color = color_map.get(data['line_status'], 'white')
        self.line_status_label.setText(f"生产线状态: <b style='color:{line_status_color};'>{line_status_text}</b>")
        self.output_label.setText(f"今日产量: {data['total_output']:.1f} 米")
        
        self.temp_data.append(devices_data['extruder']['temp'])
        self.pressure_data.append(devices_data['extruder']['pressure'])
        self.temp_plot_curve.setData(list(self.temp_data))
        self.pressure_plot_curve.setData(list(self.pressure_data))
        
        if data['line_status'] == 'fault' and (self.log_list.count() == 0 or self.log_list.item(0).text().find("故障") == -1):
             self.log_list.insertItem(0, f"[{data['timestamp']}] 严重: 生产线发生故障！")
        elif data['line_status'] == 'running' and (self.log_list.count() == 0 or self.log_list.item(0).text().find("启动") == -1):
             self.log_list.insertItem(0, f"[{data['timestamp']}] 信息: 生产线启动运行。")
             
    def closeEvent(self, event):
        """确保在窗口关闭时停止后台线程"""
        print("关闭数字孪生页面，正在停止模拟器线程...")
        self.simulator.stop()
        super().closeEvent(event)