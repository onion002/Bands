#!/bin/bash

# 部署验证脚本 - 逐步验证每个部署步骤

echo "🔍 部署验证脚本启动..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 验证结果统计
PASSED=0
FAILED=0
TOTAL=0

# 验证函数
verify_step() {
    local step_name="$1"
    local command="$2"
    local expected="$3"
    
    echo -e "\n${BLUE}🔍 验证: $step_name${NC}"
    echo "执行命令: $command"
    
    # 执行验证命令
    local result
    result=$(eval "$command" 2>&1)
    local exit_code=$?
    
    TOTAL=$((TOTAL + 1))
    
    if [ $exit_code -eq 0 ] && [[ "$result" == *"$expected"* ]]; then
        echo -e "${GREEN}✅ 通过${NC}"
        echo "结果: $result"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ 失败${NC}"
        echo "结果: $result"
        echo "期望包含: $expected"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# 验证函数（只检查退出码）
verify_step_exit() {
    local step_name="$1"
    local command="$2"
    
    echo -e "\n${BLUE}🔍 验证: $step_name${NC}"
    echo "执行命令: $command"
    
    # 执行验证命令
    local result
    result=$(eval "$command" 2>&1)
    local exit_code=$?
    
    TOTAL=$((TOTAL + 1))
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ 通过${NC}"
        echo "结果: $result"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ 失败${NC}"
        echo "结果: $result"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo -e "${YELLOW}🚀 开始部署验证...${NC}"

# 第一步：环境检查和准备
echo -e "\n${YELLOW}=== 第一步：环境检查和准备 ===${NC}"

verify_step "系统版本" "lsb_release -a" "Alibaba Cloud Linux"
verify_step "当前用户" "whoami" "root"
verify_step "sudo权限" "sudo whoami" "root"
verify_step "当前目录" "pwd" "/www/wwwroot"
verify_step "Python版本" "python3 --version" "Python 3"
verify_step "Node.js版本" "node --version" "v"
verify_step "npm版本" "npm --version" "."
verify_step "Git版本" "git --version" "git version"

# 第二步：基础环境安装
echo -e "\n${YELLOW}=== 第二步：基础环境安装 ===${NC}"

verify_step "MySQL服务状态" "sudo systemctl is-active mysqld" "active"
verify_step "Redis服务状态" "sudo systemctl is-active redis" "active"
verify_step "MySQL端口监听" "sudo netstat -tlnp | grep :3306" "3306"
verify_step "Redis端口监听" "sudo netstat -tlnp | grep :6379" "6379"

# 第三步：项目部署
echo -e "\n${YELLOW}=== 第三步：项目部署 ===${NC}"

verify_step "项目目录存在" "ls -la" "deploy.sh"
verify_step "后端目录存在" "ls -la BandManager/" "app.py"
verify_step "前端目录存在" "ls -la band-manager-front/" "package.json"
verify_step "环境变量文件" "ls -la BandManager/.env" ".env"
verify_step "环境变量权限" "ls -la BandManager/.env | awk '{print \$1}'" "-rw-------"
verify_step "启动脚本存在" "ls -la start_backend.sh" "start_backend.sh"
verify_step "启动脚本权限" "ls -la start_backend.sh | awk '{print \$1}'" "-rwx"

# 第四步：服务启动
echo -e "\n${YELLOW}=== 第四步：服务启动 ===${NC}"

verify_step "后端进程运行" "ps aux | grep 'python.*app_production' | grep -v grep" "python"
verify_step "后端端口监听" "sudo netstat -tlnp | grep :5000" "5000"
verify_step "前端进程运行" "ps aux | grep 'node.*preview' | grep -v grep" "node"
verify_step "前端端口监听" "sudo netstat -tlnp | grep :3000" "3000"

# 第五步：网络配置
echo -e "\n${YELLOW}=== 第五步：网络配置 ===${NC}"

verify_step "防火墙端口3000" "sudo firewall-cmd --list-ports | grep 3000" "3000"
verify_step "防火墙端口5000" "sudo firewall-cmd --list-ports | grep 5000" "5000"

# 第六步：功能验证
echo -e "\n${YELLOW}=== 第六步：功能验证 ===${NC}"

verify_step_exit "后端健康检查" "curl -s http://localhost:5000/health"
verify_step_exit "前端访问" "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000"
verify_step_exit "数据库连接" "mysql -u root -p -e 'USE band_db; SHOW TABLES;'"
verify_step_exit "Redis连接" "redis-cli ping"

# 外部访问测试
echo -e "\n${YELLOW}=== 外部访问测试 ===${NC}"

verify_step_exit "外部后端访问" "curl -s http://47.107.79.244:5000/health"
verify_step_exit "外部前端访问" "curl -s -o /dev/null -w '%{http_code}' http://47.107.79.244:3000"

# 显示验证结果
echo -e "\n${YELLOW}=== 验证结果汇总 ===${NC}"
echo -e "总验证项目: ${TOTAL}"
echo -e "${GREEN}通过: ${PASSED}${NC}"
echo -e "${RED}失败: ${FAILED}${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 所有验证项目都通过了！部署成功！${NC}"
    echo -e "\n${BLUE}📋 访问地址:${NC}"
    echo -e "前端: http://47.107.79.244:3000"
    echo -e "后端: http://47.107.79.244:5000"
    echo -e "健康检查: http://47.107.79.244:5000/health"
else
    echo -e "\n${RED}⚠️  有 ${FAILED} 个验证项目失败，请检查并修复问题。${NC}"
    echo -e "\n${BLUE}📋 建议:${NC}"
    echo -e "1. 查看失败的验证项目"
    echo -e "2. 检查相关服务状态"
    echo -e "3. 查看错误日志"
    echo -e "4. 重新运行验证脚本"
fi

echo -e "\n${BLUE}📖 详细部署指南请参考: COMPLETE_DEPLOYMENT_GUIDE.md${NC}"
