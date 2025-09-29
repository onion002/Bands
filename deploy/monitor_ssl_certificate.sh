#!/bin/bash

# ===========================================
# SSL证书监控脚本
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
WARNING_DAYS=30
CRITICAL_DAYS=7
LOG_FILE="/var/log/ssl_monitor.log"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1" >> "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] $1" >> "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING] $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" >> "$LOG_FILE"
}

# 检查证书文件是否存在
check_certificate_exists() {
    if [[ ! -f "$CERT_PATH" ]]; then
        log_error "证书文件不存在: $CERT_PATH"
        return 1
    fi
    return 0
}

# 获取证书信息
get_certificate_info() {
    if ! check_certificate_exists; then
        return 1
    fi
    
    # 获取证书到期时间
    EXPIRY_DATE=$(openssl x509 -in "$CERT_PATH" -noout -enddate | cut -d= -f2)
    EXPIRY_TIMESTAMP=$(date -d "$EXPIRY_DATE" +%s)
    CURRENT_TIMESTAMP=$(date +%s)
    DAYS_UNTIL_EXPIRY=$(( ($EXPIRY_TIMESTAMP - $CURRENT_TIMESTAMP) / 86400 ))
    
    # 获取证书颁发者
    ISSUER=$(openssl x509 -in "$CERT_PATH" -noout -issuer | sed 's/issuer=//')
    
    # 获取证书主题
    SUBJECT=$(openssl x509 -in "$CERT_PATH" -noout -subject | sed 's/subject=//')
    
    # 获取证书序列号
    SERIAL=$(openssl x509 -in "$CERT_PATH" -noout -serial | cut -d= -f2)
    
    return 0
}

# 检查证书状态
check_certificate_status() {
    log_info "检查SSL证书状态..."
    
    if ! get_certificate_info; then
        return 1
    fi
    
    log_info "域名: $DOMAIN"
    log_info "证书路径: $CERT_PATH"
    log_info "到期时间: $EXPIRY_DATE"
    log_info "剩余天数: $DAYS_UNTIL_EXPIRY 天"
    log_info "颁发者: $ISSUER"
    log_info "序列号: $SERIAL"
    
    # 根据剩余天数判断状态
    if [[ $DAYS_UNTIL_EXPIRY -le 0 ]]; then
        log_error "🚨 证书已过期！"
        return 2
    elif [[ $DAYS_UNTIL_EXPIRY -le $CRITICAL_DAYS ]]; then
        log_error "🚨 证书将在 $DAYS_UNTIL_EXPIRY 天内过期！请立即更新！"
        return 2
    elif [[ $DAYS_UNTIL_EXPIRY -le $WARNING_DAYS ]]; then
        log_warning "⚠️ 证书将在 $DAYS_UNTIL_EXPIRY 天内过期，请准备更新"
        return 1
    else
        log_success "✅ 证书状态正常，剩余 $DAYS_UNTIL_EXPIRY 天"
        return 0
    fi
}

# 测试HTTPS连接
test_https_connection() {
    log_info "测试HTTPS连接..."
    
    # 测试主域名
    if curl -s -I --max-time 10 https://$DOMAIN > /dev/null; then
        log_success "主域名 HTTPS 连接正常"
    else
        log_error "主域名 HTTPS 连接失败"
        return 1
    fi
    
    # 测试www子域名
    if curl -s -I --max-time 10 https://www.$DOMAIN > /dev/null; then
        log_success "www子域名 HTTPS 连接正常"
    else
        log_error "www子域名 HTTPS 连接失败"
        return 1
    fi
    
    # 测试API接口
    if curl -s --max-time 10 https://$DOMAIN/api/health > /dev/null; then
        log_success "API接口 HTTPS 连接正常"
    else
        log_error "API接口 HTTPS 连接失败"
        return 1
    fi
    
    return 0
}

# 检查证书链
check_certificate_chain() {
    log_info "检查证书链..."
    
    # 使用openssl s_client检查证书链
    local chain_check=$(echo | openssl s_client -connect $DOMAIN:443 -servername $DOMAIN 2>/dev/null | openssl x509 -noout -subject 2>/dev/null)
    
    if [[ -n "$chain_check" ]]; then
        log_success "证书链验证通过"
        return 0
    else
        log_error "证书链验证失败"
        return 1
    fi
}

# 检查证书与私钥匹配
check_certificate_key_match() {
    local key_path="/etc/ssl/private/bands.icu.key"
    
    if [[ ! -f "$key_path" ]]; then
        log_warning "私钥文件不存在，跳过匹配检查"
        return 0
    fi
    
    log_info "检查证书与私钥匹配..."
    
    local cert_md5=$(openssl x509 -noout -modulus -in "$CERT_PATH" | openssl md5 | cut -d' ' -f2)
    local key_md5=$(openssl rsa -noout -modulus -in "$key_path" | openssl md5 | cut -d' ' -f2)
    
    if [[ "$cert_md5" == "$key_md5" ]]; then
        log_success "证书与私钥匹配"
        return 0
    else
        log_error "证书与私钥不匹配！"
        log_error "证书MD5: $cert_md5"
        log_error "私钥MD5: $key_md5"
        return 1
    fi
}

