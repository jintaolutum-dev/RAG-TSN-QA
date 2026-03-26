"""
Authentication routes
Provides user login and current user info endpoints
"""
from flask import Blueprint, request, g
from models.user import User
from utils.auth import md5_encrypt, generate_token, login_required
from utils.response import success, error

# Create auth blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint
    Request params: username, password
    Returns: token and user info
    """
    data = request.get_json()
    if not data:
        return error('请提供登录信息')

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return error('用户名和密码不能为空')

    # Find user
    user = User.query.filter_by(username=username).first()
    if not user:
        return error('用户名或密码错误')

    # Verify password (compare MD5 hash)
    if user.password != md5_encrypt(password):
        return error('用户名或密码错误')

    # Check user status
    if user.status != 1:
        return error('账号已被禁用，请联系管理员')

    # Generate token
    token = generate_token(user.id, user.role)

    return success({
        'token': token,
        'user': user.to_dict()
    }, '登录成功')


@auth_bp.route('/info', methods=['GET'])
@login_required
def get_user_info():
    """
    Get current logged-in user info
    A valid token is required
    """
    user = User.query.get(g.user_id)
    if not user:
        return error('用户不存在', 404)

    return success(user.to_dict())

