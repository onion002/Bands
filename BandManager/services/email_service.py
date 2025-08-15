import random
import string
from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Mail, Message
from models import db, EmailVerification
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """邮件服务类"""
    
    def __init__(self, app=None):
        self.mail = Mail()
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化邮件服务"""
        self.mail.init_app(app)
    
    def generate_verification_code(self, length=6):
        """生成随机验证码"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_verification_email(self, email, code, verification_type='register'):
        """发送验证码邮件"""
        try:
            # 邮件主题
            subject_map = {
                'register': '乐队管理系统 - 邮箱验证码',
                'login': '乐队管理系统 - 登录验证码',
                'reset_password': '乐队管理系统 - 重置密码验证码'
            }
            subject = subject_map.get(verification_type, '乐队管理系统 - 验证码')
            
            # 邮件内容
            content_map = {
                'register': f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">欢迎注册乐队管理系统</h2>
                    <p>您的邮箱验证码是：</p>
                    <div style="background-color: #f5f5f5; padding: 20px; text-align: center; margin: 20px 0;">
                        <h1 style="color: #007bff; font-size: 32px; margin: 0;">{code}</h1>
                    </div>
                    <p>验证码将在5分钟后过期，请及时使用。</p>
                    <p>如果这不是您的操作，请忽略此邮件。</p>
                    <hr style="margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">此邮件由系统自动发送，请勿回复。</p>
                </div>
                ''',
                'login': f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">乐队管理系统 - 登录验证</h2>
                    <p>您的登录验证码是：</p>
                    <div style="background-color: #f5f5f5; padding: 20px; text-align: center; margin: 20px 0;">
                        <h1 style="color: #007bff; font-size: 32px; margin: 0;">{code}</h1>
                    </div>
                    <p>验证码将在5分钟后过期，请及时使用。</p>
                    <p>如果这不是您的操作，请忽略此邮件。</p>
                    <hr style="margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">此邮件由系统自动发送，请勿回复。</p>
                </div>
                ''',
                'reset_password': f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">乐队管理系统 - 重置密码</h2>
                    <p>您的重置密码验证码是：</p>
                    <div style="background-color: #f5f5f5; padding: 20px; text-align: center; margin: 20px 0;">
                        <h1 style="color: #007bff; font-size: 32px; margin: 0;">{code}</h1>
                    </div>
                    <p>验证码将在5分钟后过期，请及时使用。</p>
                    <p>如果这不是您的操作，请忽略此邮件。</p>
                    <hr style="margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">此邮件由系统自动发送，请勿回复。</p>
                </div>
                '''
            }
            
            html_content = content_map.get(verification_type, content_map['register'])
            
            # 创建邮件消息
            msg = Message(
                subject=subject,
                recipients=[email],
                html=html_content
            )
            
            # 发送邮件
            self.mail.send(msg)
            
            # 保存验证码到数据库
            self.save_verification_code(email, code, verification_type)
            
            logger.info(f"验证码邮件发送成功: {email}")
            return True
            
        except Exception as e:
            logger.error(f"发送验证码邮件失败: {email}, 错误: {str(e)}")
            return False
    
    def save_verification_code(self, email, code, verification_type='register'):
        """保存验证码到数据库"""
        try:
            # 设置过期时间（5分钟）
            expires_at = datetime.utcnow() + timedelta(minutes=5)
            
            # 创建新的验证码记录
            verification = EmailVerification(
                email=email,
                code=code,
                verification_type=verification_type,
                expires_at=expires_at
            )
            
            db.session.add(verification)
            db.session.commit()
            
            logger.info(f"验证码保存成功: {email}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"保存验证码失败: {email}, 错误: {str(e)}")
            return False
    
    def verify_code(self, email, code, verification_type='register', mark_used=True):
        """验证验证码
        
        Args:
            email: 邮箱地址
            code: 验证码
            verification_type: 验证码类型
            mark_used: 是否标记为已使用，默认为True
        """
        try:
            # 查找最新的未使用且未过期的验证码
            verification = EmailVerification.query.filter_by(
                email=email,
                verification_type=verification_type,
                is_used=False
            ).order_by(EmailVerification.created_at.desc()).first()
            
            if not verification:
                return False, "验证码不存在"
            
            if verification.is_expired():
                return False, "验证码已过期"
            
            if verification.code != code:
                return False, "验证码错误"
            
            # 根据参数决定是否标记为已使用
            if mark_used:
                verification.is_used = True
                db.session.commit()
                logger.info(f"验证码已标记为已使用: {email}")
            
            logger.info(f"验证码验证成功: {email}")
            return True, "验证成功"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"验证码验证失败: {email}, 错误: {str(e)}")
            return False, "验证失败"
    
    def clean_expired_codes(self):
        """清理过期的验证码"""
        try:
            expired_codes = EmailVerification.query.filter(
                EmailVerification.expires_at < datetime.utcnow()
            ).all()
            
            for code in expired_codes:
                db.session.delete(code)
            
            db.session.commit()
            logger.info(f"清理过期验证码: {len(expired_codes)} 个")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"清理过期验证码失败: {str(e)}")
            return False
