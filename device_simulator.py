# device_simulator.py
import time
import random
from PyQt5.QtCore import QThread, pyqtSignal

class LineSimulatorThread(QThread):
    data_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = False
        self.is_paused = False
        self.mode = 'normal' # 'normal', 'high_speed', 'energy_saving'
        self.reset_state()

    def set_mode(self, mode):
        """外部接口，用于切换仿真模式"""
        if mode in ['normal', 'high_speed', 'energy_saving']:
            self.mode = mode
            print(f"仿真模式已切换到: {mode}")

    def reset_state(self):
        # ... (此方法保持不变)
        self.devices = {
            'extruder': {'name': '挤出机', 'status': 'idle', 'temp': 85.0, 'pressure': 0.0},
            'cooling_tank': {'name': '冷却水槽', 'status': 'idle', 'temp': 25.0, 'level': 80.0},
            'tractor': {'name': '牵引机', 'status': 'idle', 'speed': 0.0},
            'winder': {'name': '收卷机', 'status': 'idle', 'tension': 0.0},
        }
        self.line_status = 'stopped'; self.fault_timer = 0; self.run_timer = 0

    def run(self):
        self.is_running = True
        while self.is_running:
            while self.is_paused:
                time.sleep(0.1)
                if not self.is_running: return

            self.run_timer += 1
            
            # --- 核心逻辑：根据不同模式调整参数 ---
            speed_factor = 1.0
            power_factor = 1.0
            if self.mode == 'high_speed':
                speed_factor = 1.2
                power_factor = 1.3
            elif self.mode == 'energy_saving':
                speed_factor = 0.8
                power_factor = 0.75
            
            # ... (状态机逻辑基本不变，但应用了上面的因子)
            if self.fault_timer > 0:
                self.line_status = 'fault'; self.fault_timer -= 1
                self.devices['extruder']['status'] = 'fault'; self.devices['tractor']['speed'] = 0
            elif self.run_timer % 30 < 20:
                self.line_status = 'running'
                for device in self.devices.values(): device['status'] = 'running'
                self.devices['extruder']['temp'] += random.uniform(-0.5, 0.5) * power_factor
                self.devices['extruder']['pressure'] = (1.8 + random.uniform(-0.1, 0.1)) * power_factor
                self.devices['cooling_tank']['temp'] += random.uniform(-0.2, 0.2)
                self.devices['tractor']['speed'] = (50.0 + random.uniform(-1, 1)) * speed_factor
                self.devices['winder']['tension'] = 5.0 + random.uniform(-0.2, 0.2)
            else:
                self.line_status = 'idle'
                for device in self.devices.values(): device['status'] = 'idle'
                self.devices['extruder']['pressure'] = 0.0; self.devices['tractor']['speed'] = 0.0
            
            if self.line_status == 'running' and random.random() < 0.05:
                self.fault_timer = 5
            
            self.data_updated.emit({
                'line_status': self.line_status, 'devices': self.devices,
                'total_output': self.run_timer * 1.5 * speed_factor, # 总产量也受速度影响
                'timestamp': time.strftime("%H:%M:%S")
            })
            time.sleep(1)

    def toggle_pause(self): # (为第一个3D页面保留)
        self.is_paused = not self.is_paused

    def stop(self):
        self.is_running = False; self.is_paused = False
        self.quit(); self.wait()