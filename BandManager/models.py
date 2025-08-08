from datetime import date, datetime
import os
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from enum import Enum

db = SQLAlchemy()

class Band(db.Model):
    __tablename__ = 'bands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    year = db.Column(db.Integer)
    genre = db.Column(db.String(50))
    bio = db.Column(db.Text)
    member_count = db.Column(db.Integer, nullable=False, default=0)
    
    # 添加图片相关字段
    banner_image_url = db.Column(db.String(255), nullable=True)  # 首页大图 URL
    profile_image_url = db.Column(db.String(255), nullable=True)  # 详情页头像 URL
    
    # 颜色相关字段（用于未上传图片时）
    primary_color = db.Column(db.String(7), default="#1d3557")  # 格式: #RRGGBB
    secondary_color = db.Column(db.String(7), default="#457b9d")

    # 时间戳字段
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 软删除字段
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    # 多租户支持 - 所属管理员
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)

    # 添加与Member的一对多关系
    members = db.relationship('Member', backref='band', lazy=True, cascade='all, delete-orphan')
    # 添加与Event的一对多关系
    events = db.relationship('Event', backref='band', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'year': self.year,
            'genre': self.genre,
            'bio': self.bio,
            'member_count': len(list(self.members)) if self.members else 0,
            # 修正：使用 None 而不是字符串 "null"
            'banner_image_url': self.banner_image_url if self.banner_image_url else None,
            'profile_image_url': self.profile_image_url if self.profile_image_url else None,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color
        }
    
    @hybrid_property
    def full_banner_image_url(self):
        """获取完整的 banner 图片 URL"""
        if self.banner_image_url:
            # 拼接完整的 URL
            return f"{current_app.config['API_BASE_URL']}/uploads{self.banner_image_url}"
        return None
    
    @hybrid_property
    def full_profile_image_url(self):
        """获取完整的 profile 图片 URL"""
        if self.profile_image_url:
            # 拼接完整的 URL
            return f"{current_app.config['API_BASE_URL']}/uploads{self.profile_image_url}"
        return None

class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50))
    join_date = db.Column(db.Date, nullable=False)
    band_id = db.Column(db.Integer, db.ForeignKey('bands.id'), nullable=False)
    
    # 添加成员头像字段
    avatar_url = db.Column(db.String(255), nullable=True)

    # 时间戳字段
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 软删除字段
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    # 多租户支持 - 所属管理员
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'join_date': str(self.join_date) if self.join_date else None,
            'band_id': self.band_id,
            'band_name': self.band.name if self.band else None,  # type: ignore
            'avatar_url': self.avatar_url
        }

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(200))
    address = db.Column(db.String(500))
    ticket_price = db.Column(db.Numeric(10, 2))  # 票价，支持小数
    capacity = db.Column(db.Integer)  # 场地容量
    status = db.Column(db.String(20), default='upcoming')  # upcoming, ongoing, completed, cancelled
    band_id = db.Column(db.Integer, db.ForeignKey('bands.id'), nullable=False)

    # 图片相关字段
    poster_image_url = db.Column(db.String(255), nullable=True)  # 演出海报

    # 时间戳字段
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 软删除字段
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    # 多租户支持 - 所属管理员
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'venue': self.venue,
            'address': self.address,
            'ticket_price': float(self.ticket_price) if self.ticket_price else None,
            'capacity': self.capacity,
            'status': self.status,
            'band_id': self.band_id,
            'band_name': self.band.name if self.band else None,  # type: ignore
            'poster_image_url': self.poster_image_url
        }

class UserType(Enum):
    """用户类型枚举"""
    ADMIN = 'admin'
    USER = 'user'

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.Enum(UserType), nullable=False, default=UserType.USER)
    display_name = db.Column(db.String(100))
    avatar_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # 时间戳字段
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系 - 管理员用户拥有的数据
    owned_bands = db.relationship('Band', backref='owner', lazy=True, foreign_keys='Band.owner_id')
    owned_members = db.relationship('Member', backref='owner', lazy=True, foreign_keys='Member.owner_id')
    owned_events = db.relationship('Event', backref='owner', lazy=True, foreign_keys='Event.owner_id')

    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """检查是否为管理员"""
        return self.user_type == UserType.ADMIN

    def generate_token(self, expires_in=86400):
        """生成JWT token"""
        payload = {
            'user_id': self.id,
            'username': self.username,
            'user_type': self.user_type.value,
            'exp': datetime.utcnow().timestamp() + expires_in
        }
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_token(token):
        """验证JWT token"""
        try:
            from flask import current_app
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload.get('user_id')
            if user_id:
                return User.query.get(user_id)
            return None
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None
            if user_id:
                return User.query.get(user_id)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None
        return None

    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email if include_sensitive else None,
            'user_type': self.user_type.value,
            'display_name': self.display_name,
            'avatar_url': self.avatar_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        return data

    def __repr__(self):
        return f'<User {self.username}>'