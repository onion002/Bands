import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime

uploads_bp = Blueprint('uploads', __name__)

def allowed_file(filename):
    """检查文件扩展名是否合法"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def generate_unique_filename(filename):
    """生成唯一的文件名"""
    # 提取文件扩展名
    ext = filename.rsplit('.', 1)[1].lower()
    # 使用时间戳生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{timestamp}_{secure_filename(filename)}"

@uploads_bp.route('/', methods=['POST'])
def upload_file():
    """处理文件上传"""
    # 检查是否有文件部分
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # 如果用户没有选择文件
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # 检查文件类型
    if file and allowed_file(file.filename):
        # 生成唯一文件名
        filename = generate_unique_filename(file.filename)
        # 确保上传目录存在
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        # 保存文件
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 生成访问URL
        file_url = f"{current_app.config['API_BASE_URL']}/uploads/{filename}"
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'filename': filename,
            'url': file_url
        }), 201
    
    return jsonify({'error': 'File type not allowed'}), 400

@uploads_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """提供上传的文件"""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)