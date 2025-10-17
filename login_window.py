# login_window.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
                             QMessageBox, QTabWidget, QWidget, QFormLayout, QLabel, QFrame)
from PyQt5.QtCore import Qt
import user_manager

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("系统登录")
        self.username = ""

        # --- 1. 基础布局改为左右分栏 (QHBoxLayout) ---
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0) # 移除边距，让面板填满窗口
        main_layout.setSpacing(0)

        # --- 2. 创建左侧的品牌/标题面板 ---
        left_panel = self._create_left_panel()
        
        # --- 3. 创建右侧的登录表单面板 ---
        right_panel = self._create_right_panel()

        main_layout.addWidget(left_panel, 1) # 左侧占1份
        main_layout.addWidget(right_panel, 2) # 右侧占2份

    def _create_left_panel(self):
        """创建左侧的品牌信息面板"""
        panel = QFrame()
        # 使用更深的背景色
        panel.setStyleSheet("background-color: #263238;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # --- 4. 更新系统标题 ---
        title_label = QLabel("信息传输技术服务")
        title_label.setObjectName("mainTitle")
        title_label.setStyleSheet("""
            font-size: 28pt; 
            font-weight: bold; 
            color: white;
        """)
        
        subtitle_label = QLabel("后台管理系统")
        subtitle_label.setObjectName("subTitle")
        subtitle_label.setStyleSheet("""
            font-size: 24pt; 
            color: #B0BEC5; 
            padding-bottom: 20px;
        """)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        # 使用青色作为强调色
        separator.setStyleSheet("background-color: #00BCD4; height: 2px; border: none;")

        description_label = QLabel("通过实时数据映射与智能分析，\n构建物理世界的虚拟镜像，\n赋能生产决策。")
        description_label.setWordWrap(True)
        description_label.setStyleSheet("font-size: 11pt; color: #78909C; padding-top: 20px;")
        
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(separator)
        layout.addWidget(description_label)
        layout.addStretch()
        
        return panel

    def _create_right_panel(self):
        """创建右侧的登录和注册表单"""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignCenter) # 垂直居中内容
        
        self.tab_widget = QTabWidget()
        self.login_tab = QWidget()
        self.register_tab = QWidget()

        self.tab_widget.addTab(self.login_tab, "登录")
        self.tab_widget.addTab(self.register_tab, "注册")
        
        # 限制表单区域的宽度，使其在面板中居中
        tab_container = QWidget()
        tab_layout = QVBoxLayout(tab_container)
        tab_layout.addWidget(self.tab_widget)
        tab_container.setFixedWidth(400)

        self.setup_login_tab()
        self.setup_register_tab()

        hint_label = QLabel("提示测试账号：admin  密码：123456")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("color: #78909C; font-size: 9pt;")
        
        layout.addWidget(tab_container)
        layout.addSpacing(15)
        layout.addWidget(hint_label)
        
        return panel

    def setup_login_tab(self):
        layout = QFormLayout(self.login_tab)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20) 
        font = self.font(); font.setPointSize(11); self.login_tab.setFont(font)

        self.login_user_input = QLineEdit()
        self.login_pass_input = QLineEdit()
        self.login_pass_input.setEchoMode(QLineEdit.Password)
        
        self.login_button = QPushButton("登 录")
        self.login_button.setMinimumHeight(45)

        layout.addRow("用户名:", self.login_user_input)
        layout.addRow("密  码:", self.login_pass_input)
        layout.addRow("", self.login_button)

        self.login_button.clicked.connect(self.handle_login)
        self.login_user_input.returnPressed.connect(self.handle_login)
        self.login_pass_input.returnPressed.connect(self.handle_login)

    def setup_register_tab(self):
        layout = QFormLayout(self.register_tab)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        font = self.font(); font.setPointSize(11); self.register_tab.setFont(font)
        
        self.reg_user_input = QLineEdit()
        self.reg_pass_input = QLineEdit()
        self.reg_pass_input.setEchoMode(QLineEdit.Password)
        self.reg_confirm_pass_input = QLineEdit()
        self.reg_confirm_pass_input.setEchoMode(QLineEdit.Password)

        self.register_button = QPushButton("注 册")
        self.register_button.setMinimumHeight(45)

        layout.addRow("用 户 名:", self.reg_user_input)
        layout.addRow("设置密码:", self.reg_pass_input)
        layout.addRow("确认密码:", self.reg_confirm_pass_input)
        layout.addRow("", self.register_button)

        self.register_button.clicked.connect(self.handle_register)

    # handle_login 和 handle_register 方法保持不变
    def handle_login(self):
        username = self.login_user_input.text()
        password = self.login_pass_input.text()
        if user_manager.verify_user(username, password):
            self.username = username
            self.accept()
        else:
            QMessageBox.warning(self, "登录失败", "用户名或密码错误！")

    def handle_register(self):
        username = self.reg_user_input.text()
        password = self.reg_pass_input.text()
        confirm_password = self.reg_confirm_pass_input.text()
        if password != confirm_password:
            QMessageBox.warning(self, "注册失败", "两次输入的密码不一致！")
            return
        success, message = user_manager.add_user(username, password)
        if success:
            QMessageBox.information(self, "注册成功", message + "，请返回登录。")
            self.tab_widget.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "注册失败", message)