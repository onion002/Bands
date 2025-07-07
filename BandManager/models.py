from datetime import date
import os
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property

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
    
    # 添加与Member的一对多关系
    members = db.relationship('Member', backref='band', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'year': self.year,
            'genre': self.genre,
            'bio': self.bio,
            'member_count': len(self.members) if self.members else 0,
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'join_date': str(self.join_date)if self.join_date else None,
            'band_id': self.band_id,
            'band_name': self.band.name if self.band else None,
            'avatar_url': self.avatar_url
        }