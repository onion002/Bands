from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_, desc
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

from models import db, User, Post, Comment, Tag, Like, Report
from auth_decorators import require_auth, require_admin, optional_auth, get_current_user, require_superadmin


community_bp = Blueprint('community', __name__)


def _serialize_post(post: Post):
    return post.to_dict(include_author=True)


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
    return jsonify({'post': _serialize_post(post)})


@community_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@require_auth
def delete_post(post_id: int):
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'error': '帖子不存在'}), 404
        user = get_current_user()
        # 普通用户可以删除自己发的帖子；管理员可以删除自己发的帖子；超级管理员可删除所有
        if user.is_superadmin() or post.author_id == user.id:
            db.session.delete(post)
        else:
            return jsonify({'error': '无权删除该帖子'}), 403
        db.session.commit()
        return jsonify({'message': '删除成功'})
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'error': '删除失败'}), 500


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


