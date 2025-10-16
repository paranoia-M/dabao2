# pages/page_simulation.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QGroupBox, QDoubleSpinBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QSplitter, 
                             QProgressBar) # <-- 核心修正点：在这里添加 QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import pyqtgraph as pg
import numpy as np
from functools import partial

from .widgets.simulation_kernel import SimulationKernel, GeneticOptimizer

class OptimizationThread(QThread):
    """将耗时的优化算法放在后台线程中"""
    finished = pyqtSignal(dict)
    # 我们可以通过修改GA来报告进度，但为了简化，我们只在结束后报告
    # progress = pyqtSignal(int)

    def __init__(self, optimizer, parent=None):
        super().__init__(parent)
        self.optimizer = optimizer

    def run(self):
        best_individual = self.optimizer.run_optimization()
        self.finished.emit(best_individual)

class PageSimulation(QWidget):
    def __init__(self):
        super().__init__()
        self.kernel = SimulationKernel()
        
        main_layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        
        left_panel = self._create_manual_simulation_panel()
        right_panel = self._create_auto_optimization_panel()
        
        splitter.addWidget(left_panel); splitter.addWidget(right_panel)
        splitter.setSizes([int(self.width() * 0.5), int(self.width() * 0.5)]) # 均分
        main_layout.addWidget(splitter)

    def _create_manual_simulation_panel(self):
        panel = QGroupBox("手动仿真与方案对比 (What-If Analysis)")
        layout = QVBoxLayout(panel)
        
        input_layout = QHBoxLayout()
        self.temp_input = self._create_param_input("温度 (°C)", 80, 100, 90)
        self.speed_input = self._create_param_input("速度 (m/min)", 40, 60, 50)
        run_sim_button = QPushButton("运行此方案"); run_sim_button.clicked.connect(self._run_single_simulation)
        input_layout.addWidget(self.temp_input); input_layout.addWidget(self.speed_input); input_layout.addWidget(run_sim_button)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels(["方案名", "温度(°C)", "速度(m/min)", "产量(米)", "单位能耗(kWh/米)", "缺陷率(%)"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addLayout(input_layout)
        layout.addWidget(self.results_table)
        return panel

    def _create_param_input(self, name, min_val, max_val, default_val):
        box = QGroupBox(name)
        layout = QVBoxLayout(box)
        spinbox = QDoubleSpinBox(); spinbox.setRange(min_val, max_val); spinbox.setValue(default_val)
        layout.addWidget(spinbox)
        return box
        
    def _run_single_simulation(self):
        params = {
            'temp': self.temp_input.findChild(QDoubleSpinBox).value(),
            'speed': self.speed_input.findChild(QDoubleSpinBox).value()
        }
        results = self.kernel.run(params)
        
        row_count = self.results_table.rowCount()
        self.results_table.insertRow(row_count)
        
        self.results_table.setItem(row_count, 0, QTableWidgetItem(f"方案 {row_count + 1}"))
        self.results_table.setItem(row_count, 1, QTableWidgetItem(f"{params['temp']:.1f}"))
        self.results_table.setItem(row_count, 2, QTableWidgetItem(f"{params['speed']:.1f}"))
        self.results_table.setItem(row_count, 3, QTableWidgetItem(f"{results['output']:.0f}"))
        self.results_table.setItem(row_count, 4, QTableWidgetItem(f"{results['unit_energy']:.3f}"))
        self.results_table.setItem(row_count, 5, QTableWidgetItem(f"{results['defect_rate']:.2%}"))

    def _create_auto_optimization_panel(self):
        panel = QGroupBox("遗传算法自动寻优")
        layout = QVBoxLayout(panel)
        
        self.run_opt_button = QPushButton("开始自动优化"); self.run_opt_button.clicked.connect(self._run_optimization)
        self.opt_progress_bar = QProgressBar(); self.opt_progress_bar.hide()
        
        self.opt_plot = pg.PlotWidget(); self.opt_plot.setBackground('#263238')
        self.opt_plot.setTitle("优化进程 (最佳适应度)"); self.opt_plot.setLabel('left', '适应度分数'); self.opt_plot.setLabel('bottom', '迭代代数')
        self.opt_curve = self.opt_plot.plot(pen='c')
        
        self.result_label = QLabel("<b>推荐的最优方案:</b>\n- 温度: N/A\n- 速度: N/A\n\n<b>预测结果:</b>\n- 产量: N/A\n- 单位能耗: N/A\n- 缺陷率: N/A")
        self.result_label.setWordWrap(True)
        
        layout.addWidget(self.run_opt_button); layout.addWidget(self.opt_progress_bar)
        layout.addWidget(self.opt_plot); layout.addWidget(self.result_label)
        return panel

    def _run_optimization(self):
        param_ranges = {'temp': (80, 100), 'speed': (40, 60)}
        optimizer = GeneticOptimizer(self.kernel, param_ranges)
        
        self.opt_thread = OptimizationThread(optimizer)
        self.opt_thread.finished.connect(self._on_optimization_finished)
        
        self.opt_thread.optimizer.history.clear()
        self.opt_thread.start()
        
        self.opt_progress_bar.show()
        self.opt_progress_bar.setRange(0, 0)
        self.run_opt_button.setEnabled(False)

    def _on_optimization_finished(self, best_params):
        self.opt_progress_bar.hide()
        
        history = self.opt_thread.optimizer.history
        self.opt_curve.setData(history)
        
        results = self.kernel.run(best_params)
        result_text = f"""<b>推荐的最优方案:</b>
- 温度: {best_params['temp']:.2f} °C
- 速度: {best_params['speed']:.2f} m/min

<b>预测结果:</b>
- 产量: {results['output']:.0f} 米
- 单位能耗: {results['unit_energy']:.3f} kWh/米
- 缺陷率: {results['defect_rate']:.2%}"""
        self.result_label.setText(result_text)
        
        self.temp_input.findChild(QDoubleSpinBox).setValue(best_params['temp'])
        self.speed_input.findChild(QDoubleSpinBox).setValue(best_params['speed'])
        self._run_single_simulation()
        
        last_row = self.results_table.rowCount() - 1
        item = QTableWidgetItem("GA优化方案")
        item.setBackground(QColor("#00796B"))
        self.results_table.setItem(last_row, 0, item)
        
        self.run_opt_button.setEnabled(True)