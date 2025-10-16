# widgets/side_menu.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PyQt5.QtCore import pyqtSignal, QSize, Qt
# from qt_material import get_icon  <- 我们移除了这一行

class SideMenu(QWidget):
    # 定义一个信号，当页面需要切换时发出，参数为页面的key(str)
    page_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200) # 设置侧边栏的固定宽度

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0) # 移除边距
        self.layout.setSpacing(0)

        self.list_widget = QListWidget()
        # 使用样式表自定义外观
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #263238; /* 深色背景 */
                border: none;
                padding-top: 20px;
                font-size: 11pt;
            }
            QListWidget::item {
                padding: 15px 20px;
                color: #B0BEC5; /* 未选中时的文字颜色 */
            }
            QListWidget::item:hover {
                background-color: #37474F; /* 悬停时的背景色 */
            }
            QListWidget::item:selected {
                background-color: #00796B; /* 选中时的背景色 */
                color: white; /* 选中时的文字颜色 */
                border-left: 4px solid #00BCD4; /* 左侧高亮条 */
            }
        """)
        # self.list_widget.setIconSize(QSize(24, 24)) # <- 我们移除了这一行

        # 连接item点击事件到我们的槽函数
        self.list_widget.currentItemChanged.connect(self.on_item_changed)
        
        self.layout.addWidget(self.list_widget)

    def add_menu_item(self, text, page_key):
        """向菜单列表添加一个项目 (已移除图标参数)"""
        item = QListWidgetItem()
        item.setText(text) # 直接设置文本，不再需要为图标留空
        # item.setIcon(get_icon(icon_name)) # <- 我们移除了这一行
        
        # 将 page_key 存储在 item 的数据中，以便之后获取
        item.setData(Qt.UserRole, page_key)
        
        self.list_widget.addItem(item)
    
    def on_item_changed(self, current_item, previous_item):
        """当选择的项目改变时触发"""
        if current_item:
            page_key = current_item.data(Qt.UserRole)
            self.page_changed.emit(page_key) # 发出信号
            
    def set_current_item_by_key(self, page_key):
        """通过page_key来设置当前选中的项目"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) == page_key:
                item.setSelected(True)
                self.list_widget.setCurrentItem(item)
                break