#!/bin/bash

# 乐队管理系统部署脚本
# 服务器IP: 47.108.249.242

echo "🚀 开始部署乐队管理系统到生产服务器..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查是否在项目根目录
if [ ! -f "deploy.sh" ]; then
    echo -e "${RED}❌ 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 设置环境变量
export FLASK_ENV=production
export API_BASE_URL=http://47.108.249.242:5000
export SECRET_KEY=$(openssl rand -hex 32)

echo -e "${BLUE}📋 部署配置:${NC}"
echo -e "   服务器IP: 47.108.249.242"
echo -e "   后端端口: 5000"
echo -e "   前端端口: 3000"
echo -e "   环境: production"

# 1. 后端部署准备
echo -e "\n${YELLOW}🔧 准备后端环境...${NC}"
cd BandManager

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 创建Python虚拟环境...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo -e "${BLUE}📦 安装Python依赖...${NC}"
pip install -r requirements.txt

# 确保上传目录存在
mkdir -p uploads/bands uploads/members

# 设置权限
chmod 755 uploads
chmod 755 uploads/bands
chmod 755 uploads/members

echo -e "${GREEN}✅ 后端环境准备完成${NC}"

# 2. 前端构建
echo -e "\n${YELLOW}🔧 构建前端应用...${NC}"
cd ../band-manager-front

# 检查Node.js环境
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ Node.js/npm 未安装${NC}"
    exit 1
fi

# 安装依赖
echo -e "${BLUE}📦 安装前端依赖...${NC}"
npm install

# 构建生产版本
echo -e "${BLUE}🏗️ 构建生产版本...${NC}"
npm run build

echo -e "${GREEN}✅ 前端构建完成${NC}"

# 3. 创建启动脚本
echo -e "\n${YELLOW}📝 创建启动脚本...${NC}"
cd ..

# 后端启动脚本
cat > start_backend.sh << 'EOF'
#!/bin/bash
cd BandManager
source venv/bin/activate
export FLASK_ENV=production
export API_BASE_URL=http://47.108.249.242:5000
echo "🚀 启动后端服务器..."
python app_production.py
EOF

# 前端启动脚本
cat > start_frontend.sh << 'EOF'
#!/bin/bash
cd band-manager-front
echo "🚀 启动前端服务器..."
npm run preview -- --host 0.0.0.0 --port 3000
EOF

# 设置执行权限
chmod +x start_backend.sh
chmod +x start_frontend.sh

echo -e "${GREEN}✅ 启动脚本创建完成${NC}"

# 4. 创建系统服务文件（可选）
echo -e "\n${YELLOW}📝 创建系统服务文件...${NC}"

# 获取当前目录
CURRENT_DIR=$(pwd)

# 后端服务文件
cat > band-manager-backend.service << EOF
[Unit]
Description=Band Manager Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR/BandManager
Environment=FLASK_ENV=production
Environment=API_BASE_URL=http://47.108.249.242:5000
ExecStart=$CURRENT_DIR/BandManager/venv/bin/python $CURRENT_DIR/BandManager/app_production.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 前端服务文件
cat > band-manager-frontend.service << EOF
[Unit]
Description=Band Manager Frontend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR/band-manager-front
ExecStart=/usr/bin/npm run preview -- --host 0.0.0.0 --port 3000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ 系统服务文件创建完成${NC}"

# 5. 显示部署完成信息
echo -e "\n${GREEN}🎉 部署准备完成！${NC}"
echo -e "\n${BLUE}📋 下一步操作:${NC}"
echo -e "1. 手动启动服务:"
echo -e "   ${YELLOW}后端:${NC} ./start_backend.sh"
echo -e "   ${YELLOW}前端:${NC} ./start_frontend.sh"
echo -e ""
echo -e "2. 或者安装为系统服务:"
echo -e "   ${YELLOW}sudo cp band-manager-*.service /etc/systemd/system/${NC}"
echo -e "   ${YELLOW}sudo systemctl daemon-reload${NC}"
echo -e "   ${YELLOW}sudo systemctl enable band-manager-backend${NC}"
echo -e "   ${YELLOW}sudo systemctl enable band-manager-frontend${NC}"
echo -e "   ${YELLOW}sudo systemctl start band-manager-backend${NC}"
echo -e "   ${YELLOW}sudo systemctl start band-manager-frontend${NC}"
echo -e ""
echo -e "3. 访问地址:"
echo -e "   ${YELLOW}前端:${NC} http://47.108.249.242:3000"
echo -e "   ${YELLOW}后端API:${NC} http://47.108.249.242:5000"
echo -e "   ${YELLOW}健康检查:${NC} http://47.108.249.242:5000/health"
echo -e ""
echo -e "4. 防火墙设置 (如需要):"
echo -e "   ${YELLOW}sudo ufw allow 3000${NC}"
echo -e "   ${YELLOW}sudo ufw allow 5000${NC}"

echo -e "\n${GREEN}✨ 部署脚本执行完成！${NC}"
