#!/bin/bash

# 乐队管理系统 - 一键快速部署脚本
# 适用于新服务器快速部署

echo "🚀 乐队管理系统一键快速部署启动..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查是否在项目根目录
if [ ! -f "quick_setup.sh" ]; then
    echo -e "${RED}❌ 请在项目根目录运行此脚本${NC}"
    exit 1
fi

echo -e "${BLUE}📋 部署配置:${NC}"
echo -e "   服务器IP: 47.108.30.30"
echo -e "   后端端口: 5000"
echo -e "   前端端口: 3000"
echo -e "   环境: production"

# 第一步：安装基础环境
echo -e "\n${YELLOW}=== 第一步：安装基础环境 ===${NC}"
chmod +x quick_setup.sh
./quick_setup.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 基础环境安装失败${NC}"
    exit 1
fi

# 第二步：配置环境变量
echo -e "\n${YELLOW}=== 第二步：配置环境变量 ===${NC}"
chmod +x setup_env.sh
./setup_env.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 环境变量配置失败${NC}"
    exit 1
fi

# 第三步：部署项目
echo -e "\n${YELLOW}=== 第三步：部署项目 ===${NC}"
chmod +x simple_deploy.sh
./simple_deploy.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 项目部署失败${NC}"
    exit 1
fi

# 第四步：启动服务
echo -e "\n${YELLOW}=== 第四步：启动服务 ===${NC}"
echo -e "${BLUE}启动后端服务...${NC}"
./start_backend.sh &
BACKEND_PID=$!

# 等待后端启动
sleep 5

echo -e "${BLUE}启动前端服务...${NC}"
./start_frontend.sh &
FRONTEND_PID=$!

# 等待前端启动
sleep 5

# 第五步：验证部署
echo -e "\n${YELLOW}=== 第五步：验证部署 ===${NC}"
chmod +x verify_deployment.sh
./verify_deployment.sh

# 显示最终结果
echo -e "\n${GREEN}🎉 一键部署完成！${NC}"
echo -e "\n${BLUE}📋 服务状态:${NC}"
echo -e "   后端服务PID: $BACKEND_PID"
echo -e "   前端服务PID: $FRONTEND_PID"

echo -e "\n${BLUE}🌐 访问地址:${NC}"
echo -e "   前端应用: http://47.108.30.30:3000"
echo -e "   后端API: http://47.108.30.30:5000"
echo -e "   健康检查: http://47.108.30.30:5000/health"

echo -e "\n${BLUE}📖 部署文档:${NC}"
echo -e "   部署总结: DEPLOYMENT_SUMMARY.md"
echo -e "   完整指南: COMPLETE_DEPLOYMENT_GUIDE.md"

echo -e "\n${YELLOW}⚠️  注意:${NC}"
echo -e "   1. 后端和前端服务已在后台启动"
echo -e "   2. 如需停止服务，运行: ./stop_services.sh"
echo -e "   3. 如需查看日志，检查进程输出"

echo -e "\n${GREEN}✨ 部署完成！现在可以访问你的应用了！${NC}"
