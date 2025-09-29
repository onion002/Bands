#!/bin/bash

# ===========================================
# SSL证书快速更新脚本
# ===========================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
DOMAIN="bands.icu"
CERT_PATH="/etc/ssl/certs/bands.icu.pem"
KEY_PATH="/etc/ssl/private/bands.icu.key"
NGINX_CONFIG="/etc/nginx/conf.d/bands.icu.conf"

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

# 检查当前证书状态
check_current_certificate() {
    log_info "检查当前证书状态..."
    
    if [[ -f "$CERT_PATH" ]]; then
        local expiry_date=$(openssl x509 -in "$CERT_PATH" -noout -enddate | cut -d= -f2)
        local expiry_timestamp=$(date -d "$expiry_date" +%s)
        local current_timestamp=$(date +%s)
        local days_until_expiry=$(( ($expiry_timestamp - $current_timestamp) / 86400 ))
        
        log_info "当前证书到期时间: $expiry_date"
        log_info "剩余有效天数: $days_until_expiry 天"
        
        if [[ $days_until_expiry -le 30 ]]; then
            log_warning "证书将在30天内到期，建议尽快更新！"
        fi
    else
        log_error "未找到当前证书文件: $CERT_PATH"
        return 1
    fi
}

# 备份现有证书
backup_certificates() {
    local backup_date=$(date +%Y%m%d_%H%M%S)
    local backup_dir="/opt/ssl_backups/$backup_date"
    
    log_info "备份现有证书到: $backup_dir"
    
    mkdir -p "$backup_dir"
    
    if [[ -f "$CERT_PATH" ]]; then
        cp "$CERT_PATH" "$backup_dir/bands.icu.pem"
        log_success "证书文件已备份"
    fi
    
    if [[ -f "$KEY_PATH" ]]; then
        cp "$KEY_PATH" "$backup_dir/bands.icu.key"
        log_success "私钥文件已备份"
    fi
    
    echo "$backup_dir" > /tmp/ssl_backup_path
    log_success "备份完成: $backup_dir"
}

# 验证新证书文件
validate_new_certificates() {
    local new_cert="$1"
    local new_key="$2"
    
    log_info "验证新证书文件..."
    
    # 检查文件是否存在
    if [[ ! -f "$new_cert" ]]; then
        log_error "新证书文件不存在: $new_cert"
        return 1
    fi
    
    if [[ ! -f "$new_key" ]]; then
        log_error "新私钥文件不存在: $new_key"
        return 1
    fi
    
    # 验证证书格式
    if ! openssl x509 -in "$new_cert" -text -noout > /dev/null 2>&1; then
        log_error "新证书文件格式无效"
        return 1
    fi
    
    # 验证私钥格式
    if ! openssl rsa -in "$new_key" -check > /dev/null 2>&1; then
        log_error "新私钥文件格式无效"
        return 1
    fi
    
    # 验证证书和私钥匹配
    local cert_md5=$(openssl x509 -noout -modulus -in "$new_cert" | openssl md5 | cut -d' ' -f2)
    local key_md5=$(openssl rsa -noout -modulus -in "$new_key" | openssl md5 | cut -d' ' -f2)
    
    if [[ "$cert_md5" != "$key_md5" ]]; then
        log_error "证书和私钥不匹配！"
        log_error "证书MD5: $cert_md5"
        log_error "私钥MD5: $key_md5"
        return 1
    fi
    
    # 检查证书域名
    local cert_domains=$(openssl x509 -in "$new_cert" -text -noout | grep -A1 "Subject Alternative Name" | tail -1)
    if [[ "$cert_domains" == *"bands.icu"* ]]; then
        log_success "证书域名验证通过"
    else
        log_warning "证书可能不包含 bands.icu 域名，请检查"
    fi
    
    # 检查证书有效期
    local expiry_date=$(openssl x509 -in "$new_cert" -noout -enddate | cut -d= -f2)
    local expiry_timestamp=$(date -d "$expiry_date" +%s)
    local current_timestamp=$(date +%s)
    
    if [[ $expiry_timestamp -gt $current_timestamp ]]; then
        local days_valid=$(( ($expiry_timestamp - $current_timestamp) / 86400 ))
        log_success "新证书有效期: $expiry_date (剩余 $days_valid 天)"
    else
        log_error "新证书已过期！"
        return 1
    fi
    
    log_success "新证书验证通过"
    return 0
}

# 安装新证书
install_new_certificates() {
    local new_cert="$1"
    local new_key="$2"
    
    log_info "安装新证书..."
    
    # 复制新证书文件
    cp "$new_cert" "$CERT_PATH"
    cp "$new_key" "$KEY_PATH"
    
    # 设置正确权限
    chmod 644 "$CERT_PATH"
    chmod 600 "$KEY_PATH"
    chown root:root "$CERT_PATH"
    chown root:root "$KEY_PATH"
    
    log_success "新证书文件已安装"
}

