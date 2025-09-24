#!/bin/bash

# 乐队管理系统 - 新服务器部署脚本
# 服务器IP: 47.108.30.30

echo "🚀 开始部署乐队管理系统到新服务器..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 服务器信息
SERVER_IP="47.108.30.30"
SERVER_USER="root"  # 根据实际情况修改
PROJECT_DIR="/www/wwwroot/git-bands"

echo -e "${BLUE}📋 部署信息:${NC}"
echo -e "   服务器IP: $SERVER_IP"
echo -e "   项目目录: $PROJECT_DIR"
echo -e "   后端端口: 5000"
echo -e "   前端端口: 3000"

# 第一步：创建项目目录
echo -e "\n${YELLOW}=== 第一步：创建项目目录 ===${NC}"
ssh $SERVER_USER@$SERVER_IP "mkdir -p $PROJECT_DIR"

# 第二步：上传代码
echo -e "\n${YELLOW}=== 第二步：上传代码 ===${NC}"
echo "正在上传项目文件..."
rsync -avz --exclude 'node_modules' --exclude '.git' --exclude 'dist' --exclude '__pycache__' --exclude '*.pyc' ./ $SERVER_USER@$SERVER_IP:$PROJECT_DIR/

# 第三步：设置权限
echo -e "\n${YELLOW}=== 第三步：设置权限 ===${NC}"
ssh $SERVER_USER@$SERVER_IP "cd $PROJECT_DIR && chmod +x deploy/*.sh"

echo -e "\n${GREEN}✅ 代码上传完成！${NC}"
echo -e "\n${BLUE}📝 下一步操作:${NC}"
echo -e "   1. 登录服务器: ssh $SERVER_USER@$SERVER_IP"
echo -e "   2. 进入项目目录: cd $PROJECT_DIR"
echo -e "   3. 运行部署脚本: ./deploy/quick_deploy_all.sh"
