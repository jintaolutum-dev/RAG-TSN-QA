"""
JWT authentication utilities
Provides token generation, verification, and auth decorators
"""
import jwt
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import request, g, current_app


def md5_encrypt(text):
    """
    MD5 hashing
    :param text: Raw string
    :return: MD5 hashing后的字符串
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def generate_token(user_id, role):
    """
    Generate JWT token
    :param user_id: User ID
    :param role: User role
    :return: Token string
    """
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(seconds=current_app.config['JWT_EXPIRATION'])
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token


def verify_token(token):
    """
    Verify JWT token
    :param token: Token string
    :return: Decoded payload or None
    """
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def login_required(f):
    """
    Login-required decorator
    Requires a valid Authorization token in request headers
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '')
        if token.startswith('Bearer '):
            token = token[7:]

        if not token:
            from utils.response import error
            return error('请先登录', 401)

        payload = verify_token(token)
        if not payload:
            from utils.response import error
            return error('登录已过期，请重新登录', 401)

        # Store user info in g for downstream handlers
        g.user_id = payload['user_id']
        g.role = payload['role']
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    """
    Admin-required decorator
    Requires user to be logged in and role to be admin
    """
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if g.role != 'admin':
            from utils.response import error
            return error('权限不足，需要管理员权限', 403)
        return f(*args, **kwargs)

    return decorated

