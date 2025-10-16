# main.py

import sys
from PyQt5.QtWidgets import QApplication, QDialog

def main():
    """程序主入口，包含一个循环来处理登出和重新登录"""
    app = QApplication(sys.argv)
    
    # 在 QApplication 实例化后，立即导入并应用 qt_material
    from qt_material import apply_stylesheet
    apply_stylesheet(app, theme='dark_blue.xml')
    
    # 现在，可以安全地导入我们自己的模块了
    import user_manager
    from login_window import LoginDialog
    from main_window import MainWindow

    # 为 QSettings 设置应用信息
    app.setOrganizationName("YourCompany")
    app.setApplicationName("DigitalTwinSystem")

    # 使用一个循环来控制整个应用的生命周期
    while True:
        # 尝试获取已登录的用户
        username = user_manager.get_logged_in_user()
        
        # 如果没有自动登录的用户，则显示登录对话框
        if not username:
            login_dialog = LoginDialog()
            login_dialog.setFixedSize(800, 500)
            
            screen_center = app.primaryScreen().availableGeometry().center()
            login_geometry = login_dialog.frameGeometry()
            login_geometry.moveCenter(screen_center)
            login_dialog.move(login_geometry.topLeft())

            if login_dialog.exec_() == QDialog.Accepted:
                username = login_dialog.username
                user_manager.save_logged_in_user(username)
            else:
                # 如果用户关闭了登录窗口，则退出循环
                break
        else:
            print(f"检测到已保存的登录状态，自动登录用户: {username}")
        
        main_win = MainWindow(username)
        
        screen_geometry = app.primaryScreen().geometry()
        width = int(screen_geometry.width() * 0.8)
        height = int(screen_geometry.height() * 0.8)
        main_win.resize(width, height)
        
        window_geometry = main_win.frameGeometry()
        center_point = app.primaryScreen().availableGeometry().center()
        window_geometry.moveCenter(center_point)
        main_win.move(window_geometry.topLeft())
        
        main_win.show()
        
        app.exec_()

        # 检查主窗口关闭的原因
        if hasattr(main_win, 'logout_triggered') and main_win.logout_triggered:
            # 如果是登出触发的，则继续循环，下一次循环会显示登录框
            print("用户登出，准备重新显示登录界面...")
            continue
        else:
            # 如果是正常关闭（点X），则退出循环
            print("应用关闭。")
            break
            
if __name__ == "__main__":
    main()