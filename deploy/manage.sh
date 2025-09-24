#!/bin/bash

# ===========================================
# 乐队管理系统 - 服务管理脚本
# ===========================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目目录
PROJECT_DIR="/opt/Bands"
BACKEND_DIR="$PROJECT_DIR/BandManager"
FRONTEND_DIR="$PROJECT_DIR/band-manager-front"

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

# 检查服务状态
check_status() {
    log_info "检查服务状态..."
    
    # 检查后端服务
    if netstat -tlnp | grep -q ":5000"; then
        local backend_pid=$(netstat -tlnp | grep ":5000" | awk '{print $7}' | cut -d'/' -f1)
        log_success "后端服务运行中 (PID: $backend_pid)"
    else
        log_warning "后端服务未运行"
    fi
    
    # 检查前端服务
    if netstat -tlnp | grep -q ":3000"; then
        local frontend_pid=$(netstat -tlnp | grep ":3000" | awk '{print $7}' | cut -d'/' -f1)
        log_success "前端服务运行中 (PID: $frontend_pid)"
    else
        log_warning "前端服务未运行"
    fi
    
    # 检查数据库
    if systemctl is-active --quiet mysqld; then
        log_success "MySQL服务运行中"
    else
        log_warning "MySQL服务未运行"
    fi
    
    # 检查Redis
    if systemctl is-active --quiet redis; then
        log_success "Redis服务运行中"
    else
        log_warning "Redis服务未运行"
    fi
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动后端
    if ! netstat -tlnp | grep -q ":5000"; then
        log_info "启动后端服务..."
        cd "$BACKEND_DIR"
        nohup python3 app.py > backend.log 2>&1 &
        local backend_pid=$!
        echo $backend_pid > backend.pid
        sleep 3
        
        if netstat -tlnp | grep -q ":5000"; then
            log_success "后端服务启动成功 (PID: $backend_pid)"
        else
            log_error "后端服务启动失败"
            return 1
        fi
    else
        log_warning "后端服务已在运行"
    fi
    
    # 启动前端
    if ! netstat -tlnp | grep -q ":3000"; then
        log_info "启动前端服务..."
        cd "$FRONTEND_DIR"
        nohup npm run preview > frontend.log 2>&1 &
        local frontend_pid=$!
        echo $frontend_pid > frontend.pid
        sleep 3
        
        if netstat -tlnp | grep -q ":3000"; then
            log_success "前端服务启动成功 (PID: $frontend_pid)"
        else
            log_error "前端服务启动失败"
            return 1
        fi
    else
        log_warning "前端服务已在运行"
    fi
    
    log_success "所有服务启动完成"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    # 停止后端服务
    if [[ -f "$BACKEND_DIR/backend.pid" ]]; then
        local backend_pid=$(cat "$BACKEND_DIR/backend.pid")
        if kill -0 "$backend_pid" 2>/dev/null; then
            kill "$backend_pid"
            log_success "后端服务已停止 (PID: $backend_pid)"
        fi
        rm -f "$BACKEND_DIR/backend.pid"
    fi
    
    # 停止前端服务
    if [[ -f "$FRONTEND_DIR/frontend.pid" ]]; then
        local frontend_pid=$(cat "$FRONTEND_DIR/frontend.pid")
        if kill -0 "$frontend_pid" 2>/dev/null; then
            kill "$frontend_pid"
            log_success "前端服务已停止 (PID: $frontend_pid)"
        fi
        rm -f "$FRONTEND_DIR/frontend.pid"
    fi
    
    # 强制停止占用端口的进程
    local backend_pid=$(netstat -tlnp | grep ":5000" | awk '{print $7}' | cut -d'/' -f1)
    if [[ -n "$backend_pid" ]]; then
        kill -9 "$backend_pid" 2>/dev/null
        log_info "强制停止后端服务 (PID: $backend_pid)"
    fi
    
    local frontend_pid=$(netstat -tlnp | grep ":3000" | awk '{print $7}' | cut -d'/' -f1)
    if [[ -n "$frontend_pid" ]]; then
        kill -9 "$frontend_pid" 2>/dev/null
        log_info "强制停止前端服务 (PID: $frontend_pid)"
    fi
    
    log_success "所有服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    stop_services
    sleep 2
    start_services
}

# 查看日志
view_logs() {
    local service=$1
    
    case $service in
        "backend"|"b")
            log_info "查看后端日志..."
            if [[ -f "$BACKEND_DIR/backend.log" ]]; then
                tail -f "$BACKEND_DIR/backend.log"
            else
                log_error "后端日志文件不存在"
            fi
            ;;
        "frontend"|"f")
            log_info "查看前端日志..."
            if [[ -f "$FRONTEND_DIR/frontend.log" ]]; then
                tail -f "$FRONTEND_DIR/frontend.log"
            else
                log_error "前端日志文件不存在"
            fi
            ;;
        "all"|"a")
            log_info "查看所有日志..."
            echo "=== 后端日志 ==="
            if [[ -f "$BACKEND_DIR/backend.log" ]]; then
                tail -20 "$BACKEND_DIR/backend.log"
            fi
            echo -e "\n=== 前端日志 ==="
            if [[ -f "$FRONTEND_DIR/frontend.log" ]]; then
                tail -20 "$FRONTEND_DIR/frontend.log"
            fi
            ;;
        *)
            log_error "无效的日志类型: $service"
            log_info "可用选项: backend(b), frontend(f), all(a)"
            ;;
    esac
}

# 更新代码
update_code() {
    log_info "更新代码..."
    
    cd "$PROJECT_DIR"
    git pull origin main
    
    # 重新构建前端
    log_info "重新构建前端..."
    cd "$FRONTEND_DIR"
    npm run build
    
    log_success "代码更新完成"
}

# 备份数据
backup_data() {
    local backup_dir="/opt/backups/bands_$(date +%Y%m%d_%H%M%S)"
    
    log_info "备份数据到: $backup_dir"
    
    mkdir -p "$backup_dir"
    
    # 备份数据库
    log_info "备份数据库..."
    mysqldump -u root -p002101 band_db > "$backup_dir/band_db.sql"
    
    # 备份上传文件
    log_info "备份上传文件..."
    cp -r "$BACKEND_DIR/uploads" "$backup_dir/"
    
    # 备份配置文件
    log_info "备份配置文件..."
    cp "$BACKEND_DIR/.env" "$backup_dir/"
    
    log_success "数据备份完成: $backup_dir"
}

# 显示帮助信息
show_help() {
    echo "乐队管理系统 - 服务管理脚本"
    echo ""
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  status, s      - 检查服务状态"
    echo "  start          - 启动所有服务"
    echo "  stop           - 停止所有服务"
    echo "  restart, r     - 重启所有服务"
    echo "  logs [类型]    - 查看日志 (backend|frontend|all)"
    echo "  update, u      - 更新代码并重新构建"
    echo "  backup, b      - 备份数据"
    echo "  help, h        - 显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 status              # 检查服务状态"
    echo "  $0 restart             # 重启所有服务"
    echo "  $0 logs backend        # 查看后端日志"
    echo "  $0 logs all            # 查看所有日志"
}

# 主函数
main() {
    case "${1:-help}" in
        "status"|"s")
            check_status
            ;;
        "start")
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "restart"|"r")
            restart_services
            ;;
        "logs")
            view_logs "${2:-all}"
            ;;
        "update"|"u")
            update_code
            ;;
        "backup"|"b")
            backup_data
            ;;
        "help"|"h"|*)
            show_help
            ;;
    esac
}

# 运行主函数
main "$@"
