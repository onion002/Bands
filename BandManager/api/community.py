from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_, desc
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
import os
import uuid
import logging
from datetime import datetime
from utils.timezone_utils import get_beijing_now_for_db

from models import db, User, Post, Comment, Tag, Like, Report
from auth_decorators import require_auth, require_admin, optional_auth, get_current_user, require_superadmin

logger = logging.getLogger(__name__)
community_bp = Blueprint('community', __name__)


def _serialize_post(post: Post):
    return post.to_dict(include_author=True)


def delete_post_related_files(post):
    """删除帖子相关的所有图片文件"""
    deleted_files = []
    
    try:
        # 1. 删除帖子中的图片文件
        image_urls = post.get_image_urls()
        if image_urls:
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
                
                for image_url in image_urls:
                    if not image_url:
                        continue
                        
                    try:
                        filename = image_url.split('/')[-1]
                        file_path = os.path.join(posts_upload_dir, filename)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            deleted_files.append(file_path)
                            logger.info(f"删除帖子图片: {file_path}")
                    except Exception as e:
                        logger.warning(f"删除帖子图片失败 {image_url}: {str(e)}")
                
                # 如果找到了目录并处理了，就跳出循环
                break
        
        logger.info(f"帖子 {post.id} 相关文件删除完成，共删除 {len(deleted_files)} 个文件")
        return deleted_files
        
    except Exception as e:
        logger.error(f"删除帖子相关文件时发生错误: {str(e)}")
        return deleted_files


def delete_comment_related_files(comment):
    """删除评论相关的所有文件（目前评论没有文件，预留接口）"""
    # 评论目前没有文件附件，预留接口以便将来扩展
    return []


@community_bp.route('/posts', methods=['GET'])
@optional_auth
def list_posts():
    try:
        sort = request.args.get('sort', 'latest')  # latest | hot
        search = request.args.get('search')
        tag = request.args.get('tag')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))

        query = Post.query

        if search:
            like_expr = f"%{search}%"
            query = query.filter(or_(Post.title.ilike(like_expr), Post.content.ilike(like_expr)))

        if tag:
            query = query.join(Post.tags).filter(Tag.name == tag)

        if sort == 'hot':
            query = query.order_by(desc(Post.like_count), desc(Post.comment_count), desc(Post.created_at))
        else:
            query = query.order_by(desc(Post.created_at))

        pagination = query.paginate(page=page, per_page=page_size, error_out=False)

        # 序列化
        posts = [_serialize_post(p) for p in pagination.items]

        # 标记当前用户是否点赞
        user = get_current_user()
        if user:
            post_ids = [p.id for p in pagination.items]
            if post_ids:
                liked = Like.query.filter(Like.user_id == user.id, Like.post_id.in_(post_ids)).all()
                liked_ids = {l.post_id for l in liked if l.post_id}
                for p in posts:
                    p['liked_by_me'] = p['id'] in liked_ids

        return jsonify({
            'items': posts,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages
        })
    except Exception as e:
        current_app.logger.exception('获取帖子列表失败')
        return jsonify({'error': '服务器内部错误'}), 500


@community_bp.route('/me/likes', methods=['GET'])
@require_auth
def list_my_liked_posts():
    try:
        user = get_current_user()
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))

        query = Post.query.join(Like, Like.post_id == Post.id).filter(Like.user_id == user.id)
        query = query.order_by(desc(Post.created_at))
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        items = [_serialize_post(p) for p in pagination.items]
        return jsonify({
            'items': items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages
        })
    except Exception:
        current_app.logger.exception('获取我的点赞帖子失败')
        return jsonify({'error': '服务器内部错误'}), 500


@community_bp.route('/posts', methods=['POST'])
@require_auth
def create_post():
    try:
        user = get_current_user()
        data = request.json or {}

        content = (data.get('content') or '').strip()
        if not content:
            return jsonify({'error': '内容不能为空'}), 400

        title = (data.get('title') or '').strip() or None
        image_urls = data.get('image_urls') or []
        link_urls = data.get('link_urls') or []
        tags = data.get('tags') or []

        post = Post(title=title, content=content, author_id=user.id)
        post.set_image_urls(image_urls)
        post.set_link_urls(link_urls)

        # 处理标签：存在则使用，不存在则创建
        tag_objs = []
        for t in tags:
            name = (t or '').strip()
            if not name:
                continue
            tag_obj = Tag.query.filter_by(name=name).first()
            if not tag_obj:
                tag_obj = Tag(name=name)
                db.session.add(tag_obj)
            tag_objs.append(tag_obj)
        post.tags = tag_objs

        db.session.add(post)
        db.session.commit()
        return jsonify({'message': '发布成功', 'post': _serialize_post(post)}), 201
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception('创建帖子失败')
        return jsonify({'error': '创建帖子失败'}), 500


