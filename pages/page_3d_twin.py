# pages/page_3d_twin.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
import pyvista as pv
from pyvistaqt import QtInteractor # pyvista 与 PyQt 集成的关键组件

from device_simulator import LineSimulatorThread

class Page3DTwin(QWidget):
    def __init__(self):
        super().__init__()
        
        # --- 1. 创建 PyVista 的绘图器和 PyQt 窗口 ---
        self.plotter = QtInteractor(self)
        
        # --- 2. 布局 ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plotter.interactor) # 将 pyvista 的窗口嵌入布局

        # --- 3. 初始化3D场景 ---
        self.setup_scene()

        # --- 4. 启动模拟器 ---
        # (我们将使用 QTimer 来从模拟器拉取数据，这是一种更稳健的方式)
        self.simulator = LineSimulatorThread(self)
        self.simulator.start()

        # --- 5. 设置一个定时器来周期性更新UI ---
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_3d_scene)
        self.update_timer.start(1000) # 每1000毫秒 (1秒) 更新一次
        
    def setup_scene(self):
        """使用 PyVista API 创建3D场景"""
        self.plotter.set_background("#34495e") # 设置背景色
        
        # 创建地面
        ground = pv.Plane(center=(0, -0.5, 0), direction=(0, 1, 0), i_size=40, j_size=20)
        self.plotter.add_mesh(ground, color="#455A64")

        # --- 创建设备模型 ---
        self.devices_3d = {
            'extruder': self._create_machine("挤出机", (-10, 1, 0), (3, 3, 3)),
            'cooling_tank': self._create_machine("冷却水槽", (-3, 0, 0), (6, 1, 2)),
            'tractor': self._create_machine("牵引机", (4, 0.5, 0), (2, 2, 2)),
            'winder': self._create_machine("收卷机", (10, 1, 0), (3, 3, 3)),
        }
        
        # --- 创建产品模型 (一个小球) ---
        self.product_actor = self.plotter.add_mesh(pv.Sphere(radius=0.3), color="lightblue", name="product")
        self.product_actor.SetVisibility(False) # 初始隐藏

        # 设置相机初始位置
        self.plotter.camera_position = [(0, 10, 25), (0, 0, 0), (0, 1, 0)]
        
    def _create_machine(self, name, position, size):
        """创建一个设备（长方体）并添加到场景中"""
        machine = pv.Cube(center=position, x_length=size[0], y_length=size[1], z_length=size[2])
        actor = self.plotter.add_mesh(machine, color="#B0BEC5", name=name)
        return actor

    def update_3d_scene(self):
        """核心逻辑：从模拟器获取最新数据并更新3D场景"""
        # 注意：这里我们直接访问模拟器线程的属性
        # 在简单场景下是可行的，因为Python的GIL提供了一定的线程安全
        data = {
            'line_status': self.simulator.line_status,
            'devices': self.simulator.devices,
            'total_output': self.simulator.run_timer * 1.5,
        }

        status_colors = {
            'running': "#4CAF50",
            'idle': "#FFC107",
            'fault': "#D32F2F",
        }
        
        # 更新设备颜色
        for key, device_actor in self.devices_3d.items():
            status = data['devices'][key]['status']
            color = status_colors.get(status, "#B0BEC5")
            device_actor.prop.color = color
            
        # 更新产品流动动画
        if data['line_status'] == 'running':
            self.product_actor.SetVisibility(True)
            progress = (data['total_output'] % 100) / 100.0
            x_pos = -10 + progress * 20
            self.product_actor.position = (x_pos, 1.5, 0)
        else:
            self.product_actor.SetVisibility(False)
            
    def closeEvent(self, event):
        """确保在窗口关闭时停止后台线程和定时器"""
        print("关闭3D孪生页面，正在停止模拟器和定时器...")
        self.update_timer.stop()
        if hasattr(self, 'simulator'):
            self.simulator.stop()
        self.plotter.close() # 关闭 pyvista 渲染器
        super().closeEvent(event)