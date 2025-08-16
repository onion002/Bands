from flask import Blueprint, request, jsonify, current_app
from models import db, User, Post, Report, UserType
from auth_decorators import require_superadmin
from werkzeug.security import generate_password_hash
from sqlalchemy import or_
import os
import logging

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)


def delete_user_related_files(user):
    """删除用户相关的所有文件"""
    deleted_files = []
    
    try:
        # 1. 删除用户头像
        if user.avatar_url:
            try:
                avatar_filename = user.avatar_url.split('/')[-1]
                avatar_path = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    'avatars',
                    avatar_filename
                )
                if os.path.exists(avatar_path):
                    os.remove(avatar_path)
                    deleted_files.append(avatar_path)
                    logger.info(f"删除用户头像: {avatar_path}")
            except Exception as e:
                logger.warning(f"删除用户头像失败 {user.avatar_url}: {str(e)}")
        
        # 2. 删除用户上传的乐队图片（如果用户是乐队所有者）
        from models import Band
        owned_bands = Band.query.filter_by(owner_id=user.id).all()
        bands_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'bands')
        
        for band in owned_bands:
            if band.banner_image_url:
                try:
                    filename = band.banner_image_url.split('/')[-1]
                    file_path = os.path.join(bands_upload_dir, filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        deleted_files.append(file_path)
                        logger.info(f"删除用户拥有的乐队图片: {file_path}")
                except Exception as e:
                    logger.warning(f"删除用户拥有的乐队图片失败: {str(e)}")
        
        # 3. 删除用户上传的成员头像（如果用户是乐队所有者）
        from models import Member
        owned_members = Member.query.filter_by(owner_id=user.id).all()
        members_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'members')
        
        for member in owned_members:
            if member.avatar_url:
                try:
                    filename = member.avatar_url.split('/')[-1]
                    file_path = os.path.join(members_upload_dir, filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        deleted_files.append(file_path)
                        logger.info(f"删除用户拥有的成员头像: {file_path}")
                except Exception as e:
                    logger.warning(f"删除用户拥有的成员头像失败: {str(e)}")
        
        # 4. 删除用户上传的活动海报（如果用户是活动所有者）
        from models import Event
        owned_events = Event.query.filter_by(owner_id=user.id).all()
        events_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'events')
        
        for event in owned_events:
            if event.poster_image_url:
                try:
                    filename = event.poster_image_url.split('/')[-1]
                    file_path = os.path.join(events_upload_dir, filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        deleted_files.append(file_path)
                        logger.info(f"删除用户拥有的活动海报: {file_path}")
                except Exception as e:
                    logger.warning(f"删除用户拥有的活动海报失败: {str(e)}")
        
        logger.info(f"用户 {user.username} 相关文件删除完成，共删除 {len(deleted_files)} 个文件")
        return deleted_files
        
    except Exception as e:
        logger.error(f"删除用户相关文件时发生错误: {str(e)}")
        return deleted_files


def delete_user_related_data(user):
    """删除用户关联的所有数据库数据"""
    deleted_data = {
        'bands': 0,
        'members': 0,
        'events': 0,
        'posts': 0,
        'comments': 0,
        'likes': 0,
        'reports': 0
    }
    
    try:
        from models import Band, Member, Event, Post, Comment, Like, Report
        
        # 1. 删除用户拥有的乐队（会级联删除成员）
        owned_bands = Band.query.filter_by(owner_id=user.id).all()
        for band in owned_bands:
            try:
                db.session.delete(band)
                deleted_data['bands'] += 1
                logger.info(f"删除用户拥有的乐队: {band.name}")
            except Exception as e:
                logger.warning(f"删除乐队失败 {band.name}: {str(e)}")
        
        # 2. 删除用户拥有的成员（如果还有的话）
        owned_members = Member.query.filter_by(owner_id=user.id).all()
        for member in owned_members:
            try:
                db.session.delete(member)
                deleted_data['members'] += 1
                logger.info(f"删除用户拥有的成员: {member.name}")
            except Exception as e:
                logger.warning(f"删除成员失败 {member.name}: {str(e)}")
        
        # 3. 删除用户拥有的活动
        owned_events = Event.query.filter_by(owner_id=user.id).all()
        for event in owned_events:
            try:
                db.session.delete(event)
                deleted_data['events'] += 1
                logger.info(f"删除用户拥有的活动: {event.title}")
            except Exception as e:
                logger.warning(f"删除活动失败 {event.title}: {str(e)}")
        
        # 4. 删除用户发布的帖子（会级联删除评论和点赞）
        user_posts = Post.query.filter_by(author_id=user.id).all()
        for post in user_posts:
            try:
                db.session.delete(post)
                deleted_data['posts'] += 1
                logger.info(f"删除用户发布的帖子: {post.title or f'帖子#{post.id}'}")
            except Exception as e:
                logger.warning(f"删除帖子失败 {post.id}: {str(e)}")
        
        # 5. 删除用户发布的评论（会级联删除点赞）
        user_comments = Comment.query.filter_by(author_id=user.id).all()
        for comment in user_comments:
            try:
                db.session.delete(comment)
                deleted_data['comments'] += 1
                logger.info(f"删除用户发布的评论: {comment.content[:50]}...")
            except Exception as e:
                logger.warning(f"删除评论失败 {comment.id}: {str(e)}")
        
        # 6. 删除用户的点赞记录
        user_likes = Like.query.filter_by(user_id=user.id).all()
        for like in user_likes:
            try:
                db.session.delete(like)
                deleted_data['likes'] += 1
            except Exception as e:
                logger.warning(f"删除点赞记录失败 {like.id}: {str(e)}")
        
        # 7. 删除用户的举报记录
        user_reports = Report.query.filter_by(reporter_id=user.id).all()
        for report in user_reports:
            try:
                db.session.delete(report)
                deleted_data['reports'] += 1
            except Exception as e:
                logger.warning(f"删除举报记录失败 {report.id}: {str(e)}")
        
        # 8. 删除用户作为被举报者的相关记录
        # 如果用户被举报，需要处理相关记录
        target_reports = Report.query.filter_by(target_id=user.id, target_type='user').all()
        for report in target_reports:
            try:
                db.session.delete(report)
                deleted_data['reports'] += 1
            except Exception as e:
                logger.warning(f"删除针对用户的举报记录失败 {report.id}: {str(e)}")
        
        logger.info(f"用户 {user.username} 关联数据删除完成: {deleted_data}")
        return deleted_data
        
    except Exception as e:
        logger.error(f"删除用户关联数据时发生错误: {str(e)}")
        return deleted_data


# 用户管理
@admin_bp.route('/users', methods=['GET'])
@require_superadmin
def list_users():
    keyword = (request.args.get('q') or '').strip()
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    
    # 新增筛选参数
    role_filter = request.args.get('role')  # user, admin, superadmin
    status_filter = request.args.get('status')  # active, inactive
    date_from = request.args.get('date_from')  # YYYY-MM-DD
    date_to = request.args.get('date_to')  # YYYY-MM-DD
    export_csv = request.args.get('export') == 'csv'

    query = User.query
    if keyword:
        like = f"%{keyword}%"
        # 兼容 MySQL，使用 like
        query = query.filter(or_(
            User.username.like(like),
            User.email.like(like),
            User.display_name.like(like)
        ))
    
    # 角色筛选
    if role_filter:
        query = query.filter(User.user_type == role_filter)
    
    # 状态筛选
    if status_filter == 'active':
        query = query.filter(User.is_active == True)
    elif status_filter == 'inactive':
        query = query.filter(User.is_active == False)
    
    # 时间筛选
    if date_from:
        try:
            from datetime import datetime
            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(User.created_at >= start_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            from datetime import datetime
            end_date = datetime.strptime(date_to, '%Y-%m-%d')
            # 包含整天，所以加1天
            end_date = end_date.replace(hour=23, minute=59, second=59)
            query = query.filter(User.created_at <= end_date)
        except ValueError:
            pass
    
    query = query.order_by(User.created_at.desc())
    
    # CSV导出
    if export_csv:
        users = query.all()
        import csv
        import io
        from flask import make_response
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # CSV标题行
        writer.writerow(['ID', '用户名', '显示名', '邮箱', '用户类型', '状态', '注册时间', '最后登录'])
        
        for user in users:
            writer.writerow([
                user.id,
                user.username,
                user.display_name or '',
                user.email,
                {'user': '普通用户', 'admin': '管理员', 'superadmin': '超级管理员'}.get(user.user_type, user.user_type),
                '激活' if user.is_active else '禁用',
                user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else '',
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else ''
            ])
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename="users_export.csv"'
        return response
    
    # 正常分页返回
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    users = [u.to_dict(include_sensitive=True) for u in pagination.items]
    return jsonify({'items': users, 'total': pagination.total, 'page': pagination.page, 'pages': pagination.pages})


@admin_bp.route('/users/<int:user_id>', methods=['PATCH'])
@require_superadmin
def update_user(user_id: int):
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error': '用户不存在'}), 404
    data = request.json or {}
    if 'is_active' in data:
        u.is_active = bool(data['is_active'])
    if 'display_name' in data:
        u.display_name = data['display_name']
    if 'user_type' in data and data['user_type'] in [t.value for t in UserType]:
        # 保证超级管理员唯一
        if data['user_type'] == UserType.SUPERADMIN.value:
            existing = User.query.filter(User.user_type == UserType.SUPERADMIN).first()
            if existing and existing.id != user_id:
                return jsonify({'error': '已存在超级管理员，无法再设置'}), 400
        u.user_type = UserType(data['user_type'])
    if 'password' in data and data['password']:
        u.password_hash = generate_password_hash(data['password'])
    db.session.commit()
    return jsonify({'message': '更新成功', 'user': u.to_dict(include_sensitive=True)})


# 批量更新（状态/角色）
@admin_bp.route('/users/batch_update', methods=['POST'])
@require_superadmin
def batch_update_users():
    data = request.json or {}
    ids = data.get('user_ids') or []
    if not ids:
        return jsonify({'error': '缺少用户ID列表'}), 400
    update_fields = {}
    if 'is_active' in data:
        update_fields['is_active'] = bool(data['is_active'])
    if 'user_type' in data and data['user_type'] in [t.value for t in UserType]:
        # 保证超级管理员唯一
        if data['user_type'] == UserType.SUPERADMIN.value:
            existing = User.query.filter(User.user_type == UserType.SUPERADMIN).first()
            if existing and existing.id not in ids:
                return jsonify({'error': '已存在超级管理员，无法再设置'}), 400
        update_fields['user_type'] = UserType(data['user_type'])
    if not update_fields:
        return jsonify({'error': '没有可更新的字段'}), 400
    users = User.query.filter(User.id.in_(ids)).all()
    for u in users:
        for k, v in update_fields.items():
            setattr(u, k, v)
    db.session.commit()
    return jsonify({'message': '批量更新成功', 'count': len(users)})


# 批量删除
@admin_bp.route('/users/batch_delete', methods=['POST'])
@require_superadmin
def batch_delete_users():
    data = request.json or {}
    ids = data.get('user_ids') or []
    if not ids:
        return jsonify({'error': '缺少用户ID列表'}), 400
    
    users = User.query.filter(User.id.in_(ids)).all()
    if len(users) != len(ids):
        found_ids = [user.id for user in users]
        missing_ids = [uid for uid in ids if uid not in found_ids]
        return jsonify({'error': f'以下用户不存在: {missing_ids}'}), 404
    
    deleted_users = []
    total_deleted_files = 0
    
    # 逐个删除用户
    for user in users:
            try:
                username = user.username
                
                # 删除相关文件
                deleted_files = delete_user_related_files(user)
                total_deleted_files += len(deleted_files)
                
                # 删除关联数据
                deleted_data = delete_user_related_data(user)
                total_deleted_data = sum(deleted_data.values())
                total_deleted_files += total_deleted_data
                
                # 删除数据库记录
                db.session.delete(user)
                
                deleted_users.append({
                    'id': user.id,
                    'username': username,
                    'deleted_files_count': len(deleted_files),
                    'deleted_data_count': total_deleted_data,
                    'deleted_data_details': deleted_data
                })
                
            except Exception as e:
                logger.error(f"删除用户 {user.username} 时发生错误: {str(e)}")
                # 继续删除其他用户，不中断整个过程
                continue
    
    # 提交所有删除操作
    db.session.commit()
    
    return jsonify({
        'message': f'成功删除 {len(deleted_users)} 个用户',
        'deleted_users': deleted_users,
        'total_deleted_files': total_deleted_files
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_superadmin
def delete_user(user_id: int):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 记录用户信息用于日志
        username = user.username
        
        # 删除用户相关的所有文件
        deleted_files = delete_user_related_files(user)
        
        # 删除关联数据
        deleted_data = delete_user_related_data(user)
        total_deleted_files = len(deleted_files) + sum(deleted_data.values())
        
        # 删除数据库记录
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': f'用户 "{username}" 删除成功',
            'deleted_files_count': total_deleted_files
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除用户失败: {str(e)}", exc_info=True)
        return jsonify({'error': '删除用户失败'}), 500


# 帖子强删（超级管理员）
@admin_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@require_superadmin
def force_delete_post(post_id: int):
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'error': '帖子不存在'}), 404
        
        # 记录帖子信息用于日志
        post_title = post.title or f"帖子#{post.id}"
        
        # 删除帖子相关的所有文件
        from api.community import delete_post_related_files
        deleted_files = delete_post_related_files(post)
        
        # 删除数据库记录
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({
            'message': f'帖子 "{post_title}" 强制删除成功',
            'deleted_files_count': len(deleted_files)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"强制删除帖子失败: {str(e)}", exc_info=True)
        return jsonify({'error': '强制删除帖子失败'}), 500


# 批量强制删除帖子（超级管理员）
@admin_bp.route('/posts/batch_force_delete', methods=['POST'])
@require_superadmin
def batch_force_delete_posts():
    """批量强制删除帖子（超级管理员权限）"""
    try:
        data = request.json or {}
        
        if not data or 'post_ids' not in data:
            return jsonify({'error': '请提供要删除的帖子ID列表'}), 400
        
        post_ids = data['post_ids']
        if not isinstance(post_ids, list) or not post_ids:
            return jsonify({'error': '帖子ID列表不能为空'}), 400
        
        # 验证所有帖子是否存在
        posts = Post.query.filter(Post.id.in_(post_ids)).all()
        if len(posts) != len(post_ids):
            found_ids = [post.id for post in posts]
            missing_ids = [pid for pid in post_ids if pid not in found_ids]
            return jsonify({'error': f'以下帖子不存在: {missing_ids}'}), 404
        
        deleted_posts = []
        total_deleted_files = 0
        
        # 逐个删除帖子
        for post in posts:
            try:
                post_title = post.title or f"帖子#{post.id}"
                
                # 删除相关文件
                from api.community import delete_post_related_files
                deleted_files = delete_post_related_files(post)
                total_deleted_files += len(deleted_files)
                
                # 删除数据库记录
                db.session.delete(post)
                
                deleted_posts.append({
                    'id': post.id,
                    'title': post_title,
                    'deleted_files_count': len(deleted_files)
                })
                
            except Exception as e:
                logger.error(f"强制删除帖子 {post.id} 时发生错误: {str(e)}")
                # 继续删除其他帖子，不中断整个过程
                continue
        
        # 提交所有删除操作
        db.session.commit()
        
        return jsonify({
            'message': f'成功强制删除 {len(deleted_posts)} 个帖子',
            'deleted_posts': deleted_posts,
            'total_deleted_files': total_deleted_files
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"批量强制删除帖子失败: {str(e)}", exc_info=True)
        return jsonify({'error': '批量强制删除帖子失败'}), 500


# 评论强删（超级管理员）
@admin_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@require_superadmin
def force_delete_comment(comment_id: int):
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'error': '评论不存在'}), 404
        
        # 记录评论信息用于日志
        comment_content = comment.content[:50] + '...' if len(comment.content) > 50 else comment.content
        
        # 删除评论相关的所有文件
        from api.community import delete_comment_related_files
        deleted_files = delete_comment_related_files(comment)
        
        # 删除数据库记录
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({
            'message': f'评论强制删除成功',
            'deleted_files_count': len(deleted_files)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"强制删除评论失败: {str(e)}", exc_info=True)
        return jsonify({'error': '强制删除评论失败'}), 500


# 批量强制删除评论（超级管理员）
@admin_bp.route('/comments/batch_force_delete', methods=['POST'])
@require_superadmin
def batch_force_delete_comments():
    """批量强制删除评论（超级管理员权限）"""
    try:
        data = request.json or {}
        
        if not data or 'comment_ids' not in data:
            return jsonify({'error': '请提供要删除的评论ID列表'}), 400
        
        comment_ids = data['comment_ids']
        if not isinstance(comment_ids, list) or not comment_ids:
            return jsonify({'error': '评论ID列表不能为空'}), 400
        
        # 验证所有评论是否存在
        from models import Comment
        comments = Comment.query.filter(Comment.id.in_(comment_ids)).all()
        if len(comments) != len(comment_ids):
            found_ids = [comment.id for comment in comments]
            missing_ids = [cid for cid in comment_ids if cid not in found_ids]
            return jsonify({'error': f'以下评论不存在: {missing_ids}'}), 404
        
        deleted_comments = []
        total_deleted_files = 0
        
        # 逐个删除评论
        for comment in comments:
            try:
                # 删除相关文件
                from api.community import delete_comment_related_files
                deleted_files = delete_comment_related_files(comment)
                total_deleted_files += len(deleted_files)
                
                # 删除数据库记录
                db.session.delete(comment)
                
                deleted_comments.append({
                    'id': comment.id,
                    'deleted_files_count': len(deleted_files)
                })
                
            except Exception as e:
                logger.error(f"强制删除评论 {comment.id} 时发生错误: {str(e)}")
                # 继续删除其他评论，不中断整个过程
                continue
        
        # 提交所有删除操作
        db.session.commit()
        
        return jsonify({
            'message': f'成功强制删除 {len(deleted_comments)} 个评论',
            'deleted_comments': deleted_comments,
            'total_deleted_files': total_deleted_files
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"批量强制删除评论失败: {str(e)}", exc_info=True)
        return jsonify({'error': '批量强制删除评论失败'}), 500


# 举报管理
@admin_bp.route('/reports', methods=['GET'])
@require_superadmin
def admin_list_reports():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    status_filter = request.args.get('status')  # pending, resolved, dismissed
    
    query = Report.query
    
    # 状态筛选
    if status_filter:
        query = query.filter(Report.status == status_filter)
    
    query = query.order_by(Report.created_at.desc())
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    reports = []
    for r in pagination.items:
        report_dict = r.to_dict()
        # 添加目标内容信息
        if r.target_type == 'post':
            post = Post.query.get(r.target_id)
            if post:
                report_dict['target_content'] = {
                    'id': post.id,
                    'author': post.author.username if post.author else 'Unknown',
                    'content': post.content[:100] + '...' if len(post.content) > 100 else post.content,
                    'created_at': post.created_at.isoformat() if post.created_at else None
                }
        elif r.target_type == 'comment':
            from models import Comment
            comment = Comment.query.get(r.target_id)
            if comment:
                report_dict['target_content'] = {
                    'id': comment.id,
                    'author': comment.author.username if comment.author else 'Unknown',
                    'content': comment.content[:100] + '...' if len(comment.content) > 100 else comment.content,
                    'post_id': comment.post_id,
                    'created_at': comment.created_at.isoformat() if comment.created_at else None
                }
        reports.append(report_dict)
    
    return jsonify({
        'items': reports,
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages
    })


@admin_bp.route('/reports/<int:report_id>', methods=['PATCH'])
@require_superadmin
def admin_update_report(report_id: int):
    from sqlalchemy.exc import SQLAlchemyError
    r = Report.query.get(report_id)
    if not r:
        return jsonify({'error': '举报不存在'}), 404
    data = request.json or {}
    status = data.get('status')
    if status not in ('pending', 'resolved', 'dismissed'):
        return jsonify({'error': '无效的状态'}), 400
    r.status = status
    try:
        db.session.commit()
        return jsonify({'message': '更新成功', 'report': r.to_dict()})
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': '更新失败'}), 500


# 手动触发清理任务
@admin_bp.route('/cleanup/run', methods=['POST'])
@require_superadmin
def run_cleanup_task():
    """手动触发数据清理任务"""
    try:
        from services.cleanup_service import CleanupService
        
        # 运行完整清理任务
        results = CleanupService.run_full_cleanup()
        
        if results is None:
            return jsonify({'error': '清理任务执行失败'}), 500
        
        return jsonify({
            'message': '清理任务执行成功',
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"执行清理任务失败: {str(e)}", exc_info=True)
        return jsonify({'error': '执行清理任务失败'}), 500


# 获取清理任务状态
@admin_bp.route('/cleanup/status', methods=['GET'])
@require_superadmin
def get_cleanup_status():
    """获取数据清理任务状态"""
    try:
        from services.cleanup_service import CleanupService
        from datetime import datetime, timedelta
        
        # 统计各种数据量
        stats = {
            'total_users': User.query.count(),
            'total_posts': Post.query.count(),
            'total_comments': Comment.query.count(),
            'total_reports': Report.query.count(),
            'expired_verifications': EmailVerification.query.filter(
                EmailVerification.expires_at < datetime.utcnow()
            ).count(),
            'old_reports': Report.query.filter(
                Report.status.in_(['resolved', 'dismissed']),
                Report.created_at < datetime.utcnow() - timedelta(days=30)
            ).count()
        }
        
        return jsonify({
            'message': '获取清理状态成功',
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"获取清理状态失败: {str(e)}", exc_info=True)
        return jsonify({'error': '获取清理状态失败'}), 500


