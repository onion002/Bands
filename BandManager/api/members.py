import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
from models import db, Member, Band
from sqlalchemy.exc import SQLAlchemyError
import logging
from auth_decorators import require_auth, require_admin, optional_auth, get_current_user, apply_user_filter, set_owner_for_creation

members_bp = Blueprint('members', __name__, url_prefix='/api/members')

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """检查文件扩展名是否合法"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 获取所有成员（分页，可选band_id筛选）
@members_bp.route('/', methods=['GET'])
@require_admin
def get_all_members():
    try:
        current_user = get_current_user()
        # 可选乐队筛选
        band_id = request.args.get('band_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        page = max(1, page)
        per_page = max(1, min(per_page, 100))

        query = Member.query.filter_by(owner_id=current_user.id)
        if band_id:
            # 确保乐队也属于当前用户
            band = Band.query.filter_by(id=band_id, owner_id=current_user.id).first()
            if not band:
                return jsonify({'error': '乐队不存在或无权限访问'}), 404
            query = query.filter_by(band_id=band_id)
        pagination = query.order_by(Member.join_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
        members = [member.to_dict() for member in pagination.items]
        return jsonify({
            'items': members,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        })
    except Exception as e:
        logging.error(f"获取成员列表失败: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@members_bp.route('/public/<username>', methods=['GET'])
def get_public_members(username):
    """获取指定管理员的公开成员列表"""
    try:
        from models import User
        # 查找管理员用户
        admin_user = User.query.filter_by(username=username, user_type='admin').first()
        if not admin_user:
            return jsonify({'error': '管理员用户不存在'}), 404

        # 可选乐队筛选
        band_id = request.args.get('band_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        page = max(1, page)
        per_page = max(1, min(per_page, 100))

        query = Member.query.filter_by(owner_id=admin_user.id)
        if band_id:
            # 确保乐队也属于该管理员
            band = Band.query.filter_by(id=band_id, owner_id=admin_user.id).first()
            if not band:
                return jsonify({'error': '乐队不存在'}), 404
            query = query.filter_by(band_id=band_id)

        pagination = query.order_by(Member.join_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
        members = [member.to_dict() for member in pagination.items]

        return jsonify({
            'items': members,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'admin_info': {
                'username': admin_user.username,
                'display_name': admin_user.display_name
            }
        })
    except Exception as e:
        logging.exception("获取所有成员失败")
        # 返回空结构，附加错误信息
        return jsonify({
            'items': [],
            'total': 0,
            'pages': 1,
            'current_page': 1,
            'error': '服务器内部错误'
        }), 500

# 获取乐队成员列表
@members_bp.route('/band/<int:band_id>', methods=['GET'])
def get_band_members(band_id):
    try:
        # 检查乐队是否存在
        band = Band.query.get(band_id)
        if not band:
            return jsonify({'error': '乐队不存在'}), 404
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        page = max(1, page)
        per_page = max(1, min(per_page, 100))  # 限制每页最大100条
        
        # 查询成员
        pagination = Member.query.filter_by(band_id=band_id)\
                       .order_by(Member.join_date.desc())\
                       .paginate(page=page, per_page=per_page, error_out=False)
        
        members = [member.to_dict() for member in pagination.items]
        
        return jsonify({
            'items': members,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        })
    except Exception as e:
        logging.exception("获取成员列表失败")
        return jsonify({'error': '服务器内部错误'}), 500

# 创建新成员
@members_bp.route('/', methods=['POST'])
@require_admin
def create_member():
    try:
        current_user = get_current_user()
        data = request.json

        # 验证必要字段
        required_fields = ['name', 'join_date', 'band_id']
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': '缺少必要字段: name, join_date 或 band_id'}), 400
        
        # 验证乐队是否存在
        if not Band.query.get(data['band_id']):
            return jsonify({'error': '乐队不存在'}), 404
        
        # 转换日期格式
        try:
            join_date = datetime.strptime(data['join_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': '日期格式无效，请使用YYYY-MM-DD格式'}), 400
        
        # 创建成员
        name = data.get('name')
        band_id = data.get('band_id')
        if not name or not band_id:
            return jsonify({'error': '缺少必要字段: name 或 band_id'}), 400

        # 验证乐队是否属于当前用户
        band = Band.query.filter_by(id=band_id, owner_id=current_user.id).first()
        if not band:
            return jsonify({'error': '乐队不存在或无权限访问'}), 404

        new_member = Member(
            name=name,
            role=data.get('role'),
            join_date=join_date,
            band_id=band_id,
            avatar_url=data.get('avatar_url'),  # 支持头像URL
            owner_id=current_user.id
        )  # type: ignore
        
        db.session.add(new_member)
        db.session.commit()
        
        return jsonify(new_member.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.exception("创建成员失败")
        return jsonify({'error': '数据库操作失败'}), 500
    except Exception as e:
        logging.exception("未知错误")
        return jsonify({'error': '服务器内部错误'}), 500

# 获取成员详情
@members_bp.route('/<int:member_id>', methods=['GET'])
def get_member(member_id):
    try:
        member = Member.query.get(member_id)
        if not member:
            return jsonify({'error': '成员不存在'}), 404
            
        return jsonify(member.to_dict())
    except Exception as e:
        logging.exception("获取成员详情失败")
        return jsonify({'error': '服务器内部错误'}), 500

# 更新成员信息
@members_bp.route('/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    try:
        member = Member.query.get(member_id)
        if not member:
            return jsonify({'error': '成员不存在'}), 404
            
        data = request.json
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400
        
        # 更新可修改字段
        if 'name' in data:
            member.name = data['name']
        if 'role' in data:
            member.role = data['role']
        if 'join_date' in data:
            try:
                member.join_date = datetime.strptime(data['join_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': '日期格式无效'}), 400
        if 'band_id' in data:
            # 验证新乐队是否存在
            if not Band.query.get(data['band_id']):
                return jsonify({'error': '乐队不存在'}), 404
            member.band_id = data['band_id']
        if 'avatar_url' in data:
            avatar_val = data['avatar_url']
            if not avatar_val:  # 兼容 '', None, False
                # 删除逻辑
                member.avatar_url = None
            else:
                member.avatar_url = avatar_val
            
        db.session.commit()
        
        return jsonify(member.to_dict())
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.exception("更新成员失败")
        return jsonify({'error': '数据库操作失败'}), 500
    except Exception as e:
        logging.exception("未知错误")
        return jsonify({'error': '服务器内部错误'}), 500

# 删除成员
@members_bp.route('/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    try:
        member = Member.query.get(member_id)
        if not member:
            return jsonify({'error': '成员不存在'}), 404
        
        # 删除成员头像文件（如果存在）
        if member.avatar_url:
            try:
                avatar_path = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    'members',
                    member.avatar_url.split('/')[-1]
                )
                if os.path.exists(avatar_path):
                    os.remove(avatar_path)
            except Exception as e:
                logging.warning(f"删除成员头像失败: {str(e)}")
        
        db.session.delete(member)
        db.session.commit()
        
        return jsonify({'message': '成员删除成功'})
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.exception("删除成员失败")
        return jsonify({'error': '数据库操作失败'}), 500
    except Exception as e:
        logging.exception("未知错误")
        return jsonify({'error': '服务器内部错误'}), 500

# 上传成员头像
@members_bp.route('/<int:member_id>/avatar', methods=['POST'])
def upload_member_avatar(member_id):
    try:
        # 检查成员是否存在
        member = Member.query.get(member_id)
        if not member:
            return jsonify({'error': '成员不存在'}), 404

        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400

        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件类型，请上传图片文件'}), 400

        # 删除旧头像文件（如果存在）
        if member.avatar_url:
            try:
                old_file_path = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    'members',
                    member.avatar_url.split('/')[-1]
                )
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            except Exception as e:
                logging.warning(f"删除旧头像失败: {str(e)}")

        # 生成安全文件名
        safe_name = member.name.replace(' ', '_') if member.name else 'member'
        ext = file.filename.split('.')[-1] if file.filename and '.' in file.filename else 'jpg'
        filename = f"member_{safe_name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{ext}"

        # 确保上传目录存在
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'members')
        os.makedirs(upload_dir, exist_ok=True)

        # 保存文件
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # 更新数据库中的头像URL
        member.avatar_url = f"/uploads/members/{filename}"
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '头像上传成功',
            'avatar_url': member.avatar_url
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.exception("上传头像失败")
        return jsonify({'error': '数据库操作失败'}), 500
    except Exception as e:
        logging.exception("上传头像时发生未知错误")
        return jsonify({'error': '服务器内部错误'}), 500