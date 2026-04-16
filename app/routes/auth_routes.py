from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User
from app.utils import login_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET'])
def login():
    """
    顯示登入頁面。
    - 若使用者已登入，直接 redirect 至 /dashboard。
    - 輸出：渲染 auth/login.html
    """
    pass


@auth_bp.route('/login', methods=['POST'])
def login_post():
    """
    執行登入驗證。
    - 輸入（表單）：email, password
    - 邏輯：User.get_by_email() → check_password() → 寫入 session['user_id']
    - 成功：redirect /dashboard
    - 失敗：flash 錯誤訊息，redirect /login
    """
    pass


@auth_bp.route('/register', methods=['GET'])
def register():
    """
    顯示會員註冊頁面。
    - 若已登入，redirect 至 /dashboard。
    - 輸出：渲染 auth/register.html
    """
    pass


@auth_bp.route('/register', methods=['POST'])
def register_post():
    """
    執行會員註冊。
    - 輸入（表單）：username, email, password, confirm_password
    - 邏輯：驗證兩次密碼 → 確認 email/username 未重複 → User.create()
    - 成功：redirect /login，flash 'Registration successful!'
    - 失敗：flash 錯誤訊息，redirect /register
    """
    pass


@auth_bp.route('/logout')
@login_required
def logout():
    """
    執行登出。
    - 邏輯：清除 session
    - 輸出：redirect /login
    """
    pass
