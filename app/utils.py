"""
app/utils.py

共用工具函式，包含路由保護裝飾器等。
"""

from functools import wraps
from flask import session, redirect, url_for


def login_required(f):
    """
    路由保護裝飾器。
    未登入的請求一律 redirect 至 /login。

    使用方式：
        @blueprint.route('/some-path')
        @login_required
        def some_view():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