@community_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id: int):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': '帖子不存在'}), 404
    return jsonify(_serialize_post(post))


@community_bp.route('/posts/<int:post_id>', methods=['PUT'])
@require_auth
def update_post(post_id: int):
    """更新帖子（仅作者可以操作）"""
    try:
        user = get_current_user()
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'error': '帖子不存在'}), 404
        
        # 只有帖子作者可以编辑
        if post.author_id != user.id:
            return jsonify({'error': '只能编辑自己的帖子'}), 403
        
        data = request.json or {}
        content = (data.get('content') or '').strip()
        
        if not content:
            return jsonify({'error': '帖子内容不能为空'}), 400
        
        # 更新帖子内容
        post.content = content
        post.updated_at = get_beijing_now_for_db()
        
        # 处理标签
        tags = data.get('tags') or []
        tag_objs = []
        for t in tags:
            name = (t or '').strip()
            if not name:
                continue
            tag_obj = Tag.query.filter_by(name=name).first()
            if not tag_obj:
                tag_obj = Tag(name=name)
                db.session.add(tag_obj)
            tag_objs.append(tag_obj)
        post.tags = tag_objs
        
        # 处理链接URLs（如果提供的话）
        if 'link_urls' in data:
            post.set_link_urls(data.get('link_urls', []))
        
        # 处理图片URLs（如果提供的话）
        if 'image_urls' in data:
            post.set_image_urls(data.get('image_urls', []))
        
        db.session.commit()
        return jsonify({
            'message': '帖子更新成功',
            'post': _serialize_post(post)
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新帖子失败: {str(e)}")
        return jsonify({'error': '更新失败'}), 500


# 删除帖子
@community_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@require_auth
def delete_post(post_id):
    """删除帖子（作者或超级管理员可删除）"""
    try:
        user = get_current_user()
        post = Post.query.get(post_id)
        
        if not post:
            return jsonify({'error': '帖子不存在'}), 404
        
        # 检查权限：只有作者或超级管理员可以删除
        if not user.is_superadmin() and post.author_id != user.id:
            return jsonify({'error': '无权删除该帖子'}), 403
        
        # 记录帖子信息用于日志
        post_title = post.title or f"帖子#{post.id}"
        
        # 删除帖子相关的所有文件
        deleted_files = delete_post_related_files(post)
        
        # 删除数据库记录（由于设置了cascade='all, delete-orphan'，评论和点赞会自动删除）
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({
            'message': f'帖子 "{post_title}" 删除成功',
            'deleted_files_count': len(deleted_files)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除帖子失败: {str(e)}", exc_info=True)
        return jsonify({'error': '删除帖子失败'}), 500


# 批量删除帖子
@community_bp.route('/posts/batch_delete', methods=['POST'])
@require_auth
def batch_delete_posts():
    """批量删除帖子（作者或超级管理员可删除）"""
    try:
        user = get_current_user()
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
        
        # 检查权限：只有作者或超级管理员可以删除
        if not user.is_superadmin():
            unauthorized_posts = [post for post in posts if post.author_id != user.id]
            if unauthorized_posts:
                unauthorized_ids = [post.id for post in unauthorized_posts]
                return jsonify({'error': f'无权删除以下帖子: {unauthorized_ids}'}), 403
        
        deleted_posts = []
        total_deleted_files = 0
        
        # 逐个删除帖子
        for post in posts:
            try:
                post_title = post.title or f"帖子#{post.id}"
                
                # 删除相关文件
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
                logger.error(f"删除帖子 {post.id} 时发生错误: {str(e)}")
                # 继续删除其他帖子，不中断整个过程
                continue
        
        # 提交所有删除操作
        db.session.commit()
        
        return jsonify({
            'message': f'成功删除 {len(deleted_posts)} 个帖子',
            'deleted_posts': deleted_posts,
            'total_deleted_files': total_deleted_files
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"批量删除帖子失败: {str(e)}", exc_info=True)
        return jsonify({'error': '批量删除帖子失败'}), 500


@community_bp.route('/posts/<int:post_id>/like', methods=['POST'])
@require_auth
def like_post(post_id: int):
    try:
        user = get_current_user()
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'error': '帖子不存在'}), 404

        existing = Like.query.filter_by(user_id=user.id, post_id=post_id).first()
        if existing:
            db.session.delete(existing)
            post.like_count = max(0, (post.like_count or 0) - 1)
            action = 'unliked'
        else:
            like = Like(user_id=user.id, post_id=post_id)
            db.session.add(like)
            post.like_count = (post.like_count or 0) + 1
            action = 'liked'

        db.session.commit()
        return jsonify({'message': 'ok', 'action': action, 'like_count': post.like_count})
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': '操作失败'}), 500


@community_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def list_comments(post_id: int):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': '帖子不存在'}), 404
    comment_entities = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    comments = [c.to_dict(include_author=True) for c in comment_entities]

    # 标记当前用户是否点赞
    user = get_current_user()
    if user and comment_entities:
        comment_ids = [c.id for c in comment_entities]
        liked = Like.query.filter(Like.user_id == user.id, Like.comment_id.in_(comment_ids)).all()
        liked_ids = {l.comment_id for l in liked if l.comment_id}
        for c in comments:
            c['liked_by_me'] = c['id'] in liked_ids
    return jsonify({'items': comments, 'total': len(comments)})


@community_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@require_auth
def create_comment(post_id: int):
    try:
        user = get_current_user()
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'error': '帖子不存在'}), 404

        data = request.json or {}
        content = (data.get('content') or '').strip()
        if not content:
            return jsonify({'error': '评论内容不能为空'}), 400

        parent_id = data.get('parent_id')
        comment = Comment(content=content, post_id=post_id, author_id=user.id, parent_id=parent_id)
        db.session.add(comment)
        post.comment_count = (post.comment_count or 0) + 1
        db.session.commit()
        return jsonify({'message': '评论成功', 'comment': comment.to_dict(include_author=True), 'comment_count': post.comment_count}), 201
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': '评论失败'}), 500


@community_bp.route('/comments/<int:comment_id>/like', methods=['POST'])
@require_auth
def like_comment(comment_id: int):
    try:
        user = get_current_user()
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'error': '评论不存在'}), 404

        existing = Like.query.filter_by(user_id=user.id, comment_id=comment_id).first()
        if existing:
            db.session.delete(existing)
            comment.like_count = max(0, (comment.like_count or 0) - 1)
            action = 'unliked'
        else:
            like = Like(user_id=user.id, comment_id=comment_id)
            db.session.add(like)
            comment.like_count = (comment.like_count or 0) + 1
            action = 'liked'

        db.session.commit()
        return jsonify({'message': 'ok', 'action': action, 'like_count': comment.like_count})
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': '操作失败'}), 500


