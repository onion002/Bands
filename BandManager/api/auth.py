from flask import Blueprint, request, jsonify, current_app
from models import db, User, UserType
from sqlalchemy.exc import IntegrityError
import os
import re
import logging

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """验证密码强度"""
    if len(password) < 8:
        return False, "密码长度至少8位"
    if not re.search(r'[A-Za-z]', password):
        return False, "密码必须包含字母"
    if not re.search(r'\d', password):
        return False, "密码必须包含数字"
    return True, ""

def validate_developer_key(key):
    """验证开发者密钥"""
    valid_keys = current_app.config.get('DEVELOPER_SECRET_KEYS', '').split(',')
    valid_keys = [k.strip() for k in valid_keys if k.strip()]
    return key in valid_keys

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供注册信息'}), 400
        
        # 获取注册信息
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        user_type = data.get('user_type', 'user')
        display_name = data.get('display_name', '').strip()
        developer_key = data.get('developer_key', '').strip()
        
        # 验证必填字段
        if not username or not email or not password:
            return jsonify({'error': '用户名、邮箱和密码不能为空'}), 400
        
        # 验证用户名格式
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
            return jsonify({'error': '用户名只能包含字母、数字和下划线，长度3-20位'}), 400
        
        # 验证邮箱格式
        if not validate_email(email):
            return jsonify({'error': '邮箱格式不正确'}), 400
        
        # 验证密码强度
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # 验证用户类型
        if user_type not in ['user', 'admin']:
            return jsonify({'error': '用户类型无效'}), 400
        
        # 如果是管理员注册，验证开发者密钥
        if user_type == 'admin':
            if not developer_key:
                return jsonify({'error': '管理员注册需要提供开发者密钥'}), 400
            if not validate_developer_key(developer_key):
                return jsonify({'error': '开发者密钥无效'}), 403
        
        # 检查用户名和邮箱是否已存在
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                return jsonify({'error': '用户名已存在'}), 409
            else:
                return jsonify({'error': '邮箱已被注册'}), 409
        
        # 创建新用户
        new_user = User(
            username=username,
            email=email,
            user_type=UserType.ADMIN if user_type == 'admin' else UserType.USER,
            display_name=display_name or username
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f"新用户注册成功: {username} ({user_type})")
        
        # 生成token
        token = new_user.generate_token()
        
        return jsonify({
            'message': '注册成功',
            'user': new_user.to_dict(),
            'token': token
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': '用户名或邮箱已存在'}), 409
    except Exception as e:
        db.session.rollback()
        logger.error(f"注册失败: {str(e)}")
        return jsonify({'error': '注册失败，请稍后重试'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供登录信息'}), 400
        
        # 获取登录信息
        login_field = data.get('login', '').strip()  # 可以是用户名或邮箱
        password = data.get('password', '')
        
        if not login_field or not password:
            return jsonify({'error': '用户名/邮箱和密码不能为空'}), 400
        
        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter(
            (User.username == login_field) | (User.email == login_field)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': '用户名/邮箱或密码错误'}), 401
        
        if not user.is_active:
            return jsonify({'error': '账户已被禁用'}), 403
        
        # 生成token
        token = user.generate_token()
        
        logger.info(f"用户登录成功: {user.username}")
        
        return jsonify({
            'message': '登录成功',
            'user': user.to_dict(),
            'token': token
        }), 200
        
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        return jsonify({'error': '登录失败，请稍后重试'}), 500

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """获取用户信息"""
    try:
        # 从请求头获取token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '未提供认证token'}), 401
        
        token = auth_header.split(' ')[1]
        user = User.verify_token(token)
        
        if not user:
            return jsonify({'error': 'token无效或已过期'}), 401
        
        return jsonify({
            'user': user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        return jsonify({'error': '获取用户信息失败'}), 500

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    """更新用户信息"""
    try:
        # 验证token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '未提供认证token'}), 401
        
        token = auth_header.split(' ')[1]
        user = User.verify_token(token)
        
        if not user:
            return jsonify({'error': 'token无效或已过期'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供更新信息'}), 400
        
        # 更新允许的字段
        if 'display_name' in data:
            user.display_name = data['display_name'].strip()
        
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url'].strip()
        
        # 更新邮箱（需要验证格式和唯一性）
        if 'email' in data:
            new_email = data['email'].strip()
            if not validate_email(new_email):
                return jsonify({'error': '邮箱格式不正确'}), 400
            
            # 检查邮箱是否已被其他用户使用
            existing_user = User.query.filter(
                User.email == new_email,
                User.id != user.id
            ).first()
            
            if existing_user:
                return jsonify({'error': '邮箱已被其他用户使用'}), 409
            
            user.email = new_email
        
        db.session.commit()
        
        logger.info(f"用户信息更新成功: {user.username}")
        
        return jsonify({
            'message': '用户信息更新成功',
            'user': user.to_dict(include_sensitive=True)
        }), 200
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': '邮箱已被使用'}), 409
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新用户信息失败: {str(e)}")
        return jsonify({'error': '更新失败，请稍后重试'}), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """修改密码"""
    try:
        # 验证token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '未提供认证token'}), 401
        
        token = auth_header.split(' ')[1]
        user = User.verify_token(token)
        
        if not user:
            return jsonify({'error': 'token无效或已过期'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供密码信息'}), 400
        
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        if not old_password or not new_password:
            return jsonify({'error': '旧密码和新密码不能为空'}), 400
        
        # 验证旧密码
        if not user.check_password(old_password):
            return jsonify({'error': '旧密码错误'}), 401
        
        # 验证新密码强度
        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # 更新密码
        user.set_password(new_password)
        db.session.commit()
        
        logger.info(f"用户密码修改成功: {user.username}")
        
        return jsonify({'message': '密码修改成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"修改密码失败: {str(e)}")
        return jsonify({'error': '修改密码失败，请稍后重试'}), 500

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """验证token有效性"""
    try:
        data = request.get_json()
        token = data.get('token') if data else None
        
        if not token:
            # 尝试从请求头获取
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'valid': False, 'error': '未提供token'}), 400
        
        user = User.verify_token(token)
        
        if user and user.is_active:
            return jsonify({
                'valid': True,
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'valid': False, 'error': 'token无效或已过期'}), 401
            
    except Exception as e:
        logger.error(f"验证token失败: {str(e)}")
        return jsonify({'valid': False, 'error': '验证失败'}), 500