# 测试Nginx配置
test_nginx_config() {
    log_info "测试Nginx配置..."
    
    if nginx -t > /dev/null 2>&1; then
        log_success "Nginx配置测试通过"
        return 0
    else
        log_error "Nginx配置测试失败！"
        nginx -t
        return 1
    fi
}

# 重新加载Nginx
reload_nginx() {
    log_info "重新加载Nginx服务..."
    
    if systemctl reload nginx; then
        log_success "Nginx服务重新加载成功"
        return 0
    else
        log_error "Nginx服务重新加载失败！"
        return 1
    fi
}

# 验证更新结果
verify_update() {
    log_info "验证SSL证书更新结果..."
    
    # 检查HTTPS连接
    if curl -I https://bands.icu > /dev/null 2>&1; then
        log_success "HTTPS连接测试通过"
    else
        log_error "HTTPS连接测试失败"
        return 1
    fi
    
    # 检查API接口
    if curl -k https://bands.icu/api/health > /dev/null 2>&1; then
        log_success "API接口测试通过"
    else
        log_error "API接口测试失败"
        return 1
    fi
    
    # 显示新证书信息
    local new_expiry=$(openssl x509 -in "$CERT_PATH" -noout -enddate | cut -d= -f2)
    log_success "新证书到期时间: $new_expiry"
    
    return 0
}

# 恢复备份
restore_backup() {
    local backup_path=$(cat /tmp/ssl_backup_path 2>/dev/null)
    
    if [[ -n "$backup_path" && -d "$backup_path" ]]; then
        log_warning "恢复证书备份..."
        
        if [[ -f "$backup_path/bands.icu.pem" ]]; then
            cp "$backup_path/bands.icu.pem" "$CERT_PATH"
        fi
        
        if [[ -f "$backup_path/bands.icu.key" ]]; then
            cp "$backup_path/bands.icu.key" "$KEY_PATH"
        fi
        
        # 重新设置权限
        chmod 644 "$CERT_PATH"
        chmod 600 "$KEY_PATH"
        chown root:root "$CERT_PATH"
        chown root:root "$KEY_PATH"
        
        # 重新加载Nginx
        systemctl reload nginx
        
        log_success "证书备份已恢复"
    else
        log_error "未找到备份路径，无法自动恢复"
    fi
}

# 显示帮助信息
show_help() {
    echo "SSL证书快速更新脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  check                    - 检查当前证书状态"
    echo "  update <cert> <key>      - 更新SSL证书"
    echo "  backup                   - 仅备份当前证书"
    echo "  restore                  - 恢复最近的备份"
    echo "  verify                   - 验证当前证书状态"
    echo "  help                     - 显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 check                           # 检查证书状态"
    echo "  $0 update /tmp/new.pem /tmp/new.key  # 更新证书"
    echo "  $0 backup                          # 备份证书"
    echo "  $0 restore                         # 恢复备份"
}

# 主函数
main() {
    case "${1:-help}" in
        "check")
            check_current_certificate
            ;;
        "update")
            if [[ -z "$2" || -z "$3" ]]; then
                log_error "请提供新证书和私钥文件路径"
                echo "用法: $0 update <证书文件> <私钥文件>"
                exit 1
            fi
            
            log_info "开始SSL证书更新流程..."
            
            # 检查当前状态
            check_current_certificate
            
            # 备份现有证书
            if ! backup_certificates; then
                log_error "备份失败，终止更新"
                exit 1
            fi
            
            # 验证新证书
            if ! validate_new_certificates "$2" "$3"; then
                log_error "新证书验证失败，终止更新"
                exit 1
            fi
            
            # 安装新证书
            install_new_certificates "$2" "$3"
            
            # 测试Nginx配置
            if ! test_nginx_config; then
                log_error "Nginx配置测试失败，恢复备份..."
                restore_backup
                exit 1
            fi
            
            # 重新加载Nginx
            if ! reload_nginx; then
                log_error "Nginx重新加载失败，恢复备份..."
                restore_backup
                exit 1
            fi
            
            # 验证更新结果
            if verify_update; then
                log_success "🎉 SSL证书更新完成！"
                log_info "可以删除临时文件: $2 $3"
            else
                log_error "更新验证失败，恢复备份..."
                restore_backup
                exit 1
            fi
            ;;
        "backup")
            backup_certificates
            ;;
        "restore")
            restore_backup
            ;;
        "verify")
            verify_update
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 运行主函数
main "$@"
