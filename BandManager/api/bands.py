import os
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from models import db, Band
from sqlalchemy import text
from datetime import datetime
import logging
from sqlalchemy.exc import IntegrityError

# 创建蓝图
bands_bp = Blueprint('bands', __name__, url_prefix='/api/bands')

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """检查文件扩展名是否合法"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, upload_folder, file_prefix):
    """保存上传的文件并返回相对路径"""
    if file and allowed_file(file.filename):
        # 生成安全文件名
        filename = f"{file_prefix}_{secure_filename(file.filename)}"
        file_path = os.path.join(upload_folder, filename)
        
        # 确保目标目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 保存文件
        file.save(file_path)
        return f"/{os.path.basename(upload_folder)}/{filename}"
    
    return None

@bands_bp.route('/', methods=['GET'])
def get_bands():
    try:
        bands = Band.query.all()
        results = [{
            'id': band.id,
            'name': band.name,
            'year': band.year,
            'genre': band.genre,
            'member_count': band.member_count,
            'bio': band.bio,
            'banner_image_url': band.banner_image_url if hasattr(band, 'banner_image_url') else None,
            'primary_color': band.primary_color if hasattr(band, 'primary_color') else None
        } for band in bands]
        return jsonify({'items': results, 'total': len(results)})
    except Exception as e:
        logging.error(f"获取乐队列表失败: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@bands_bp.route('/', methods=['POST'])
def create_band():
    """创建新乐队"""
    try:
        # 检查是否为表单数据（可能包含文件）
        if 'file' in request.files:
            # 表单数据模式
            file = request.files['file']
            form_data = request.form
            name = form_data.get('name')
            if not name:
                return jsonify({'error': '乐队名称不能为空'}), 400
            
            # 处理上传的图片
            file_path = None
            if file and allowed_file(file.filename):
                # 生成安全文件名
                if name is not None:
                    safe_name = name.replace(' ', '_')
                else:
                    safe_name = 'band'
                ext = file.filename.split('.')[-1] if file and file.filename and '.' in file.filename else 'jpg'
                filename = f"band_{safe_name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{ext}"
                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'bands')
                os.makedirs(upload_folder, exist_ok=True)
                file_path_full = os.path.join(upload_folder, filename)
                file.save(file_path_full)
                file_path = f"/uploads/bands/{filename}"
            
            # 创建新乐队对象
            year_val = form_data.get('year')
            member_count_val = form_data.get('member_count')

            # 安全地转换年份
            year_int = None
            if year_val is not None:
                try:
                    if isinstance(year_val, (int, float)):
                        year_int = int(year_val)
                    elif isinstance(year_val, str) and year_val.strip():
                        year_int = int(year_val.strip())
                except (ValueError, TypeError):
                    year_int = None

            # 安全地转换成员数量
            member_count_int = 0
            if member_count_val is not None:
                try:
                    if isinstance(member_count_val, (int, float)):
                        member_count_int = int(member_count_val)
                    elif isinstance(member_count_val, str) and member_count_val.strip():
                        member_count_int = int(member_count_val.strip())
                except (ValueError, TypeError):
                    member_count_int = 0

            new_band = Band(
                name=name,
                year=year_int,
                genre=form_data.get('genre'),
                member_count=member_count_int,
                bio=form_data.get('bio', ''),
                banner_image_url=file_path
            )
            
            db.session.add(new_band)
            db.session.commit()
            
            return jsonify({
                'id': new_band.id,
                'name': new_band.name,
                'year': new_band.year,
                'genre': new_band.genre,
                'member_count': new_band.member_count,
                'banner_image_url': new_band.banner_image_url
            }), 201
        else:
            # JSON 数据模式
            data = request.json
            
            # 验证必要字段
            if not data or not data.get('name'):
                return jsonify({'error': '乐队名称不能为空'}), 400
                
            # 处理 banner_image_url 路径（如果是 /uploads/xxx，自动修正为 /uploads/bands/xxx）
            banner_image_url = data.get('banner_image_url')
            if banner_image_url and banner_image_url.startswith('/uploads/') and not banner_image_url.startswith('/uploads/bands/'):
                banner_image_url = banner_image_url.replace('/uploads/', '/uploads/bands/')
            
            # 创建新乐队对象
            year_val = data.get('year') if data else None
            member_count_val = data.get('member_count') if data else None

            # 安全地转换年份
            year_int = None
            if year_val is not None:
                try:
                    if isinstance(year_val, (int, float)):
                        year_int = int(year_val)
                    elif isinstance(year_val, str) and year_val.strip():
                        year_int = int(year_val.strip())
                except (ValueError, TypeError):
                    year_int = None

            # 安全地转换成员数量
            member_count_int = 0
            if member_count_val is not None:
                try:
                    if isinstance(member_count_val, (int, float)):
                        member_count_int = int(member_count_val)
                    elif isinstance(member_count_val, str) and member_count_val.strip():
                        member_count_int = int(member_count_val.strip())
                except (ValueError, TypeError):
                    member_count_int = 0

            new_band = Band(
                name=data['name'],
                year=year_int,
                genre=data.get('genre'),
                member_count=member_count_int,
                bio=data.get('bio', ''),
                banner_image_url=banner_image_url
            )
            
            # 保存到数据库
            db.session.add(new_band)
            db.session.commit()
            
            return jsonify({
                'id': new_band.id,
                'name': new_band.name,
                'year': new_band.year,
                'genre': new_band.genre,
                'member_count': new_band.member_count,
                'banner_image_url': new_band.banner_image_url
            }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': '乐队名称已存在'}), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f"创建乐队失败: {str(e)}", exc_info=True)
        return jsonify({'error': '创建乐队失败'}), 500

@bands_bp.route('/<int:band_id>', methods=['GET'])
def get_band(band_id):
    """获取单个乐队详情"""
    try:
        band = Band.query.get(band_id)
        if not band:
            return jsonify({'error': '乐队不存在'}), 404
            
        # 返回完整信息
        return jsonify({
            'id': band.id,
            'name': band.name,
            'year': band.year,
            'genre': band.genre,
            'member_count': band.member_count,
            'bio': band.bio,
            'banner_image_url': band.banner_image_url
        })
    except Exception as e:
        logging.error(f"获取乐队详情失败: {str(e)}", exc_info=True)
        return jsonify({'error': '服务器内部错误'}), 500

@bands_bp.route('/<int:band_id>', methods=['PUT'])
def update_band(band_id):
    """更新乐队信息"""
    try:
        band = Band.query.get(band_id)
        if not band:
            return jsonify({'error': '乐队不存在'}), 404
            
        # 检查是否为表单数据（可能包含文件）
        if 'file' in request.files:
            # 表单数据模式
            file = request.files['file']
            form_data = request.form
            
            # 处理普通字段
            if 'name' in form_data and form_data.get('name'):
                band.name = form_data['name']
            year_val = form_data.get('year')
            if 'year' in form_data and year_val is not None and str(year_val).strip() != '':
                band.year = int(year_val)
            if 'genre' in form_data:
                band.genre = form_data['genre']
            member_count_val = form_data.get('member_count')
            if 'member_count' in form_data and member_count_val is not None and str(member_count_val).strip() != '':
                band.member_count = int(member_count_val)
            if 'bio' in form_data:
                band.bio = form_data['bio']
            
            # 处理文件上传
            if file and allowed_file(file.filename):
                # 如果已有图片，先删除旧文件
                if band.banner_image_url:
                    try:
                        old_file = os.path.join(current_app.config['UPLOAD_FOLDER'], 'bands', band.banner_image_url.split('/')[-1])
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    except Exception as e:
                        logging.warning(f"删除旧图片失败: {str(e)}")
                
                # 保存新文件
                safe_name = band.name.replace(' ', '_') if band.name else 'band'
                ext = file.filename.split('.')[-1] if file and file.filename and '.' in file.filename else 'jpg'
                filename = f"band_{safe_name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{ext}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'bands', filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                file.save(file_path)
                band.banner_image_url = f"/uploads/bands/{filename}"
            
            db.session.commit()
            return jsonify({
                'id': band.id,
                'name': band.name,
                'year': band.year,
                'genre': band.genre,
                'member_count': band.member_count,
                'banner_image_url': band.banner_image_url
            })
        else:
            # JSON 数据模式
            data = request.json
            
            # 更新可修改的字段
            if not data or not data.get('name'):
                return jsonify({'error': '无数据或乐队名称不能为空'}), 400
            year_val = data.get('year') if data else None
            member_count_val = data.get('member_count') if data else None
            if data and 'name' in data and data['name']:
                band.name = data['name']
            if data and 'year' in data and year_val is not None and str(year_val).strip() != '':
                band.year = int(year_val)
            if data and 'genre' in data:
                band.genre = data['genre']
            if data and 'member_count' in data and member_count_val is not None and str(member_count_val).strip() != '':
                band.member_count = int(member_count_val)
            if data and 'bio' in data:
                band.bio = data['bio']
            if data and 'banner_image_url' in data:
                band.banner_image_url = data['banner_image_url']
            
            db.session.commit()
            return jsonify({
                'id': band.id,
                'name': band.name,
                'year': band.year,
                'genre': band.genre,
                'member_count': band.member_count,
                'banner_image_url': band.banner_image_url
            })
    except Exception as e:
        db.session.rollback()
        print("更新乐队异常：", e)  # 这行会把异常信息打印到控制台
        logging.error(f"更新乐队失败: {str(e)}", exc_info=True)
        return jsonify({'error': f'更新乐队失败: {str(e)}'}), 500

@bands_bp.route('/<int:band_id>', methods=['DELETE'])
def delete_band(band_id):
    """删除乐队（物理删除图片）"""
    try:
        band = Band.query.get(band_id)
        if not band:
            return jsonify({'error': '乐队不存在'}), 404
        
        # 删除乐队相关图片
        if band.banner_image_url:
            try:
                file_path = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    'bands',
                    band.banner_image_url.split('/')[-1]
                )
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logging.warning(f"删除乐队图片失败: {str(e)}")
        
        db.session.delete(band)
        db.session.commit()
        
        return jsonify({'message': '乐队删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"删除乐队失败: {str(e)}", exc_info=True)
        return jsonify({'error': '删除乐队失败'}), 500

@bands_bp.route('/upload_image', methods=['POST'])
def upload_band_image():
    """上传乐队图片，统一存储到 uploads/bands/ 目录下"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        # 检查文件类型
        allowed_exts = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件类型，请上传图片文件'}), 400
        # 生成唯一文件名
        ext = file.filename.rsplit('.', 1)[1].lower()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_" + secure_filename(file.filename)
        # 确保上传目录存在
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'bands')
        os.makedirs(upload_dir, exist_ok=True)
        # 保存文件
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        # 返回图片URL
        url = f"/uploads/bands/{filename}"
        return jsonify({
            'success': True,
            'message': '图片上传成功',
            'url': url
        }), 201
    except Exception as e:
        return jsonify({'error': f'图片上传失败: {str(e)}'}), 500