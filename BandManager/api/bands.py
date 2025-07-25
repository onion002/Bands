import os
import glob
import re
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from models import db, Band, Member
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

def delete_band_related_images(band):
    """删除乐队相关的所有图片文件"""
    deleted_files = []

    try:
        # 1. 删除乐队的所有历史图片
        bands_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'bands')
        if os.path.exists(bands_upload_dir):
            # 首先删除当前数据库中记录的图片
            if band.banner_image_url:
                try:
                    current_filename = band.banner_image_url.split('/')[-1]
                    current_file_path = os.path.join(bands_upload_dir, current_filename)
                    if os.path.exists(current_file_path):
                        os.remove(current_file_path)
                        deleted_files.append(current_file_path)
                        logging.info(f"删除当前乐队图片: {current_file_path}")
                except Exception as e:
                    logging.warning(f"删除当前乐队图片失败 {band.banner_image_url}: {str(e)}")

            # 生成乐队名称的安全版本，用于匹配文件名
            safe_band_name = band.name.replace(' ', '_') if band.name else 'band'

            # 删除所有明确属于该乐队的历史图片
            # 格式: band_{safe_name}_{timestamp}.{ext}
            patterns = [
                f"band_{safe_band_name}_*.jpg",
                f"band_{safe_band_name}_*.jpeg",
                f"band_{safe_band_name}_*.png",
                f"band_{safe_band_name}_*.gif",
                f"band_{safe_band_name}_*.webp"
            ]

            for pattern in patterns:
                matching_files = glob.glob(os.path.join(bands_upload_dir, pattern))
                for file_path in matching_files:
                    filename = os.path.basename(file_path)

                    # 跳过已经删除的当前图片
                    if band.banner_image_url and filename == band.banner_image_url.split('/')[-1]:
                        continue

                    try:
                        os.remove(file_path)
                        deleted_files.append(file_path)
                        logging.info(f"删除乐队历史图片: {file_path}")
                    except Exception as e:
                        logging.warning(f"删除乐队历史图片失败 {file_path}: {str(e)}")

            # 对于upload_image端点上传的图片（格式: {timestamp}_{original_filename}）
            # 我们需要检查所有其他乐队是否还在使用这些图片
            # 如果没有其他乐队使用，则可以安全删除
            all_files = [f for f in os.listdir(bands_upload_dir)
                        if os.path.isfile(os.path.join(bands_upload_dir, f))
                        and any(f.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])]

            # 获取所有其他乐队正在使用的图片
            other_bands = Band.query.filter(Band.id != band.id).all()
            used_images = set()
            for other_band in other_bands:
                if other_band.banner_image_url:
                    used_images.add(other_band.banner_image_url.split('/')[-1])

            # 检查每个文件是否可以安全删除
            for filename in all_files:
                file_path = os.path.join(bands_upload_dir, filename)

                # 跳过已经删除的当前图片
                if band.banner_image_url and filename == band.banner_image_url.split('/')[-1]:
                    continue

                # 跳过明确属于该乐队的图片（已经在上面处理过）
                if filename.startswith(f"band_{safe_band_name}_"):
                    continue

                # 跳过其他乐队正在使用的图片
                if filename in used_images:
                    continue

                # 对于格式2的文件，如果没有其他乐队使用，可能是该乐队的历史图片
                # 检查文件名格式是否符合 {timestamp}_{filename} 模式
                parts = filename.split('_', 1)
                if len(parts) == 2 and parts[0].isdigit() and len(parts[0]) >= 8:
                    # 看起来像是时间戳格式的文件，且没有被其他乐队使用
                    # 可能是该乐队的历史图片，删除它
                    try:
                        os.remove(file_path)
                        deleted_files.append(file_path)
                        logging.info(f"删除可能的乐队历史图片: {file_path}")
                    except Exception as e:
                        logging.warning(f"删除可能的乐队历史图片失败 {file_path}: {str(e)}")
                else:
                    # 不符合已知格式，跳过
                    continue

        # 2. 删除该乐队所有成员的头像
        members = Member.query.filter_by(band_id=band.id).all()
        members_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'members')

        for member in members:
            if member.avatar_url:
                try:
                    # 删除当前头像
                    avatar_filename = member.avatar_url.split('/')[-1]
                    avatar_path = os.path.join(members_upload_dir, avatar_filename)
                    if os.path.exists(avatar_path):
                        os.remove(avatar_path)
                        deleted_files.append(avatar_path)
                        logging.info(f"删除成员头像: {avatar_path}")
                except Exception as e:
                    logging.warning(f"删除成员头像失败 {member.avatar_url}: {str(e)}")

            # 删除该成员的所有历史头像
            if os.path.exists(members_upload_dir):
                safe_member_name = member.name.replace(' ', '_') if member.name else 'member'
                member_patterns = [
                    f"member_{safe_member_name}_*.jpg",
                    f"member_{safe_member_name}_*.jpeg",
                    f"member_{safe_member_name}_*.png",
                    f"member_{safe_member_name}_*.gif",
                    f"member_{safe_member_name}_*.webp"
                ]

                for pattern in member_patterns:
                    matching_files = glob.glob(os.path.join(members_upload_dir, pattern))
                    for file_path in matching_files:
                        try:
                            os.remove(file_path)
                            deleted_files.append(file_path)
                            logging.info(f"删除成员历史头像: {file_path}")
                        except Exception as e:
                            logging.warning(f"删除成员历史头像失败 {file_path}: {str(e)}")

        logging.info(f"乐队 {band.name} 相关图片删除完成，共删除 {len(deleted_files)} 个文件")
        return deleted_files

    except Exception as e:
        logging.error(f"删除乐队相关图片时发生错误: {str(e)}")
        return deleted_files

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
    """删除乐队（物理删除所有相关图片和成员图片）"""
    try:
        band = Band.query.get(band_id)
        if not band:
            return jsonify({'error': '乐队不存在'}), 404

        # 记录乐队信息用于日志
        band_name = band.name

        # 删除乐队相关的所有图片文件（包括历史图片和成员头像）
        deleted_files = delete_band_related_images(band)

        # 删除数据库记录（由于设置了cascade='all, delete-orphan'，成员记录会自动删除）
        db.session.delete(band)
        db.session.commit()

        return jsonify({
            'message': f'乐队 "{band_name}" 删除成功',
            'deleted_files_count': len(deleted_files)
        }), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"删除乐队失败: {str(e)}", exc_info=True)
        return jsonify({'error': '删除乐队失败'}), 500

@bands_bp.route('/batch_delete', methods=['POST'])
def batch_delete_bands():
    """批量删除乐队（物理删除所有相关图片和成员图片）"""
    try:
        data = request.json
        if not data or 'band_ids' not in data:
            return jsonify({'error': '请提供要删除的乐队ID列表'}), 400

        band_ids = data['band_ids']
        if not isinstance(band_ids, list) or not band_ids:
            return jsonify({'error': '乐队ID列表不能为空'}), 400

        # 验证所有乐队是否存在
        bands = Band.query.filter(Band.id.in_(band_ids)).all()
        if len(bands) != len(band_ids):
            found_ids = [band.id for band in bands]
            missing_ids = [bid for bid in band_ids if bid not in found_ids]
            return jsonify({'error': f'以下乐队不存在: {missing_ids}'}), 404

        deleted_bands = []
        total_deleted_files = 0

        # 逐个删除乐队
        for band in bands:
            try:
                band_name = band.name

                # 删除相关图片文件
                deleted_files = delete_band_related_images(band)
                total_deleted_files += len(deleted_files)

                # 删除数据库记录
                db.session.delete(band)

                deleted_bands.append({
                    'id': band.id,
                    'name': band_name,
                    'deleted_files_count': len(deleted_files)
                })

            except Exception as e:
                logging.error(f"删除乐队 {band.name} 时发生错误: {str(e)}")
                # 继续删除其他乐队，不中断整个过程
                continue

        # 提交所有删除操作
        db.session.commit()

        return jsonify({
            'message': f'成功删除 {len(deleted_bands)} 个乐队',
            'deleted_bands': deleted_bands,
            'total_deleted_files': total_deleted_files
        }), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"批量删除乐队失败: {str(e)}", exc_info=True)
        return jsonify({'error': '批量删除乐队失败'}), 500

