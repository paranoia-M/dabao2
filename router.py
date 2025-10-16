# router.py
# 这个文件是所有页面的“工厂”，专门负责创建页面实例。

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

# --- 在这里导入所有的页面类 ---
from pages.page_dashboard import PageDashboard 
from pages.page_3d_twin import Page3DTwin
from pages.page_deep_dive import PageDeepDive
from pages.page_quality_vision import PageQualityVision
from pages.page_health_diagnosis import PageHealthDiagnosis
from pages.page_consumption_model import PageConsumptionModel
from pages.page_simulation import PageSimulation # <-- 新增导入

def create_placeholder_page(text):
    """一个辅助函数，用于快速创建占位符页面"""
    page = QWidget()
    layout = QVBoxLayout(page)
    label = QLabel(text)
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("font-size: 24pt; color: #78909C;")
    layout.addWidget(label)
    return page

def get_page_widget(page_key):
    """根据 key 返回对应的页面实例"""
    if page_key == "dashboard": return PageDashboard()
    if page_key == "3d_twin": return Page3DTwin()
    if page_key == "deep_dive": return PageDeepDive()
    if page_key == "quality_vision": return PageQualityVision()
    if page_key == "health_diagnosis": return PageHealthDiagnosis()
    if page_key == "consumption_model": return PageConsumptionModel()
    if page_key == "simulation": return PageSimulation() # <-- 新增路由
        
    # 如果传入一个未知的 key，返回一个错误提示页面
    return create_placeholder_page(f"错误: 页面 '{page_key}' 未定义")