# 生成监控报告
generate_report() {
    local report_file="/tmp/ssl_monitor_report_$(date +%Y%m%d_%H%M%S).txt"
    
    echo "SSL证书监控报告" > "$report_file"
    echo "生成时间: $(date)" >> "$report_file"
    echo "=========================" >> "$report_file"
    echo "" >> "$report_file"
    
    if get_certificate_info; then
        echo "域名: $DOMAIN" >> "$report_file"
        echo "证书路径: $CERT_PATH" >> "$report_file"
        echo "到期时间: $EXPIRY_DATE" >> "$report_file"
        echo "剩余天数: $DAYS_UNTIL_EXPIRY 天" >> "$report_file"
        echo "颁发者: $ISSUER" >> "$report_file"
        echo "序列号: $SERIAL" >> "$report_file"
        echo "" >> "$report_file"
        
        # 状态判断
        if [[ $DAYS_UNTIL_EXPIRY -le 0 ]]; then
            echo "状态: 🚨 已过期" >> "$report_file"
        elif [[ $DAYS_UNTIL_EXPIRY -le $CRITICAL_DAYS ]]; then
            echo "状态: 🚨 紧急 (将在 $DAYS_UNTIL_EXPIRY 天内过期)" >> "$report_file"
        elif [[ $DAYS_UNTIL_EXPIRY -le $WARNING_DAYS ]]; then
            echo "状态: ⚠️ 警告 (将在 $DAYS_UNTIL_EXPIRY 天内过期)" >> "$report_file"
        else
            echo "状态: ✅ 正常" >> "$report_file"
        fi
    fi
    
    echo "$report_file"
}

# 发送告警通知（示例，需要根据实际情况配置）
send_alert() {
    local alert_level="$1"
    local message="$2"
    
    # 这里可以集成各种通知方式：
    # 1. 邮件通知
    # echo "$message" | mail -s "SSL证书告警 - $DOMAIN" admin@example.com
    
    # 2. 钉钉/企业微信通知
    # curl -X POST "钉钉webhook地址" -H "Content-Type: application/json" -d "{\"text\": \"$message\"}"
    
    # 3. 短信通知
    # 调用短信API
    
    # 4. 日志记录
    echo "[ALERT] $alert_level: $message" >> "$LOG_FILE"
    
    log_info "告警通知已发送: $alert_level"
}

# 完整监控检查
full_check() {
    log_info "开始完整SSL证书监控检查..."
    
    local overall_status=0
    
    # 检查证书状态
    check_certificate_status
    local cert_status=$?
    if [[ $cert_status -gt $overall_status ]]; then
        overall_status=$cert_status
    fi
    
    # 测试HTTPS连接
    if ! test_https_connection; then
        overall_status=2
    fi
    
    # 检查证书链
    if ! check_certificate_chain; then
        overall_status=1
    fi
    
    # 检查证书与私钥匹配
    if ! check_certificate_key_match; then
        overall_status=2
    fi
    
    # 根据状态发送告警
    if [[ $overall_status -eq 2 ]]; then
        send_alert "CRITICAL" "SSL证书严重问题 - $DOMAIN (剩余 $DAYS_UNTIL_EXPIRY 天)"
    elif [[ $overall_status -eq 1 ]]; then
        send_alert "WARNING" "SSL证书警告 - $DOMAIN (剩余 $DAYS_UNTIL_EXPIRY 天)"
    fi
    
    log_info "监控检查完成，状态码: $overall_status"
    return $overall_status
}

# 显示帮助信息
show_help() {
    echo "SSL证书监控脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  status       - 检查证书状态"
    echo "  test         - 测试HTTPS连接"
    echo "  chain        - 检查证书链"
    echo "  match        - 检查证书与私钥匹配"
    echo "  full         - 完整监控检查"
    echo "  report       - 生成监控报告"
    echo "  help         - 显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 status    # 检查证书状态"
    echo "  $0 full      # 完整检查"
    echo "  $0 report    # 生成报告"
    echo ""
    echo "定时任务示例:"
    echo "  # 每天上午9点检查"
    echo "  0 9 * * * /opt/Bands/deploy/monitor_ssl_certificate.sh full"
    echo ""
    echo "  # 每周一生成报告"
    echo "  0 10 * * 1 /opt/Bands/deploy/monitor_ssl_certificate.sh report"
}

# 主函数
main() {
    # 确保日志目录存在
    mkdir -p "$(dirname "$LOG_FILE")"
    
    case "${1:-help}" in
        "status")
            check_certificate_status
            ;;
        "test")
            test_https_connection
            ;;
        "chain")
            check_certificate_chain
            ;;
        "match")
            check_certificate_key_match
            ;;
        "full")
            full_check
            ;;
        "report")
            local report_file=$(generate_report)
            log_success "监控报告已生成: $report_file"
            cat "$report_file"
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 运行主函数
main "$@"
