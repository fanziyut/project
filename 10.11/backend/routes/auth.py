"""登录认证接口：登录、退出、当前用户。"""
from flask import Blueprint, jsonify, request, session

from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__)

DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin123'


def require_login():
    """供各业务蓝图在 before_request 中调用，未登录时返回 401。"""
    if request.method == 'OPTIONS':  # 放行跨域预检请求
        return None
    if 'user_id' not in session:
        return jsonify({'message': '请先登录'}), 401
    return None


def ensure_default_user():
    """首次启动时创建默认管理员，方便直接体验登录功能。"""
    if User.query.count() > 0:
        return
    user = User(username=DEFAULT_USERNAME, display_name='管理员')
    user.set_password(DEFAULT_PASSWORD)
    db.session.add(user)
    db.session.commit()


def _current_user():
    user_id = session.get('user_id')
    if user_id is None:
        return None
    return db.session.get(User, user_id)


@auth_bp.post('/login')
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'message': '请输入用户名和密码'}), 400

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify({'message': '用户名或密码错误'}), 401

    session.clear()
    session['user_id'] = user.id
    session.permanent = True
    return jsonify({'user': user.to_dict()})


@auth_bp.post('/logout')
def logout():
    session.clear()
    return jsonify({'message': '已退出登录'})


@auth_bp.get('/me')
def me():
    user = _current_user()
    if user is None:
        return jsonify({'message': '未登录'}), 401
    return jsonify({'user': user.to_dict()})
