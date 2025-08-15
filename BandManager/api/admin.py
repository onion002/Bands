from flask import Blueprint, request, jsonify
from models import db, User, Post, Report, UserType
from auth_decorators import require_superadmin
from werkzeug.security import generate_password_hash
from sqlalchemy import or_

admin_bp = Blueprint('admin', __name__)


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
    for u in users:
        db.session.delete(u)
    db.session.commit()
    return jsonify({'message': '批量删除成功', 'count': len(users)})


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_superadmin
def delete_user(user_id: int):
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error': '用户不存在'}), 404
    db.session.delete(u)
    db.session.commit()
    return jsonify({'message': '删除成功'})


# 帖子强删（超级管理员）
@admin_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@require_superadmin
def force_delete_post(post_id: int):
    p = Post.query.get(post_id)
    if not p:
        return jsonify({'error': '帖子不存在'}), 404
    db.session.delete(p)
    db.session.commit()
    return jsonify({'message': '删除成功'})


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


