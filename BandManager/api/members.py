from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, Member, Band
from sqlalchemy.exc import SQLAlchemyError
import logging

members_bp = Blueprint('members', __name__, url_prefix='/api/members')

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
def create_member():
    try:
        data = request.json
        
        # 验证必要字段
        required_fields = ['name', 'join_date', 'band_id']
        if not all(field in data for field in required_fields):
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
        new_member = Member(
            name=data['name'],
            role=data.get('role'),
            join_date=join_date,
            band_id=data['band_id']
        )
        
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