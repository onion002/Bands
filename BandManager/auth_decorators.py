from functools import wraps
from flask import request, jsonify, g
from models import User
import logging

logger = logging.getLogger(__name__)

def require_auth(f):
    """需要认证的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 从请求头获取token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': '未提供认证token'}), 401
            
            token = auth_header.split(' ')[1]
            user = User.verify_token(token)
            
            if not user:
                return jsonify({'error': 'token无效或已过期'}), 401
            
            if not user.is_active:
                return jsonify({'error': '账户已被禁用'}), 403
            
            # 将用户信息存储到g对象中，供视图函数使用
            g.current_user = user
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"认证失败: {str(e)}")
            return jsonify({'error': '认证失败'}), 401
    
    return decorated_function

def require_admin(f):
    """需要管理员权限的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 先进行基本认证
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': '未提供认证token'}), 401
            
            token = auth_header.split(' ')[1]
            user = User.verify_token(token)
            
            if not user:
                return jsonify({'error': 'token无效或已过期'}), 401
            
            if not user.is_active:
                return jsonify({'error': '账户已被禁用'}), 403
            
            # 检查管理员权限
            if not user.is_admin():
                return jsonify({'error': '需要管理员权限'}), 403
            
            # 将用户信息存储到g对象中
            g.current_user = user
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"管理员权限验证失败: {str(e)}")
            return jsonify({'error': '权限验证失败'}), 403
    
    return decorated_function

def require_superadmin(f):
    """需要超级管理员权限的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': '未提供认证token'}), 401
            token = auth_header.split(' ')[1]
            user = User.verify_token(token)
            if not user:
                return jsonify({'error': 'token无效或已过期'}), 401
            if not user.is_active:
                return jsonify({'error': '账户已被禁用'}), 403
            if not user.is_superadmin():
                return jsonify({'error': '需要超级管理员权限'}), 403
            g.current_user = user
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"超级管理员权限验证失败: {str(e)}")
            return jsonify({'error': '权限验证失败'}), 403
    return decorated_function

def optional_auth(f):
    """可选认证的装饰器（用于公开API，但如果有token则验证）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 尝试获取token
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                user = User.verify_token(token)
                
                if user and user.is_active:
                    g.current_user = user
                else:
                    g.current_user = None
            else:
                g.current_user = None
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"可选认证失败: {str(e)}")
            g.current_user = None
            return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """获取当前用户"""
    return getattr(g, 'current_user', None)

def is_authenticated():
    """检查是否已认证"""
    return get_current_user() is not None

def is_admin():
    """检查是否为管理员"""
    user = get_current_user()
    return user is not None and user.is_admin()

def get_user_filter():
    """获取用户数据过滤条件"""
    user = get_current_user()
    if user and user.is_admin():
        return {'owner_id': user.id}
    return None

def apply_user_filter(query, model_class):
    """应用用户数据过滤"""
    user = get_current_user()
    if user and user.is_admin():
        # 管理员只能看到自己的数据
        return query.filter(getattr(model_class, 'owner_id') == user.id)
    return query

def set_owner_for_creation(data):
    """为创建操作设置owner_id"""
    user = get_current_user()
    if user and user.is_admin():
        data['owner_id'] = user.id
    return data
