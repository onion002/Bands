#!/bin/bash

# 快速部署脚本 - 适用于已配置好环境的服务器
echo "🚀 快速部署乐队管理系统..."

# 设置环境变量
export FLASK_ENV=production
export API_BASE_URL=http://47.107.79.244:5000

# 后端启动
echo "🔧 启动后端服务..."
cd BandManager
source venv/bin/activate 2>/dev/null || echo "虚拟环境不存在，使用系统Python"
nohup python app_production.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "后端PID: $BACKEND_PID"
cd ..

# 等待后端启动
sleep 3

# 前端启动
echo "🔧 启动前端服务..."
cd band-manager-front
nohup npm run preview -- --host 0.0.0.0 --port 3000 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端PID: $FRONTEND_PID"
cd ..

# 保存PID到文件
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

echo "✅ 部署完成！"
echo "📋 服务信息:"
echo "   前端: http://47.107.79.244:3000"
echo "   后端: http://47.107.79.244:5000"
echo "   健康检查: http://47.107.79.244:5000/health"
echo ""
echo "📝 日志文件:"
echo "   后端日志: backend.log"
echo "   前端日志: frontend.log"
echo ""
echo "🛑 停止服务:"
echo "   ./stop_services.sh"
