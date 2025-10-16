# user_manager.py

import json
import hashlib
import os
from PyQt5.QtCore import QSettings

USERS_FILE = 'users.json'
LOGGED_IN_USER_KEY = "last_logged_in_user"

def _hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        default_users = {"admin": _hash_password("123456")}
        save_users(default_users)
        return default_users
    try:
        with open(USERS_FILE, 'r') as f: return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError): return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f: json.dump(users, f, indent=4)

def verify_user(username, password):
    users = load_users()
    if username in users and users[username] == _hash_password(password):
        return True
    return False

def add_user(username, password):
    users = load_users()
    if username in users: return False, "用户名已存在"
    if not username or not password: return False, "用户名和密码不能为空"
    users[username] = _hash_password(password)
    save_users(users)
    return True, "注册成功"

def save_logged_in_user(username):
    """当用户成功登录时，保存用户名"""
    settings = QSettings()
    settings.setValue(LOGGED_IN_USER_KEY, username)
    print(f"已保存登录状态: {username}")

def get_logged_in_user():
    """获取已保存的登录用户"""
    settings = QSettings()
    username = settings.value(LOGGED_IN_USER_KEY, None)
    if username and username in load_users():
        return username
    # 如果保存的用户不存在或无效，清除它
    logout_user()
    return None

def logout_user():
    """登出用户，清除已保存的状态"""
    settings = QSettings()
    settings.remove(LOGGED_IN_USER_KEY)
    print("登录状态已清除。")