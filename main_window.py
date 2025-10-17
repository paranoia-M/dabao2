# main_window.py

from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QWidget, QHBoxLayout, QAction
from PyQt5.QtCore import Qt

# --- 不再导入任何 pages, 只导入核心模块 ---
import user_manager
from widgets.side_menu import SideMenu
import router # <-- 导入新的路由模块

class MainWindow(QMainWindow):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle("信息传输技术服务后台管理系统")

        self.logout_triggered = False

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.side_menu = SideMenu()
        self.stacked_widget = QStackedWidget()
        
        main_layout.addWidget(self.side_menu)
        main_layout.addWidget(self.stacked_widget)
        
        self.pages = {}

        self.init_ui()
        self._create_actions_menu()

    def init_ui(self):
        self.side_menu.page_changed.connect(self.switch_page)
        self.populate_menu()
        self.statusBar().showMessage(f"欢迎您，{self.username}！")
        self.switch_page("dashboard")
        self.side_menu.set_current_item_by_key("dashboard")

    def populate_menu(self):
        """向侧边栏添加所有菜单项"""
        self.side_menu.add_menu_item("系统总览", "dashboard")
        self.side_menu.add_menu_item("信息三维模型", "3d_twin")
        self.side_menu.add_menu_item("信息参数深潜", "deep_dive")
        self.side_menu.add_menu_item("信息质量视觉", "quality_vision")
        self.side_menu.add_menu_item("设备健康诊断", "health_diagnosis")
        self.side_menu.add_menu_item("能耗与物耗模型", "consumption_model")
        self.side_menu.add_menu_item("仿真与优化推演", "simulation")

    def switch_page(self, page_key):
        """核心路由函数，现在调用 router 模块"""
        if page_key not in self.pages:
            # --- 核心改动：调用 router 来创建页面 ---
            widget = router.get_page_widget(page_key)
            
            self.stacked_widget.addWidget(widget)
            self.pages[page_key] = widget

        widget_to_show = self.pages[page_key]
        self.stacked_widget.setCurrentWidget(widget_to_show)
        
        current_item = self.side_menu.list_widget.currentItem()
        if current_item:
             self.statusBar().showMessage(f"当前页面: {current_item.text()}")

    # --- get_page_widget 和 create_placeholder_page 方法已被移除 ---

    def _create_actions_menu(self):
        menu_bar = self.menuBar()
        user_menu = menu_bar.addMenu(f"用户: {self.username}")
        logout_action = QAction("登出", self)
        logout_action.triggered.connect(self._handle_logout)
        user_menu.addAction(logout_action)

    def _handle_logout(self):
        user_manager.logout_user()
        self.logout_triggered = True
        self.close()

    def closeEvent(self, event):
        print("主窗口正在关闭，通知所有子页面...")
        for page in self.pages.values():
            if hasattr(page, 'closeEvent') and callable(page.closeEvent):
                page.closeEvent(event)
        super().closeEvent(event)