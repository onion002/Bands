from datetime import date, datetime
import os
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from enum import Enum
import json

db = SQLAlchemy()

class EmailVerification(db.Model):
    """邮箱验证码模型"""
    __tablename__ = 'email_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, index=True)
    code = db.Column(db.String(10), nullable=False)
    verification_type = db.Column(db.String(20), nullable=False, default='register')  # register, login, reset_password
    is_used = db.Column(db.Boolean, nullable=False, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def is_expired(self):
        """检查验证码是否过期"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'verification_type': self.verification_type,
            'is_used': self.is_used,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

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
    # 添加与Event的多对多关系
    events = db.relationship('Event', secondary='event_bands', backref='bands', lazy=True)
    
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

# Event和Band的多对多关联表
event_bands = db.Table('event_bands',
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True),
    db.Column('band_id', db.Integer, db.ForeignKey('bands.id'), primary_key=True)
)

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
            'band_ids': [band.id for band in self.bands] if self.bands else [],
            'band_names': [band.name for band in self.bands] if self.bands else [],
            'poster_image_url': self.poster_image_url
        }

class UserType(Enum):
    """用户类型枚举"""
    ADMIN = 'admin'
    USER = 'user'
    SUPERADMIN = 'superadmin'

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    # 使用枚举的 value 作为存储值（小写字符串），避免大小写不一致
    user_type = db.Column(db.Enum(UserType, values_callable=lambda e: [m.value for m in e]), nullable=False, default=UserType.USER)
    display_name = db.Column(db.String(100))
    avatar_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # 公开设置字段
    bands_public = db.Column(db.Boolean, nullable=False, default=False)
    members_public = db.Column(db.Boolean, nullable=False, default=False)
    events_public = db.Column(db.Boolean, nullable=False, default=False)

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
        return self.user_type in (UserType.ADMIN, UserType.SUPERADMIN)

    def is_superadmin(self):
        return self.user_type == UserType.SUPERADMIN

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
            if not user_id:
                return None
            return User.query.get(user_id)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'bands_public': self.bands_public,
            'members_public': self.members_public,
            'events_public': self.events_public
        }
        return data

    def __repr__(self):
        return f'<User {self.username}>'


# 关联表：帖子与标签多对多关系
post_tags = db.Table(
    'post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, index=True, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)

    # 存储为JSON字符串：图片URL数组和链接数组
    image_urls_json = db.Column(db.Text)
    link_urls_json = db.Column(db.Text)

    like_count = db.Column(db.Integer, nullable=False, default=0)
    comment_count = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    author = db.relationship('User', backref=db.backref('posts', lazy=True))

    # 标签多对多
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))

    def get_image_urls(self):
        if not self.image_urls_json:
            return []
        try:
            return json.loads(self.image_urls_json)
        except Exception:
            return []

    def set_image_urls(self, urls):
        self.image_urls_json = json.dumps(urls or [])

    def get_link_urls(self):
        if not self.link_urls_json:
            return []
        try:
            return json.loads(self.link_urls_json)
        except Exception:
            return []

    def set_link_urls(self, urls):
        self.link_urls_json = json.dumps(urls or [])

    def to_dict(self, include_author=True):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'image_urls': self.get_image_urls(),
            'link_urls': self.get_link_urls(),
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'display_name': self.author.display_name,
                'avatar_url': self.author.avatar_url
            } if include_author and self.author else None,
            'tags': [tag.to_dict() for tag in self.tags] if self.tags else []
        }


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    like_count = db.Column(db.Integer, nullable=False, default=0)
    is_pinned = db.Column(db.Boolean, nullable=False, default=False)  # 是否置顶
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    post = db.relationship('Post', backref=db.backref('comments', lazy=True, cascade='all, delete-orphan'))

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    author = db.relationship('User', backref=db.backref('comments', lazy=True))

    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    parent = db.relationship('Comment', remote_side=[id], backref=db.backref('replies', lazy=True, cascade='all, delete-orphan'))

    def to_dict(self, include_author=True):
        return {
            'id': self.id,
            'content': self.content,
            'like_count': self.like_count,
            'is_pinned': self.is_pinned,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'post_id': self.post_id,
            'author': {
                'id': self.author.id,
                'username': self.author.username,
                'display_name': self.author.display_name,
                'avatar_url': self.author.avatar_url
            } if include_author and self.author else None,
            'parent_id': self.parent_id
        }


class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True, index=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('likes', lazy=True, cascade='all, delete-orphan'))
    post = db.relationship('Post', backref=db.backref('likes', lazy=True, cascade='all, delete-orphan'))
    comment = db.relationship('Comment', backref=db.backref('likes', lazy=True, cascade='all, delete-orphan'))


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    target_type = db.Column(db.String(20), nullable=False)  # 'post' or 'comment'
    target_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(500))
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, resolved, dismissed
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    reporter = db.relationship('User', backref=db.backref('reports', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'reporter_id': self.reporter_id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'reason': self.reason,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }