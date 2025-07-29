from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import logging
import os
import glob
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.utils import secure_filename
from models import db, Event, Band

# 创建蓝图
events_bp = Blueprint('events', __name__)

def delete_event_related_images(event):
    """
    删除演出活动相关的所有图片文件
    包括当前海报和历史海报
    """
    deleted_files = []

    try:
        # 1. 删除当前海报图片
        events_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'events')
        if os.path.exists(events_upload_dir):
            # 删除当前数据库中记录的海报
            if event.poster_image_url:
                try:
                    current_filename = event.poster_image_url.split('/')[-1]
                    current_file_path = os.path.join(events_upload_dir, current_filename)
                    if os.path.exists(current_file_path):
                        os.remove(current_file_path)
                        deleted_files.append(current_file_path)
                        logging.info(f"删除当前演出活动海报: {current_file_path}")
                except Exception as e:
                    logging.warning(f"删除当前演出活动海报失败 {event.poster_image_url}: {str(e)}")

            # 2. 删除该演出活动的所有历史海报
            # 生成安全的活动标题用于文件名匹配
            safe_event_title = event.title.replace(' ', '_').replace('/', '_').replace('\\', '_') if event.title else 'event'

            # 查找所有可能的历史海报文件
            # 格式1: event_{title}_{timestamp}.{ext}
            # 格式2: {timestamp}_{original_filename}.{ext}
            patterns = [
                f"event_{safe_event_title}_*.jpg",
                f"event_{safe_event_title}_*.jpeg",
                f"event_{safe_event_title}_*.png",
                f"event_{safe_event_title}_*.gif",
                f"event_{safe_event_title}_*.webp"
            ]

            # 获取所有其他演出活动正在使用的图片文件名，避免误删
            other_events = Event.query.filter(Event.id != event.id, Event.is_deleted == False).all()
            used_images = set()
            for other_event in other_events:
                if other_event.poster_image_url:
                    used_images.add(other_event.poster_image_url.split('/')[-1])

            for pattern in patterns:
                matching_files = glob.glob(os.path.join(events_upload_dir, pattern))
                for file_path in matching_files:
                    filename = os.path.basename(file_path)

                    # 跳过已经删除的当前海报
                    if event.poster_image_url and filename == event.poster_image_url.split('/')[-1]:
                        continue

                    # 跳过其他演出活动正在使用的图片
                    if filename in used_images:
                        continue

                    try:
                        os.remove(file_path)
                        deleted_files.append(file_path)
                        logging.info(f"删除演出活动历史海报: {file_path}")
                    except Exception as e:
                        logging.warning(f"删除演出活动历史海报失败 {file_path}: {str(e)}")

            # 3. 对于upload_poster端点上传的图片（格式: {timestamp}_{original_filename}）
            # 检查所有其他演出活动是否还在使用这些图片
            all_files = [f for f in os.listdir(events_upload_dir)
                        if os.path.isfile(os.path.join(events_upload_dir, f))
                        and any(f.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])]

            # 检查每个文件是否可以安全删除
            for filename in all_files:
                file_path = os.path.join(events_upload_dir, filename)

                # 跳过已经删除的当前海报
                if event.poster_image_url and filename == event.poster_image_url.split('/')[-1]:
                    continue

                # 跳过明确属于该演出活动的图片（已经在上面处理过）
                if filename.startswith(f"event_{safe_event_title}_"):
                    continue

                # 跳过其他演出活动正在使用的图片
                if filename in used_images:
                    continue

                # 对于格式2的文件，如果没有其他演出活动使用，可能是该演出活动的历史海报
                # 检查文件名格式是否符合 {timestamp}_{filename} 模式
                parts = filename.split('_', 1)
                if len(parts) == 2 and parts[0].isdigit() and len(parts[0]) >= 8:
                    # 看起来像是时间戳格式的文件，且没有被其他演出活动使用
                    # 可能是该演出活动的历史海报，删除它
                    try:
                        os.remove(file_path)
                        deleted_files.append(file_path)
                        logging.info(f"删除可能的演出活动历史海报: {file_path}")
                    except Exception as e:
                        logging.warning(f"删除可能的演出活动历史海报失败 {file_path}: {str(e)}")

        logging.info(f"演出活动 {event.title} 相关图片删除完成，共删除 {len(deleted_files)} 个文件")
        return deleted_files

    except Exception as e:
        logging.error(f"删除演出活动相关图片时发生错误: {str(e)}")
        return deleted_files

# 获取所有演出活动（分页）
@events_bp.route('/', methods=['GET'])
def get_all_events():
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        band_id = request.args.get('band_id', type=int)
        status = request.args.get('status', type=str)
        
        page = max(1, page)
        per_page = max(1, min(per_page, 100))
        
        # 构建查询
        query = Event.query.filter_by(is_deleted=False)
        
        # 按乐队筛选
        if band_id:
            query = query.filter_by(band_id=band_id)
        
        # 按状态筛选
        if status:
            query = query.filter_by(status=status)
        
        # 分页查询
        pagination = query.order_by(Event.event_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        events = [event.to_dict() for event in pagination.items]
        
        return jsonify({
            'items': events,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        })
    except Exception as e:
        logging.exception("获取演出活动列表失败")
        return jsonify({'error': '服务器内部错误'}), 500

# 获取指定乐队的演出活动
@events_bp.route('/band/<int:band_id>', methods=['GET'])
def get_band_events(band_id):
    try:
        # 检查乐队是否存在
        band = Band.query.get(band_id)
        if not band:
            return jsonify({'error': '乐队不存在'}), 404
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        page = max(1, page)
        per_page = max(1, min(per_page, 100))
        
        # 查询演出活动
        pagination = Event.query.filter_by(band_id=band_id, is_deleted=False)\
                       .order_by(Event.event_date.desc())\
                       .paginate(page=page, per_page=per_page, error_out=False)
        
        events = [event.to_dict() for event in pagination.items]
        
        return jsonify({
            'items': events,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        })
    except Exception as e:
        logging.exception("获取乐队演出活动失败")
        return jsonify({'error': '服务器内部错误'}), 500

# 创建新演出活动
@events_bp.route('/', methods=['POST'])
def create_event():
    try:
        data = request.json
        
        print(f"接收到的创建活动数据: {data}")
        
        # 验证必要字段
        required_fields = ['title', 'event_date', 'band_id']
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': '缺少必要字段: title, event_date 或 band_id'}), 400
        
        # 验证乐队是否存在
        if not Band.query.get(data['band_id']):
            return jsonify({'error': '乐队不存在'}), 404
        
        # 转换日期格式
        try:
            event_date = datetime.fromisoformat(data['event_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': '日期格式无效，请使用ISO格式'}), 400
        
        # 创建演出活动
        new_event = Event(
            title=data.get('title'),
            description=data.get('description'),
            event_date=event_date,
            venue=data.get('venue'),
            address=data.get('address'),
            ticket_price=data.get('ticket_price'),
            capacity=data.get('capacity'),
            status=data.get('status', 'upcoming'),
            band_id=data.get('band_id'),
            poster_image_url=data.get('poster_image_url')  # 确保这里正确获取
        )
        
        print(f"创建的活动对象 - 海报URL: {new_event.poster_image_url}")
        
        db.session.add(new_event)
        db.session.commit()
        
        print(f"活动创建成功，ID: {new_event.id}")
        
        return jsonify(new_event.to_dict()), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.exception("创建演出活动失败")
        return jsonify({'error': '数据库操作失败'}), 500
    except Exception as e:
        logging.exception("未知错误")
        return jsonify({'error': '服务器内部错误'}), 500

# 获取单个演出活动详情
@events_bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    try:
        event = Event.query.filter_by(id=event_id, is_deleted=False).first()
        if not event:
            return jsonify({'error': '演出活动不存在'}), 404
        
        return jsonify(event.to_dict())
    except Exception as e:
        logging.exception("获取演出活动详情失败")
        return jsonify({'error': '服务器内部错误'}), 500

# 更新演出活动
@events_bp.route('/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    try:
        event = Event.query.filter_by(id=event_id, is_deleted=False).first()
        if not event:
            return jsonify({'error': '演出活动不存在'}), 404
        
        data = request.json
        if not data:
            return jsonify({'error': '请提供要更新的数据'}), 400
        
        # 更新字段
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'event_date' in data:
            try:
                event.event_date = datetime.fromisoformat(data['event_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': '日期格式无效'}), 400
        if 'venue' in data:
            event.venue = data['venue']
        if 'address' in data:
            event.address = data['address']
        if 'ticket_price' in data:
            event.ticket_price = data['ticket_price']
        if 'capacity' in data:
            event.capacity = data['capacity']
        if 'status' in data:
            event.status = data['status']
        if 'band_id' in data:
            # 验证新乐队是否存在
            if not Band.query.get(data['band_id']):
                return jsonify({'error': '乐队不存在'}), 404
            event.band_id = data['band_id']
        if 'poster_image_url' in data:
            event.poster_image_url = data['poster_image_url']
        
        db.session.commit()
        
        return jsonify(event.to_dict())
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.exception("更新演出活动失败")
        return jsonify({'error': '数据库操作失败'}), 500
    except Exception as e:
        logging.exception("未知错误")
        return jsonify({'error': '服务器内部错误'}), 500

# 删除演出活动
@events_bp.route('/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """删除演出活动（物理删除所有相关图片）"""
    try:
        event = Event.query.filter_by(id=event_id, is_deleted=False).first()
        if not event:
            return jsonify({'error': '演出活动不存在'}), 404

        # 记录活动信息用于日志
        event_title = event.title

        # 删除演出活动相关的所有图片文件（包括历史图片）
        deleted_files = delete_event_related_images(event)

        # 物理删除数据库记录
        db.session.delete(event)
        db.session.commit()

        return jsonify({
            'message': f'演出活动 "{event_title}" 删除成功',
            'deleted_files_count': len(deleted_files)
        }), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"删除演出活动失败: {str(e)}", exc_info=True)
        return jsonify({'error': '删除演出活动失败'}), 500

# 批量删除演出活动
@events_bp.route('/batch_delete', methods=['POST'])
def batch_delete_events():
    """批量删除演出活动（物理删除所有相关图片）"""
    try:
        data = request.json
        if not data or 'event_ids' not in data:
            return jsonify({'error': '请提供要删除的演出活动ID列表'}), 400

        event_ids = data['event_ids']
        if not isinstance(event_ids, list) or not event_ids:
            return jsonify({'error': '演出活动ID列表不能为空'}), 400

        # 验证所有演出活动是否存在
        events = Event.query.filter(Event.id.in_(event_ids), Event.is_deleted == False).all()
        if len(events) != len(event_ids):
            found_ids = [event.id for event in events]
            missing_ids = [eid for eid in event_ids if eid not in found_ids]
            return jsonify({'error': f'以下演出活动不存在: {missing_ids}'}), 404

        deleted_events = []
        total_deleted_files = 0

        # 逐个删除演出活动
        for event in events:
            try:
                event_title = event.title

                # 删除相关图片文件
                deleted_files = delete_event_related_images(event)
                total_deleted_files += len(deleted_files)

                # 物理删除数据库记录
                db.session.delete(event)

                deleted_events.append({
                    'id': event.id,
                    'title': event_title,
                    'deleted_files_count': len(deleted_files)
                })

            except Exception as e:
                logging.error(f"删除演出活动 {event.title} 时发生错误: {str(e)}")
                # 继续删除其他演出活动，不中断整个过程
                continue

        # 提交所有删除操作
        db.session.commit()

        return jsonify({
            'message': f'成功删除 {len(deleted_events)} 个演出活动',
            'deleted_events': deleted_events,
            'total_deleted_files': total_deleted_files
        }), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"批量删除演出活动失败: {str(e)}", exc_info=True)
        return jsonify({'error': '批量删除演出活动失败'}), 500

# 上传演出活动海报
@events_bp.route('/upload_poster', methods=['POST'])
def upload_poster():
    try:
        print(f"=== 上传请求开始 ===")
        print(f"请求方法: {request.method}")
        print(f"Content-Type: {request.content_type}")
        print(f"Files: {list(request.files.keys())}")
        print(f"Form: {list(request.form.keys())}")
        
        if 'file' not in request.files:
            print("错误: 请求中没有文件")
            return jsonify({'error': '没有选择文件'}), 400

        file = request.files['file']
        print(f"文件信息: {file.filename}, {file.content_type}, {file.content_length}")
        
        if file.filename == '':
            print("错误: 文件名为空")
            return jsonify({'error': '没有选择文件'}), 400

        # 检查文件类型
        if not allowed_file(file.filename):
            print(f"错误: 不支持的文件类型 {file.filename}")
            return jsonify({'error': '不支持的文件类型'}), 400

        # 确保上传目录存在
        events_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'events')
        os.makedirs(events_upload_dir, exist_ok=True)
        print(f"上传目录: {events_upload_dir}")

        # 生成安全的文件名
        import time
        timestamp = str(int(time.time()))
        filename = f"event_poster_{timestamp}_{secure_filename(file.filename)}"
        file_path = os.path.join(events_upload_dir, filename)
        print(f"保存路径: {file_path}")

        # 保存文件
        file.save(file_path)
        print("文件保存成功")

        # 返回相对路径
        relative_path = f"/uploads/events/{filename}"
        print(f"返回路径: {relative_path}")

        return jsonify({
            'success': True,
            'message': '海报上传成功',
            'url': relative_path,
            'poster_url': relative_path
        })

    except Exception as e:
        print(f"上传异常: {str(e)}")
        logging.exception("上传演出活动海报失败")
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename(filename):
    """生成安全的文件名"""
    import re
    import unicodedata
    
    if not filename:
        return 'unnamed'
    
    # 处理 Unicode 字符
    try:
        filename = unicodedata.normalize('NFKD', filename)
    except:
        pass
    
    # 移除或替换不安全的字符，保留文件扩展名
    name, ext = os.path.splitext(filename)
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '-', name)
    
    # 如果处理后名称为空，使用默认名称
    if not name.strip():
        name = 'unnamed'
    
    return f"{name}{ext}"

