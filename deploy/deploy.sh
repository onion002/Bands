#!/bin/bash

# ===========================================
# 乐队管理系统 - 一键部署脚本
# ===========================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        exit 1
    fi
}

# 检查系统环境
check_system() {
    log_info "检查系统环境..."
    
    # 检查操作系统
    if [[ ! -f /etc/centos-release ]] && [[ ! -f /etc/redhat-release ]]; then
        log_warning "此脚本主要针对CentOS/RHEL系统，其他系统可能需要调整"
    fi
    
    # 检查必要的命令
    local commands=("git" "python3" "node" "npm" "mysql" "redis-cli")
    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "缺少必要命令: $cmd"
            exit 1
        fi
    done
    
    log_success "系统环境检查通过"
}

# 克隆或更新代码
setup_code() {
    log_info "设置项目代码..."
    
    local project_dir="/opt/Bands"
    
    if [[ -d "$project_dir" ]]; then
        log_info "项目目录已存在，更新代码..."
        cd "$project_dir"
        git pull origin main
    else
        log_info "克隆项目代码..."
        cd /opt
        git clone https://github.com/onion002/Bands.git
        cd "$project_dir"
    fi
    
    log_success "代码设置完成"
}

# 设置后端环境
setup_backend() {
    log_info "设置后端环境..."
    
    cd /opt/Bands/BandManager
    
    # 创建.env文件
    if [[ ! -f .env ]]; then
        log_info "创建环境变量文件..."
        cat > .env << 'EOF'
# 数据库配置
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=002101
DB_NAME=band_db

# 邮件服务配置
MAIL_SERVER=smtp.qq.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=3137826052@qq.com
MAIL_PASSWORD=ptvporstvsbqdegc

# API配置
API_BASE_URL=http://47.108.30.30:5000

# 应用配置
FLASK_ENV=production
DEBUG=false
SECRET_KEY=your-secret-key-here

# 文件上传配置
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Redis配置
REDIS_URL=redis://localhost:6379/0

# AI配置
OPENAI_API_KEY=your-openai-api-key-here
EOF
        log_success "环境变量文件创建完成"
    fi
    
    # 安装Python依赖
    log_info "安装Python依赖..."
    pip3 install -r requirements.txt
    
    # 创建上传目录
    mkdir -p uploads
    
    # 初始化数据库
    log_info "初始化数据库..."
    python3 -c "
from app_factory import create_app
from models import db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ 数据库表创建成功')
"
    
    log_success "后端环境设置完成"
}

# 设置前端环境
setup_frontend() {
    log_info "设置前端环境..."
    
    cd /opt/Bands/band-manager-front
    
    # 创建环境变量文件
    if [[ ! -f .env.production ]]; then
        log_info "创建前端环境变量文件..."
        echo "VITE_API_BASE_URL=http://47.108.30.30:5000" > .env.production
    fi
    
    # 安装依赖
    log_info "安装前端依赖..."
    npm install
    
    # 构建前端
    log_info "构建前端..."
    npm run build
    
    log_success "前端环境设置完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动后端
    cd /opt/Bands/BandManager
    nohup python3 app.py > backend.log 2>&1 &
    local backend_pid=$!
    echo $backend_pid > backend.pid
    
    # 等待后端启动
    sleep 3
    
    # 启动前端
    cd /opt/Bands/band-manager-front
    nohup npm run preview > frontend.log 2>&1 &
    local frontend_pid=$!
    echo $frontend_pid > frontend.pid
    
    # 等待服务启动
    sleep 5
    
    # 检查服务状态
    if netstat -tlnp | grep -q ":5000" && netstat -tlnp | grep -q ":3000"; then
        log_success "服务启动成功"
        log_info "后端服务: http://47.108.30.30:5000"
        log_info "前端服务: http://47.108.30.30:3000"
        log_info "默认管理员账户: admin-syx / syx002101"
    else
        log_error "服务启动失败，请检查日志"
        exit 1
    fi
}

# 主函数
main() {
    log_info "开始部署乐队管理系统..."
    
    check_root
    check_system
    setup_code
    setup_backend
    setup_frontend
    start_services
    
    log_success "部署完成！"
    log_info "访问地址: http://47.108.30.30:3000"
    log_info "管理员账户: admin-syx / syx002101"
}

# 运行主函数
main "$@"
