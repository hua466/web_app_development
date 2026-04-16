from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User
from app.utils import login_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET'])
def login():
    """顯示登入頁面；若已登入則直接 redirect 至 Dashboard。"""
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('auth/login.html')


@auth_bp.route('/login', methods=['POST'])
def login_post():
    """
    執行登入驗證。
    - 輸入（表單）：email, password
    - 成功：寫入 session，redirect /dashboard
    - 失敗：flash 錯誤訊息，redirect /login
    """
    email    = request.form.get('email', '').strip()
    password = request.form.get('password', '')

    # 基本驗證
    if not email or not password:
        flash('請填寫電子郵件與密碼', 'danger')
        return redirect(url_for('auth.login'))

    user = User.get_by_email(email)
    if user is None or not user.check_password(password):
        flash('帳號或密碼錯誤，請重新輸入', 'danger')
        return redirect(url_for('auth.login'))

    # 登入成功，寫入 session
    session.clear()
    session['user_id']   = user.id
    session['username']  = user.username
    flash(f'歡迎回來，{user.username}！', 'success')
    return redirect(url_for('dashboard.dashboard'))


@auth_bp.route('/register', methods=['GET'])
def register():
    """顯示會員註冊頁面；若已登入則 redirect 至 Dashboard。"""
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('auth/register.html')


@auth_bp.route('/register', methods=['POST'])
def register_post():
    """
    執行會員註冊。
    - 輸入（表單）：username, email, password, confirm_password
    - 成功：flash 成功訊息，redirect /login
    - 失敗：flash 錯誤訊息，redirect /register
    """
    username         = request.form.get('username', '').strip()
    email            = request.form.get('email', '').strip()
    password         = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')

    # —— 輸入驗證 ——
    if not username or not email or not password:
        flash('所有欄位皆為必填', 'danger')
        return redirect(url_for('auth.register'))

    if password != confirm_password:
        flash('兩次輸入的密碼不一致', 'danger')
        return redirect(url_for('auth.register'))

    if len(password) < 6:
        flash('密碼長度至少需要 6 個字元', 'danger')
        return redirect(url_for('auth.register'))

    # —— 重複帳號檢查 ——
    if User.get_by_email(email):
        flash('此電子郵件已被註冊', 'danger')
        return redirect(url_for('auth.register'))

    if User.get_by_username(username):
        flash('此使用者名稱已被使用', 'danger')
        return redirect(url_for('auth.register'))

    # —— 建立帳號 ——
    user = User.create(username=username, email=email, password=password)
    if user is None:
        flash('註冊失敗，請稍後再試', 'danger')
        return redirect(url_for('auth.register'))

    flash('註冊成功！請登入', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
@login_required
def logout():
    """清除 session 並 redirect 至登入頁。"""
    session.clear()
    flash('已成功登出', 'info')
    return redirect(url_for('auth.login'))