@community_bp.route('/comments', methods=['GET'])
@optional_auth
def list_comments_general():
    """通用评论列表API，支持分页和排序"""
    try:
        post_id = request.args.get('post_id', type=int)
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)  # 限制最大20条
        
        if not post_id:
            return jsonify({'error': '缺少post_id参数'}), 400
            
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'error': '帖子不存在'}), 404
        
        # 按置顶状态优先，然后按点赞数降序，点赞数相同时按创建时间降序（最新的优先）
        query = Comment.query.filter_by(post_id=post_id).order_by(
            Comment.is_pinned.desc(),  # 置顶评论优先
            Comment.like_count.desc(),
            Comment.created_at.desc()
        )
        
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        comments = [c.to_dict(include_author=True) for c in pagination.items]
        
        # 标记当前用户是否点赞
        user = get_current_user()
        if user and pagination.items:
            comment_ids = [c.id for c in pagination.items]
            liked = Like.query.filter(Like.user_id == user.id, Like.comment_id.in_(comment_ids)).all()
            liked_ids = {l.comment_id for l in liked if l.comment_id}
            for c in comments:
                c['liked_by_me'] = c['id'] in liked_ids
        
        return jsonify({
            'items': comments,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages
        })
    except Exception as e:
        logger.error(f"获取评论列表失败: {str(e)}")
        return jsonify({'error': '获取评论失败'}), 500


