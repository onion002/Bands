from flask import Blueprint, request, jsonify, current_app
from models import db, User, UserType, EmailVerification
from sqlalchemy.exc import IntegrityError
from services.email_service import EmailService
import os
import re
import logging

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建邮件服务实例（在模块级别创建）
email_service = None

def get_email_service():
    """获取邮件服务实例"""
    global email_service
    if email_service is None:
        email_service = EmailService()
        # 这里需要从current_app获取配置来初始化
        if current_app:
            email_service.init_app(current_app)
    return email_service

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

@auth_bp.route('/send-verification-code', methods=['POST'])
def send_verification_code():
    """发送邮箱验证码"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供邮箱地址'}), 400
        
        email = data.get('email', '').strip()
        verification_type = data.get('verification_type', 'register')
        
        # 验证邮箱格式
        if not validate_email(email):
            return jsonify({'error': '邮箱格式不正确'}), 400
        
        # 验证验证码类型
        valid_types = ['register', 'login', 'reset_password']
        if verification_type not in valid_types:
            return jsonify({'error': '验证码类型无效'}), 400
        
        # 如果是注册验证，检查邮箱是否已被注册
        if verification_type == 'register':
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({'error': '该邮箱已被注册'}), 409
        
        # 生成验证码
        code = get_email_service().generate_verification_code()
        
        # 发送验证码邮件
        if get_email_service().send_verification_email(email, code, verification_type):
            return jsonify({
                'message': '验证码发送成功',
                'email': email,
                'verification_type': verification_type
            }), 200
        else:
            return jsonify({'error': '验证码发送失败，请稍后重试'}), 500
            
    except Exception as e:
        logger.error(f"发送验证码失败: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500

@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """验证邮箱验证码"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供验证信息'}), 400
        
        email = data.get('email', '').strip()
        code = data.get('code', '').strip()
        verification_type = data.get('verification_type', 'register')
        
        # 验证必填字段
        if not email or not code:
            return jsonify({'error': '邮箱和验证码不能为空'}), 400
        
        # 验证邮箱格式
        if not validate_email(email):
            return jsonify({'error': '邮箱格式不正确'}), 400
        
        # 验证验证码（不标记为已使用，因为这只是验证，不是最终使用）
        is_valid, message = get_email_service().verify_code(email, code, verification_type, mark_used=False)
        
        if is_valid:
            return jsonify({
                'message': message,
                'email': email,
                'verification_type': verification_type
            }), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        logger.error(f"验证邮箱失败: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500

@auth_bp.route('/register-with-verification', methods=['POST'])
def register_with_verification():
    """使用邮箱验证码注册"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供注册信息'}), 400
        
        # 获取注册信息
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        verification_code = data.get('verification_code', '').strip()
        user_type = data.get('user_type', 'user')
        display_name = data.get('display_name', '').strip()
        developer_key = data.get('developer_key', '').strip()
        
        # 验证必填字段
        if not username or not email or not password or not verification_code:
            return jsonify({'error': '用户名、邮箱、密码和验证码不能为空'}), 400
        
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
        
        # 验证邮箱验证码（标记为已使用，因为这是最终使用）
        is_valid, message = get_email_service().verify_code(email, verification_code, 'register', mark_used=True)
        if not is_valid:
            return jsonify({'error': message}), 400
        
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
        
        # 生成JWT token
        token = new_user.generate_token()
        
        logger.info(f"用户注册成功: {username} ({email})")
        
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
        logger.error(f"用户注册失败: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册（原有接口，保持向后兼容）"""
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
        
        # 生成JWT token
        token = new_user.generate_token()
        
        logger.info(f"新用户注册成功: {username} ({user_type})")
        
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
        
        # 更新隐私设置字段
        if 'bands_public' in data:
            user.bands_public = bool(data['bands_public'])
        
        if 'members_public' in data:
            user.members_public = bool(data['members_public'])
        
        if 'events_public' in data:
            user.events_public = bool(data['events_public'])
        
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
        if not data:
            return jsonify({'error': '请提供token'}), 400
        
        token = data.get('token')
        if not token:
            return jsonify({'error': 'token不能为空'}), 400
        
        # 验证token
        user = User.verify_token(token)
        if user:
            return jsonify({
                'valid': True,
                'user': user.to_dict()
            })
        else:
            return jsonify({
                'valid': False,
                'error': 'token无效或已过期'
            })
    except Exception as e:
        logger.error(f"验证token时发生错误: {str(e)}")
        return jsonify({'error': '验证token失败'}), 500

@auth_bp.route('/upload-avatar', methods=['POST'])
def upload_avatar():
    """上传用户头像"""
    try:
        # 验证用户是否已登录
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '请先登录'}), 401
        
        token = auth_header.split(' ')[1]
        user = User.verify_token(token)
        if not user:
            return jsonify({'error': 'token无效或已过期'}), 401
        
        # 检查是否有文件上传
        if 'avatar' not in request.files:
            return jsonify({'error': '请选择头像文件'}), 400
        
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'error': '请选择头像文件'}), 400
        
        # 验证文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not file.filename.lower().endswith(tuple('.' + ext for ext in allowed_extensions)):
            return jsonify({'error': '只支持PNG、JPG、JPEG、GIF、WEBP格式的图片'}), 400
        
        # 验证文件大小（5MB）
        if len(file.read()) > 5 * 1024 * 1024:
            file.seek(0)  # 重置文件指针
            return jsonify({'error': '文件大小不能超过5MB'}), 400
        
        file.seek(0)  # 重置文件指针
        
        # 创建上传目录
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        import uuid
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"avatar_{user.id}_{uuid.uuid4().hex}{file_extension}"
        file_path = os.path.join(upload_dir, filename)
        
        # 保存文件
        file.save(file_path)
        
        # 更新用户头像URL
        avatar_url = f"/uploads/avatars/{filename}"
        user.avatar_url = avatar_url
        
        db.session.commit()
        
        return jsonify({
            'message': '头像上传成功',
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"上传头像时发生错误: {str(e)}")
        return jsonify({'error': '头像上传失败'}), 500

@auth_bp.route('/public/<username>', methods=['GET'])
def get_public_data(username):
    """获取用户的公开数据"""
    try:
        # 查找用户
        user = User.query.filter_by(username=username, is_active=True).first()
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 检查用户是否有公开数据
        if not (user.bands_public or user.members_public or user.events_public):
            return jsonify({'error': '该用户没有公开任何数据'}), 404
        
        # 获取公开的乐队数据
        bands = []
        if user.bands_public:
            from models import Band
            bands = Band.query.filter_by(owner_id=user.id, is_deleted=False).all()
            bands = [band.to_dict() for band in bands]
        
        # 获取公开的成员数据
        members = []
        if user.members_public:
            from models import Member
            members = Member.query.filter_by(owner_id=user.id, is_deleted=False).all()
            members = [member.to_dict() for member in members]
        
        # 获取公开的活动数据
        events = []
        if user.events_public:
            from models import Event
            events = Event.query.filter_by(owner_id=user.id, is_deleted=False).all()
            events = [event.to_dict() for event in events]
        
        return jsonify({
            'admin': user.to_dict(),
            'bands': bands,
            'members': members,
            'events': events
        })
        
    except Exception as e:
        logger.error(f"获取公开数据时发生错误: {str(e)}")
        return jsonify({'error': '获取公开数据失败'}), 500