@bands_bp.route('/cleanup_orphaned_images', methods=['POST'])
def cleanup_orphaned_images():
    """清理孤立的图片文件（没有被数据库记录引用的图片）"""
    try:
        cleaned_files = []

        # 清理乐队图片目录
        bands_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'bands')
        if os.path.exists(bands_upload_dir):
            # 获取所有数据库中引用的乐队图片
            referenced_band_images = set()
            bands = Band.query.all()
            for band in bands:
                if band.banner_image_url:
                    filename = band.banner_image_url.split('/')[-1]
                    referenced_band_images.add(filename)

            # 检查目录中的所有图片文件
            for filename in os.listdir(bands_upload_dir):
                file_path = os.path.join(bands_upload_dir, filename)
                if os.path.isfile(file_path) and filename not in referenced_band_images:
                    # 检查文件是否是图片文件
                    if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        try:
                            os.remove(file_path)
                            cleaned_files.append(f"bands/{filename}")
                            logging.info(f"清理孤立乐队图片: {file_path}")
                        except Exception as e:
                            logging.warning(f"清理孤立乐队图片失败 {file_path}: {str(e)}")

        # 清理成员头像目录
        members_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'members')
        if os.path.exists(members_upload_dir):
            # 获取所有数据库中引用的成员头像
            referenced_member_images = set()
            members = Member.query.all()
            for member in members:
                if member.avatar_url:
                    filename = member.avatar_url.split('/')[-1]
                    referenced_member_images.add(filename)

            # 检查目录中的所有图片文件
            for filename in os.listdir(members_upload_dir):
                file_path = os.path.join(members_upload_dir, filename)
                if os.path.isfile(file_path) and filename not in referenced_member_images:
                    # 检查文件是否是图片文件
                    if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                        try:
                            os.remove(file_path)
                            cleaned_files.append(f"members/{filename}")
                            logging.info(f"清理孤立成员头像: {file_path}")
                        except Exception as e:
                            logging.warning(f"清理孤立成员头像失败 {file_path}: {str(e)}")

        return jsonify({
            'message': f'清理完成，共删除 {len(cleaned_files)} 个孤立图片文件',
            'cleaned_files': cleaned_files
        }), 200

    except Exception as e:
        logging.error(f"清理孤立图片失败: {str(e)}", exc_info=True)
        return jsonify({'error': '清理孤立图片失败'}), 500

