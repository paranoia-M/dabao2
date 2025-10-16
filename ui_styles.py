# ui_styles.py
MODERN_STYLE = """
/* ---- Global Styles ---- */
QWidget {
    background-color: #2c3e50;
    color: #ecf0f1;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

/* ---- QMainWindow ---- */
QMainWindow {
    background-color: #34495e;
}

/* ---- QPushButton ---- */
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #2980b9;
}
QPushButton:pressed {
    background-color: #1f618d;
}

/* ---- QLineEdit ---- */
QLineEdit {
    background-color: #2c3e50;
    border: 1px solid #34495e;
    padding: 6px;
    border-radius: 4px;
    color: #ecf0f1;
}
QLineEdit:focus {
    border: 1px solid #3498db;
}

/* ---- QMenuBar ---- */
QMenuBar {
    background-color: #34495e;
    color: #ecf0f1;
}
QMenuBar::item {
    background-color: transparent;
    padding: 4px 10px;
}
QMenuBar::item:selected {
    background-color: #3498db;
}

/* ---- QMenu ---- */
QMenu {
    background-color: #34495e;
    border: 1px solid #2c3e50;
}
QMenu::item {
    padding: 4px 20px;
}
QMenu::item:selected {
    background-color: #3498db;
}

/* ---- QTabWidget ---- */
QTabWidget::pane {
    border: 1px solid #2c3e50;
    border-radius: 4px;
}
QTabBar::tab {
    background: #34495e;
    color: #ecf0f1;
    padding: 8px 20px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    border: 1px solid #2c3e50;
}
QTabBar::tab:selected {
    background: #3498db;
    color: white;
}

/* ---- QStatusBar ---- */
QStatusBar {
    background-color: #34495e;
    color: #bdc3c7;
}

/* ---- QMessageBox ---- */
QMessageBox {
    background-color: #34495e;
}
QMessageBox QLabel {
    color: #ecf0f1;
}
/* ---- QStatusBar ---- */
QStatusBar {
    background-color: #34495e;
    color: #bdc3c7;
}

/* ---- QMessageBox ---- */
QMessageBox {
    background-color: #34495e;
}
QMessageBox QLabel {
    color: #ecf0f1;
}

/* ---- 新增: 自定义标题样式 ---- */
QLabel#titleLabel {
    font-size: 16pt;
    font-weight: bold;
    color: #ecf0f1;
    padding-bottom: 10px;
}
"""