@community_bp.route('/comments', methods=['POST'])
@require_auth
def create_comment_general():
    """通用创建评论API"""
    try:
        user = get_current_user()
        data = request.json or {}
        
        post_id = data.get('post_id')
        content = (data.get('content') or '').strip()
        
        if not post_id:
            return jsonify({'error': '缺少post_id参数'}), 400
        if not content:
            return jsonify({'error': '评论内容不能为空'}), 400
            
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'error': '帖子不存在'}), 404
        
        comment = Comment(
            post_id=post_id,
            author_id=user.id,
            content=content
        )
        
        db.session.add(comment)
        post.comment_count = (post.comment_count or 0) + 1
        db.session.commit()
        
        return jsonify({
            'message': '评论成功',
            'comment': comment.to_dict(include_author=True),
            'comment_count': post.comment_count
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建评论失败: {str(e)}")
        return jsonify({'error': '评论失败'}), 500


@community_bp.route('/comments/<int:comment_id>/pin', methods=['PATCH'])
@require_auth
def pin_comment(comment_id: int):
    """置顶/取消置顶评论（仅帖子作者可以操作）"""
    try:
        user = get_current_user()
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'error': '评论不存在'}), 404
        
        post = comment.post
        if not post:
            return jsonify({'error': '帖子不存在'}), 404
        
        # 只有帖子作者可以置顶评论
        if post.author_id != user.id:
            return jsonify({'error': '只有帖子作者可以置顶评论'}), 403
        
        # 切换置顶状态
        comment.is_pinned = not comment.is_pinned
        db.session.commit()
        
        return jsonify({
            'message': '置顶成功' if comment.is_pinned else '取消置顶成功',
            'is_pinned': comment.is_pinned
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"置顶评论失败: {str(e)}")
        return jsonify({'error': '操作失败'}), 500


# 删除评论
@community_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@require_auth
def delete_comment(comment_id):
    """删除评论（作者、帖子作者或超级管理员可删除）"""
    try:
        user = get_current_user()
        comment = Comment.query.get(comment_id)
        
        if not comment:
            return jsonify({'error': '评论不存在'}), 404
        
        # 检查权限：评论作者、帖子作者或超级管理员可以删除
        post = Post.query.get(comment.post_id)
        if not post:
            return jsonify({'error': '帖子不存在'}), 404
        
        if not user.is_superadmin() and comment.author_id != user.id and post.author_id != user.id:
            return jsonify({'error': '无权删除该评论'}), 403
        
        # 记录评论信息用于日志
        comment_content = comment.content[:50] + '...' if len(comment.content) > 50 else comment.content
        
        # 删除评论相关的所有文件
        deleted_files = delete_comment_related_files(comment)
        
        # 删除数据库记录（由于设置了cascade='all, delete-orphan'，回复会自动删除）
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({
            'message': f'评论删除成功',
            'deleted_files_count': len(deleted_files)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除评论失败: {str(e)}", exc_info=True)
        return jsonify({'error': '删除评论失败'}), 500


# 批量删除评论
@community_bp.route('/comments/batch_delete', methods=['POST'])
@require_auth
def batch_delete_comments():
    """批量删除评论（作者、帖子作者或超级管理员可删除）"""
    try:
        user = get_current_user()
        data = request.json or {}
        
        if not data or 'comment_ids' not in data:
            return jsonify({'error': '请提供要删除的评论ID列表'}), 400
        
        comment_ids = data['comment_ids']
        if not isinstance(comment_ids, list) or not comment_ids:
            return jsonify({'error': '评论ID列表不能为空'}), 400
        
        # 验证所有评论是否存在
        comments = Comment.query.filter(Comment.id.in_(comment_ids)).all()
        if len(comments) != len(comment_ids):
            found_ids = [comment.id for comment in comments]
            missing_ids = [cid for cid in comment_ids if cid not in found_ids]
            return jsonify({'error': f'以下评论不存在: {missing_ids}'}), 404
        
        # 检查权限：评论作者、帖子作者或超级管理员可以删除
        if not user.is_superadmin():
            unauthorized_comments = []
            for comment in comments:
                post = Post.query.get(comment.post_id)
                if post and comment.author_id != user.id and post.author_id != user.id:
                    unauthorized_comments.append(comment)
            
            if unauthorized_comments:
                unauthorized_ids = [comment.id for comment in unauthorized_comments]
                return jsonify({'error': f'无权删除以下评论: {unauthorized_ids}'}), 403
        
        deleted_comments = []
        total_deleted_files = 0
        
        # 逐个删除评论
        for comment in comments:
            try:
                # 删除相关文件
                deleted_files = delete_comment_related_files(comment)
                total_deleted_files += len(deleted_files)
                
                # 删除数据库记录
                db.session.delete(comment)
                
                deleted_comments.append({
                    'id': comment.id,
                    'deleted_files_count': len(deleted_files)
                })
                
            except Exception as e:
                logger.error(f"删除评论 {comment.id} 时发生错误: {str(e)}")
                # 继续删除其他评论，不中断整个过程
                continue
        
        # 提交所有删除操作
        db.session.commit()
        
        return jsonify({
            'message': f'成功删除 {len(deleted_comments)} 个评论',
            'deleted_comments': deleted_comments,
            'total_deleted_files': total_deleted_files
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"批量删除评论失败: {str(e)}", exc_info=True)
        return jsonify({'error': '批量删除评论失败'}), 500


@community_bp.route('/upload-image', methods=['POST'])
@require_auth
def upload_image():
    try:
        user = get_current_user()
        if 'image' not in request.files:
            return jsonify({'error': '请选择图片文件'}), 400
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': '请选择图片文件'}), 400

        # 允许的扩展名
        allowed_ext = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed_ext:
            return jsonify({'error': '不支持的图片格式'}), 400

        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'community')
        os.makedirs(upload_dir, exist_ok=True)

        filename = f"post_{user.id}_{uuid.uuid4().hex}{ext}"
        path = os.path.join(upload_dir, secure_filename(filename))
        file.save(path)

        url = f"/uploads/community/{filename}"
        return jsonify({'message': '上传成功', 'url': url})
    except Exception:
        current_app.logger.exception('上传图片失败')
        return jsonify({'error': '上传失败'}), 500


@community_bp.route('/reports', methods=['POST'])
@require_auth
def create_report():
    try:
        user = get_current_user()
        data = request.json or {}
        target_type = data.get('target_type')  # post | comment
        target_id = data.get('target_id')
        reason = (data.get('reason') or '').strip()

        if target_type not in ('post', 'comment'):
            return jsonify({'error': '无效的举报类型'}), 400
        if not target_id:
            return jsonify({'error': '缺少举报对象'}), 400
        if not reason:
            return jsonify({'error': '请填写举报原因'}), 400

        report = Report(reporter_id=user.id, target_type=target_type, target_id=target_id, reason=reason)
        db.session.add(report)
        db.session.commit()
        return jsonify({'message': '举报已提交', 'report': report.to_dict()}), 201
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': '提交失败'}), 500


@community_bp.route('/reports', methods=['GET'])
@require_admin
def list_reports():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return jsonify({'items': [r.to_dict() for r in reports], 'total': len(reports)})


@community_bp.route('/reports/<int:report_id>', methods=['PATCH'])
@require_admin
def update_report(report_id: int):
    try:
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': '举报不存在'}), 404
        data = request.json or {}
        status = data.get('status')
        if status not in ('pending', 'resolved', 'dismissed'):
            return jsonify({'error': '无效的状态'}), 400
        report.status = status
        db.session.commit()
        return jsonify({'message': '更新成功', 'report': report.to_dict()})
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': '更新失败'}), 500


# 清理孤立的帖子图片
@community_bp.route('/posts/cleanup_orphaned_images', methods=['POST'])
@require_admin
def cleanup_orphaned_post_images():
    """清理孤立的帖子图片文件（没有被数据库记录引用的图片）"""
    try:
        cleaned_files = []
        
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
            referenced_post_images = set()
            posts = Post.query.all()
            for post in posts:
                image_urls = post.get_image_urls()
                for image_url in image_urls:
                    if image_url:
                        filename = image_url.split('/')[-1]
                        referenced_post_images.add(filename)
            
            logger.info(f"数据库中引用的帖子图片: {len(referenced_post_images)} 个")
            
            # 检查目录中的所有图片文件
            for filename in os.listdir(posts_upload_dir):
                file_path = os.path.join(posts_upload_dir, filename)
                if os.path.isfile(file_path) and filename not in referenced_post_images:
                    # 检查文件是否是图片文件
                    if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        try:
                            os.remove(file_path)
                            cleaned_files.append(f"{os.path.basename(posts_upload_dir)}/{filename}")
                            logger.info(f"清理孤立帖子图片: {file_path}")
                        except Exception as e:
                            logger.warning(f"清理孤立帖子图片失败 {file_path}: {str(e)}")
            
            # 如果找到了目录并处理了，就跳出循环
            break
        
        return jsonify({
            'message': f'清理完成，共删除 {len(cleaned_files)} 个孤立图片文件',
            'cleaned_files': cleaned_files
        }), 200
        
    except Exception as e:
        logger.error(f"清理孤立帖子图片失败: {str(e)}", exc_info=True)
        return jsonify({'error': '清理孤立帖子图片失败'}), 500