@bands_bp.route('/<int:band_id>/cleanup_all_images', methods=['POST'])
def cleanup_all_band_images(band_id):
    """强制清理指定乐队的所有可能相关图片（包括upload_image上传的图片）"""
    try:
        band = Band.query.get(band_id)
        if not band:
            return jsonify({'error': '乐队不存在'}), 404

        deleted_files = []
        bands_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'bands')

        if not os.path.exists(bands_upload_dir):
            return jsonify({
                'message': f'乐队 "{band.name}" 的图片清理完成',
                'deleted_files': [],
                'deleted_files_count': 0
            }), 200

        # 获取所有其他乐队正在使用的图片
        other_bands = Band.query.filter(Band.id != band_id).all()
        protected_images = set()
        for other_band in other_bands:
            if other_band.banner_image_url:
                protected_images.add(other_band.banner_image_url.split('/')[-1])

        # 生成该乐队的安全名称
        safe_band_name = band.name.replace(' ', '_') if band.name else 'band'

        # 获取所有图片文件
        all_files = [f for f in os.listdir(bands_upload_dir)
                    if os.path.isfile(os.path.join(bands_upload_dir, f))
                    and any(f.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])]

        logging.info(f"开始强制清理乐队 {band.name} 的图片，共找到 {len(all_files)} 个图片文件")
        logging.info(f"受保护的图片: {protected_images}")

        for filename in all_files:
            file_path = os.path.join(bands_upload_dir, filename)

            # 保护其他乐队正在使用的图片
            if filename in protected_images:
                logging.info(f"跳过受保护的图片: {filename}")
                continue

            should_delete = False
            delete_reason = ""

            # 1. 明确属于该乐队的图片（格式1）
            if filename.startswith(f"band_{safe_band_name}_"):
                should_delete = True
                delete_reason = "格式1乐队图片"

            # 2. 当前乐队正在使用的图片
            elif band.banner_image_url and filename == band.banner_image_url.split('/')[-1]:
                should_delete = True
                delete_reason = "当前使用的图片"

            # 3. 对于格式2的文件，采用激进策略：删除所有未被保护的格式2文件
            else:
                # 检查文件名格式是否符合 {timestamp}_{filename} 模式
                parts = filename.split('_', 1)
                if len(parts) == 2 and parts[0].isdigit() and len(parts[0]) >= 8:
                    # 看起来像是时间戳格式，可能是通过upload_image上传的
                    should_delete = True
                    delete_reason = "格式2历史图片"

            if should_delete:
                try:
                    os.remove(file_path)
                    deleted_files.append(filename)
                    logging.info(f"强制删除乐队图片: {file_path} (原因: {delete_reason})")
                except Exception as e:
                    logging.warning(f"强制删除乐队图片失败 {file_path}: {str(e)}")
            else:
                logging.info(f"跳过文件: {filename} (不符合删除条件)")

        return jsonify({
            'message': f'乐队 "{band.name}" 的图片强制清理完成',
            'deleted_files': deleted_files,
            'deleted_files_count': len(deleted_files)
        }), 200

    except Exception as e:
        logging.error(f"强制清理乐队图片失败: {str(e)}", exc_info=True)
        return jsonify({'error': '强制清理乐队图片失败'}), 500

@bands_bp.route('/force_cleanup_all_unused_images', methods=['POST'])
def force_cleanup_all_unused_images():
    """强制清理所有未被使用的图片文件（危险操作，谨慎使用）"""
    try:
        deleted_files = []
        bands_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'bands')

        if not os.path.exists(bands_upload_dir):
            return jsonify({
                'message': '上传目录不存在',
                'deleted_files': [],
                'deleted_files_count': 0
            }), 200

        # 获取所有乐队正在使用的图片
        all_bands = Band.query.all()
        used_images = set()
        for band in all_bands:
            if band.banner_image_url:
                used_images.add(band.banner_image_url.split('/')[-1])

        # 获取所有图片文件
        all_files = [f for f in os.listdir(bands_upload_dir)
                    if os.path.isfile(os.path.join(bands_upload_dir, f))
                    and any(f.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])]

        logging.info(f"开始强制清理所有未使用的图片，共找到 {len(all_files)} 个图片文件")
        logging.info(f"正在使用的图片: {used_images}")

        for filename in all_files:
            file_path = os.path.join(bands_upload_dir, filename)

            # 如果文件没有被任何乐队使用，删除它
            if filename not in used_images:
                try:
                    os.remove(file_path)
                    deleted_files.append(filename)
                    logging.info(f"强制删除未使用的图片: {file_path}")
                except Exception as e:
                    logging.warning(f"强制删除未使用的图片失败 {file_path}: {str(e)}")
            else:
                logging.info(f"保留正在使用的图片: {filename}")

        return jsonify({
            'message': f'强制清理完成，删除了 {len(deleted_files)} 个未使用的图片文件',
            'deleted_files': deleted_files,
            'deleted_files_count': len(deleted_files),
            'used_images': list(used_images)
        }), 200

    except Exception as e:
        logging.error(f"强制清理所有未使用图片失败: {str(e)}", exc_info=True)
        return jsonify({'error': '强制清理所有未使用图片失败'}), 500

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