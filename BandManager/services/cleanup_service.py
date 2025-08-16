import os
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from flask import current_app

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models import db, EmailVerification, User, Post, Comment, Like, Report

logger = logging.getLogger(__name__)


class CleanupService:
    """数据清理服务"""
    
    @staticmethod
    def cleanup_expired_email_verifications():
        """清理过期的邮箱验证码"""
        try:
            # 删除已过期且已使用的验证码
            expired_verifications = EmailVerification.query.filter(
                EmailVerification.expires_at < datetime.utcnow()
            ).all()
            
            count = 0
            for verification in expired_verifications:
                db.session.delete(verification)
                count += 1
            
            db.session.commit()
            logger.info(f"清理过期邮箱验证码完成，共删除 {count} 条记录")
            return count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"清理过期邮箱验证码失败: {str(e)}")
            return 0
    
    @staticmethod
    def cleanup_old_reports():
        """清理已处理的旧举报记录（保留30天）"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            old_reports = Report.query.filter(
                Report.status.in_(['resolved', 'dismissed']),
                Report.created_at < cutoff_date
            ).all()
            
            count = 0
            for report in old_reports:
                db.session.delete(report)
                count += 1
            
            db.session.commit()
            logger.info(f"清理旧举报记录完成，共删除 {count} 条记录")
            return count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"清理旧举报记录失败: {str(e)}")
            return 0
    
    @staticmethod
    def cleanup_orphaned_likes():
        """清理孤立的点赞记录（帖子或评论已被删除的点赞）"""
        try:
            # 清理孤立的帖子点赞
            orphaned_post_likes = db.session.query(Like).outerjoin(
                Post, Like.post_id == Post.id
            ).filter(
                Like.post_id.isnot(None),
                Post.id.is_(None)
            ).all()
            
            # 清理孤立的评论点赞
            orphaned_comment_likes = db.session.query(Like).outerjoin(
                Comment, Like.comment_id == Comment.id
            ).filter(
                Like.comment_id.isnot(None),
                Comment.id.is_(None)
            ).all()
            
            count = 0
            for like in orphaned_post_likes + orphaned_comment_likes:
                db.session.delete(like)
                count += 1
            
            db.session.commit()
            logger.info(f"清理孤立点赞记录完成，共删除 {count} 条记录")
            return count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"清理孤立点赞记录失败: {str(e)}")
            return 0

    @staticmethod
    def cleanup_orphaned_user_data():
        """清理已删除用户的所有关联数据"""
        try:
            from models import Band, Member, Event, Post, Comment, Like, Report
            
            cleaned_data = {
                'bands': 0,
                'members': 0,
                'events': 0,
                'posts': 0,
                'comments': 0,
                'likes': 0,
                'reports': 0
            }
            
            # 1. 清理孤立的乐队（owner_id 指向不存在的用户）
            orphaned_bands = db.session.query(Band).outerjoin(
                User, Band.owner_id == User.id
            ).filter(
                Band.owner_id.isnot(None),
                User.id.is_(None)
            ).all()
            
            for band in orphaned_bands:
                try:
                    # 先删除乐队相关的图片文件
                    if band.banner_image_url:
                        try:
                            filename = band.banner_image_url.split('/')[-1]
                            file_path = os.path.join(
                                current_app.config['UPLOAD_FOLDER'],
                                'bands',
                                filename
                            )
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                logger.info(f"删除孤立乐队图片: {file_path}")
                        except Exception as e:
                            logger.warning(f"删除孤立乐队图片失败: {str(e)}")
                    
                    db.session.delete(band)
                    cleaned_data['bands'] += 1
                    logger.info(f"删除孤立乐队: {band.name}")
                except Exception as e:
                    logger.warning(f"删除孤立乐队失败 {band.name}: {str(e)}")
            
            # 2. 清理孤立的成员（owner_id 指向不存在的用户）
            orphaned_members = db.session.query(Member).outerjoin(
                User, Member.owner_id == User.id
            ).filter(
                Member.owner_id.isnot(None),
                User.id.is_(None)
            ).all()
            
            for member in orphaned_members:
                try:
                    # 先删除成员头像文件
                    if member.avatar_url:
                        try:
                            filename = member.avatar_url.split('/')[-1]
                            file_path = os.path.join(
                                current_app.config['UPLOAD_FOLDER'],
                                'members',
                                filename
                            )
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                logger.info(f"删除孤立成员头像: {file_path}")
                        except Exception as e:
                            logger.warning(f"删除孤立成员头像失败: {str(e)}")
                    
                    db.session.delete(member)
                    cleaned_data['members'] += 1
                    logger.info(f"删除孤立成员: {member.name}")
                except Exception as e:
                    logger.warning(f"删除孤立成员失败 {member.name}: {str(e)}")
            
            # 3. 清理孤立的活动（owner_id 指向不存在的用户）
            orphaned_events = db.session.query(Event).outerjoin(
                User, Event.owner_id == User.id
            ).filter(
                Event.owner_id.isnot(None),
                User.id.is_(None)
            ).all()
            
            for event in orphaned_events:
                try:
                    # 先删除活动海报文件
                    if event.poster_image_url:
                        try:
                            filename = event.poster_image_url.split('/')[-1]
                            file_path = os.path.join(
                                current_app.config['UPLOAD_FOLDER'],
                                'events',
                                filename
                            )
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                logger.info(f"删除孤立活动海报: {file_path}")
                        except Exception as e:
                            logger.warning(f"删除孤立活动海报失败: {str(e)}")
                    
                    db.session.delete(event)
                    cleaned_data['events'] += 1
                    logger.info(f"删除孤立活动: {event.title}")
                except Exception as e:
                    logger.warning(f"删除孤立活动失败 {event.title}: {str(e)}")
            
            # 4. 清理孤立的帖子（author_id 指向不存在的用户）
            orphaned_posts = db.session.query(Post).outerjoin(
                User, Post.author_id == User.id
            ).filter(
                Post.author_id.isnot(None),
                User.id.is_(None)
            ).all()
            
            for post in orphaned_posts:
                try:
                    # 先删除帖子图片文件
                    image_urls = post.get_image_urls()
                    for image_url in image_urls:
                        if image_url:
                            try:
                                filename = image_url.split('/')[-1]
                                # 检查多个可能的目录
                                possible_dirs = [
                                    os.path.join(current_app.config['UPLOAD_FOLDER'], 'posts'),
                                    os.path.join(current_app.config['UPLOAD_FOLDER'], 'community'),
                                    os.path.join(current_app.config['UPLOAD_FOLDER'], 'community', 'posts')
                                ]
                                for posts_upload_dir in possible_dirs:
                                    if os.path.exists(posts_upload_dir):
                                        file_path = os.path.join(posts_upload_dir, filename)
                                        if os.path.exists(file_path):
                                            os.remove(file_path)
                                            logger.info(f"删除孤立帖子图片: {file_path}")
                                        break
                            except Exception as e:
                                logger.warning(f"删除孤立帖子图片失败: {str(e)}")
                    
                    db.session.delete(post)
                    cleaned_data['posts'] += 1
                    logger.info(f"删除孤立帖子: {post.title or f'帖子#{post.id}'}")
                except Exception as e:
                    logger.warning(f"删除孤立帖子失败 {post.id}: {str(e)}")
            
            # 5. 清理孤立的评论（author_id 指向不存在的用户）
            orphaned_comments = db.session.query(Comment).outerjoin(
                User, Comment.author_id == User.id
            ).filter(
                Comment.author_id.isnot(None),
                User.id.is_(None)
            ).all()
            
            for comment in orphaned_comments:
                try:
                    db.session.delete(comment)
                    cleaned_data['comments'] += 1
                    logger.info(f"删除孤立评论: {comment.content[:50]}...")
                except Exception as e:
                    logger.warning(f"删除孤立评论失败 {comment.id}: {str(e)}")
            
            # 6. 清理孤立的点赞（user_id 指向不存在的用户）
            orphaned_user_likes = db.session.query(Like).outerjoin(
                User, Like.user_id == User.id
            ).filter(
                Like.user_id.isnot(None),
                User.id.is_(None)
            ).all()
            
            for like in orphaned_user_likes:
                try:
                    db.session.delete(like)
                    cleaned_data['likes'] += 1
                except Exception as e:
                    logger.warning(f"删除孤立用户点赞失败 {like.id}: {str(e)}")
            
            # 7. 清理孤立的举报记录（reporter_id 指向不存在的用户）
            orphaned_reports = db.session.query(Report).outerjoin(
                User, Report.reporter_id == User.id
            ).filter(
                Report.reporter_id.isnot(None),
                User.id.is_(None)
            ).all()
            
            for report in orphaned_reports:
                try:
                    db.session.delete(report)
                    cleaned_data['reports'] += 1
                except Exception as e:
                    logger.warning(f"删除孤立举报记录失败 {report.id}: {str(e)}")
            
            # 提交所有删除操作
            db.session.commit()
            
            total_cleaned = sum(cleaned_data.values())
            logger.info(f"清理已删除用户关联数据完成，共删除 {total_cleaned} 项数据: {cleaned_data}")
            return cleaned_data
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"清理已删除用户关联数据失败: {str(e)}")
            return {'bands': 0, 'members': 0, 'events': 0, 'posts': 0, 'comments': 0, 'likes': 0, 'reports': 0}
    
    @staticmethod
    def cleanup_orphaned_files():
        """清理孤立的文件（没有被数据库记录引用的文件）"""
        try:
            cleaned_files = []
            
            # 清理乐队图片
            cleaned_files.extend(CleanupService._cleanup_band_images())
            
            # 清理成员头像
            cleaned_files.extend(CleanupService._cleanup_member_avatars())
            
            # 清理活动海报
            cleaned_files.extend(CleanupService._cleanup_event_posters())
            
            # 清理用户头像
            cleaned_files.extend(CleanupService._cleanup_user_avatars())
            
            # 清理帖子图片
            cleaned_files.extend(CleanupService._cleanup_post_images())
            
            logger.info(f"清理孤立文件完成，共删除 {len(cleaned_files)} 个文件")
            return cleaned_files
            
        except Exception as e:
            logger.error(f"清理孤立文件失败: {str(e)}")
            return []
    
    @staticmethod
    def _cleanup_band_images():
        """清理孤立的乐队图片"""
        cleaned_files = []
        try:
            bands_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'bands')
            if not os.path.exists(bands_upload_dir):
                return cleaned_files
            
            # 获取所有数据库中引用的乐队图片
            referenced_images = set()
            from models import Band
            bands = Band.query.all()
            for band in bands:
                if band.banner_image_url:
                    filename = band.banner_image_url.split('/')[-1]
                    referenced_images.add(filename)
            
            # 检查目录中的所有图片文件
            for filename in os.listdir(bands_upload_dir):
                file_path = os.path.join(bands_upload_dir, filename)
                if os.path.isfile(file_path) and filename not in referenced_images:
                    if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        try:
                            os.remove(file_path)
                            cleaned_files.append(f"bands/{filename}")
                            logger.info(f"清理孤立乐队图片: {file_path}")
                        except Exception as e:
                            logger.warning(f"清理孤立乐队图片失败 {file_path}: {str(e)}")
            
        except Exception as e:
            logger.error(f"清理孤立乐队图片失败: {str(e)}")
        
        return cleaned_files
    
    @staticmethod
    def _cleanup_member_avatars():
        """清理孤立的成员头像"""
        cleaned_files = []
        try:
            members_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'members')
            if not os.path.exists(members_upload_dir):
                return cleaned_files
            
            # 获取所有数据库中引用的成员头像
            referenced_avatars = set()
            from models import Member
            members = Member.query.all()
            for member in members:
                if member.avatar_url:
                    filename = member.avatar_url.split('/')[-1]
                    referenced_avatars.add(filename)
            
            # 检查目录中的所有图片文件
            for filename in os.listdir(members_upload_dir):
                file_path = os.path.join(members_upload_dir, filename)
                if os.path.isfile(file_path) and filename not in referenced_avatars:
                    if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        try:
                            os.remove(file_path)
                            cleaned_files.append(f"members/{filename}")
                            logger.info(f"清理孤立成员头像: {file_path}")
                        except Exception as e:
                            logger.warning(f"清理孤立成员头像失败 {file_path}: {str(e)}")
            
        except Exception as e:
            logger.error(f"清理孤立成员头像失败: {str(e)}")
        
        return cleaned_files
    
    @staticmethod
    def _cleanup_event_posters():
        """清理孤立的活动海报"""
        cleaned_files = []
        try:
            events_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'events')
            if not os.path.exists(events_upload_dir):
                return cleaned_files
            
            # 获取所有数据库中引用的活动海报
            referenced_posters = set()
            from models import Event
            events = Event.query.all()
            for event in events:
                if event.poster_image_url:
                    filename = event.poster_image_url.split('/')[-1]
                    referenced_posters.add(filename)
            
            # 检查目录中的所有图片文件
            for filename in os.listdir(events_upload_dir):
                file_path = os.path.join(events_upload_dir, filename)
                if os.path.isfile(file_path) and filename not in referenced_posters:
                    if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        try:
                            os.remove(file_path)
                            cleaned_files.append(f"events/{filename}")
                            logger.info(f"清理孤立活动海报: {file_path}")
                        except Exception as e:
                            logger.warning(f"清理孤立活动海报失败 {file_path}: {str(e)}")
            
        except Exception as e:
            logger.error(f"清理孤立活动海报失败: {str(e)}")
        
        return cleaned_files
    
    @staticmethod
    def _cleanup_user_avatars():
        """清理孤立的用户头像"""
        cleaned_files = []
        try:
            avatars_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
            if not os.path.exists(avatars_upload_dir):
                return cleaned_files
            
            # 获取所有数据库中引用的用户头像
            referenced_avatars = set()
            users = User.query.all()
            for user in users:
                if user.avatar_url:
                    filename = user.avatar_url.split('/')[-1]
                    referenced_avatars.add(filename)
            
            # 检查目录中的所有图片文件
            for filename in os.listdir(avatars_upload_dir):
                file_path = os.path.join(avatars_upload_dir, filename)
                if os.path.isfile(file_path) and filename not in referenced_avatars:
                    if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        try:
                            os.remove(file_path)
                            cleaned_files.append(f"avatars/{filename}")
                            logger.info(f"清理孤立用户头像: {file_path}")
                        except Exception as e:
                            logger.warning(f"清理孤立用户头像失败 {file_path}: {str(e)}")
            
        except Exception as e:
            logger.error(f"清理孤立用户头像失败: {str(e)}")
        
        return cleaned_files
    
    @staticmethod
    def _cleanup_post_images():
        """清理孤立的帖子图片"""
        cleaned_files = []
        try:
            # 检查多个可能的帖子图片目录
            possible_dirs = [
                os.path.join(current_app.config['UPLOAD_FOLDER'], 'posts'),
                os.path.join(current_app.config['UPLOAD_FOLDER'], 'community'),
                os.path.join(current_app.config['UPLOAD_FOLDER'], 'community', 'posts')
            ]
            
            for posts_upload_dir in possible_dirs:
                if not os.path.exists(posts_upload_dir):
                    continue
                
                logger.info(f"检查帖子图片目录: {posts_upload_dir}")
                
                # 获取所有数据库中引用的帖子图片
                referenced_images = set()
                posts = Post.query.all()
                for post in posts:
                    image_urls = post.get_image_urls()
                    for image_url in image_urls:
                        if image_url:
                            filename = image_url.split('/')[-1]
                            referenced_images.add(filename)
                
                logger.info(f"数据库中引用的帖子图片: {len(referenced_images)} 个")
                
                # 检查目录中的所有图片文件
                for filename in os.listdir(posts_upload_dir):
                    file_path = os.path.join(posts_upload_dir, filename)
                    if os.path.isfile(file_path) and filename not in referenced_images:
                        if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                            try:
                                os.remove(file_path)
                                cleaned_files.append(f"{os.path.basename(posts_upload_dir)}/{filename}")
                                logger.info(f"清理孤立帖子图片: {file_path}")
                            except Exception as e:
                                logger.warning(f"清理孤立帖子图片失败 {file_path}: {str(e)}")
                
                # 如果找到了目录并处理了，就跳出循环
                break
            
        except Exception as e:
            logger.error(f"清理孤立帖子图片失败: {str(e)}")
        
        return cleaned_files
    
    @staticmethod
    def run_full_cleanup():
        """运行完整的清理任务"""
        try:
            logger.info("开始运行完整清理任务...")
            
            results = {
                'expired_verifications': CleanupService.cleanup_expired_email_verifications(),
                'old_reports': CleanupService.cleanup_old_reports(),
                'orphaned_likes': CleanupService.cleanup_orphaned_likes(),
                'orphaned_user_data': CleanupService.cleanup_orphaned_user_data(),
                'orphaned_files': CleanupService.cleanup_orphaned_files()
            }
            
            # 计算总清理数量
            total_cleaned = 0
            for key, value in results.items():
                if key == 'orphaned_files':
                    total_cleaned += len(value) if isinstance(value, list) else value
                elif key == 'orphaned_user_data':
                    total_cleaned += sum(value.values()) if isinstance(value, dict) else value
                else:
                    total_cleaned += value
            
            logger.info(f"完整清理任务完成，共清理 {total_cleaned} 项数据")
            return results
            
        except Exception as e:
            logger.error(f"运行完整清理任务失败: {str(e)}")
            return None

    @staticmethod
    def run_quick_cleanup():
        """运行快速清理任务（只清理数据库数据）"""
        try:
            logger.info("开始运行快速清理任务...")
            
            results = {
                'expired_verifications': CleanupService.cleanup_expired_email_verifications(),
                'old_reports': CleanupService.cleanup_old_reports(),
                'orphaned_likes': CleanupService.cleanup_orphaned_likes(),
                'orphaned_user_data': CleanupService.cleanup_orphaned_user_data()
            }
            
            # 计算总清理数量
            total_cleaned = 0
            for key, value in results.items():
                if key == 'orphaned_user_data':
                    total_cleaned += sum(value.values()) if isinstance(value, dict) else value
                else:
                    total_cleaned += value
            logger.info(f"快速清理任务完成，共清理 {total_cleaned} 项数据")
            return results
            
        except Exception as e:
            logger.error(f"运行快速清理任务失败: {str(e)}")
            return None

    @staticmethod
    def run_file_cleanup():
        """只运行文件清理任务"""
        try:
            logger.info("开始运行文件清理任务...")
            
            cleaned_files = CleanupService.cleanup_orphaned_files()
            
            logger.info(f"文件清理任务完成，共清理 {len(cleaned_files)} 个文件")
            return cleaned_files
            
        except Exception as e:
            logger.error(f"运行文件清理任务失败: {str(e)}")
            return []

    @staticmethod
    def get_cleanup_status():
        """获取清理状态统计"""
        try:
            from models import EmailVerification, Report, Like, Band, Member, Event, User, Post
            
            status = {
                'expired_verifications': EmailVerification.query.filter(
                    EmailVerification.expires_at < datetime.utcnow()
                ).count(),
                'old_reports': Report.query.filter(
                    Report.status.in_(['resolved', 'dismissed']),
                    Report.created_at < datetime.utcnow() - timedelta(days=30)
                ).count(),
                'orphaned_bands': db.session.query(Band).outerjoin(
                    User, Band.owner_id == User.id
                ).filter(
                    Band.owner_id.isnot(None),
                    User.id.is_(None)
                ).count(),
                'orphaned_members': db.session.query(Member).outerjoin(
                    User, Member.owner_id == User.id
                ).filter(
                    Member.owner_id.isnot(None),
                    User.id.is_(None)
                ).count(),
                'orphaned_events': db.session.query(Event).outerjoin(
                    User, Event.owner_id == User.id
                ).filter(
                    Event.owner_id.isnot(None),
                    User.id.is_(None)
                ).count(),
                'orphaned_posts': db.session.query(Post).outerjoin(
                    User, Post.author_id == User.id
                ).filter(
                    Post.author_id.isnot(None),
                    User.id.is_(None)
                ).count(),
                'total_bands': Band.query.count(),
                'total_members': Member.query.count(),
                'total_events': Event.query.count(),
                'total_users': User.query.count(),
                'total_posts': Post.query.count(),
                'total_likes': Like.query.count(),
                'total_reports': Report.query.count()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"获取清理状态失败: {str(e)}")
            return None


def main():
    """主函数 - 可以直接运行此脚本进行清理"""
    import argparse
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('cleanup_service.log', encoding='utf-8')
        ]
    )
    
    parser = argparse.ArgumentParser(description='数据清理服务')
    parser.add_argument('--mode', choices=['full', 'quick', 'files', 'status'], 
                       default='full', help='清理模式: full(完整清理), quick(快速清理), files(仅文件), status(查看状态)')
    parser.add_argument('--dry-run', action='store_true', help='试运行模式，不实际删除')
    parser.add_argument('--force', action='store_true', help='强制清理，跳过确认')
    
    args = parser.parse_args()
    
    try:
        # 创建Flask应用上下文
        from app_factory import create_app
        app = create_app()
        
        with app.app_context():
            logger.info("🚀 启动数据清理服务...")
            
            if args.mode == 'status':
                # 查看清理状态
                status = CleanupService.get_cleanup_status()
                if status:
                    print("\n📊 数据清理状态:")
                    print(f"  - 过期邮箱验证码: {status['expired_verifications']} 个")
                    print(f"  - 旧举报记录: {status['old_reports']} 个")
                    print(f"  - 孤立乐队: {status['orphaned_bands']} 个")
                    print(f"  - 孤立成员: {status['orphaned_members']} 个")
                    print(f"  - 孤立活动: {status['orphaned_events']} 个")
                    print(f"  - 孤立帖子: {status['orphaned_posts']} 个")
                    print(f"  - 总乐队数: {status['total_bands']} 个")
                    print(f"  - 总成员数: {status['total_members']} 个")
                    print(f"  - 总活动数: {status['total_events']} 个")
                    print(f"  - 总用户数: {status['total_users']} 个")
                    print(f"  - 总帖子数: {status['total_posts']} 个")
                    print(f"  - 总点赞数: {status['total_likes']} 个")
                    print(f"  - 总举报数: {status['total_reports']} 个")
                return
            
            # 确认清理操作
            if not args.force:
                print(f"⚠️  即将执行 {args.mode} 清理模式")
                print("⚠️  此操作将删除过期和孤立的数据/文件")
                confirm = input("确认继续? (y/N): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    print("❌ 操作已取消")
                    return
            
            # 执行清理
            if args.mode == 'full':
                print("🧹 执行完整清理...")
                results = CleanupService.run_full_cleanup()
                if results:
                    print("\n✅ 完整清理完成!")
                    print(f"  - 过期验证码: {results['expired_verifications']} 个")
                    print(f"  - 旧举报记录: {results['old_reports']} 个")
                    print(f"  - 孤立点赞: {results['orphaned_likes']} 个")
                    print(f"  - 已删除用户关联数据: {sum(results['orphaned_user_data'].values())} 项")
                    if results['orphaned_user_data']:
                        print("    - 乐队: {results['orphaned_user_data']['bands']} 个")
                        print("    - 成员: {results['orphaned_user_data']['members']} 个")
                        print("    - 活动: {results['orphaned_user_data']['events']} 个")
                        print("    - 帖子: {results['orphaned_user_data']['posts']} 个")
                        print("    - 评论: {results['orphaned_user_data']['comments']} 个")
                        print("    - 点赞: {results['orphaned_user_data']['likes']} 个")
                        print("    - 举报: {results['orphaned_user_data']['reports']} 个")
                    print(f"  - 孤立文件: {len(results['orphaned_files'])} 个")
                    if results['orphaned_files']:
                        print("  - 删除的文件:")
                        for file_path in results['orphaned_files']:
                            print(f"    * {file_path}")
                else:
                    print("❌ 完整清理失败")
                    
            elif args.mode == 'quick':
                print("⚡ 执行快速清理...")
                results = CleanupService.run_quick_cleanup()
                if results:
                    print("\n✅ 快速清理完成!")
                    print(f"  - 过期验证码: {results['expired_verifications']} 个")
                    print(f"  - 旧举报记录: {results['old_reports']} 个")
                    print(f"  - 孤立点赞: {results['orphaned_likes']} 个")
                    print(f"  - 已删除用户关联数据: {sum(results['orphaned_user_data'].values())} 项")
                    if results['orphaned_user_data']:
                        print("    - 乐队: {results['orphaned_user_data']['bands']} 个")
                        print("    - 成员: {results['orphaned_user_data']['members']} 个")
                        print("    - 活动: {results['orphaned_user_data']['events']} 个")
                        print("    - 帖子: {results['orphaned_user_data']['posts']} 个")
                        print("    - 评论: {results['orphaned_user_data']['comments']} 个")
                        print("    - 点赞: {results['orphaned_user_data']['likes']} 个")
                        print("    - 举报: {results['orphaned_user_data']['reports']} 个")
                else:
                    print("❌ 快速清理失败")
                    
            elif args.mode == 'files':
                print("🗂️  执行文件清理...")
                cleaned_files = CleanupService.run_file_cleanup()
                print(f"\n✅ 文件清理完成，共删除 {len(cleaned_files)} 个文件")
                if cleaned_files:
                    print("删除的文件:")
                    for file_path in cleaned_files:
                        print(f"  - {file_path}")
            
            logger.info("🎯 数据清理服务执行完成")
            
    except Exception as e:
        logger.error(f"❌ 数据清理服务执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
