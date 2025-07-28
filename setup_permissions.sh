#!/bin/bash

echo "🔧 设置部署脚本权限..."

# 设置所有脚本的执行权限
chmod +x deploy.sh
chmod +x quick_deploy.sh
chmod +x stop_services.sh
chmod +x check_status.sh
chmod +x setup_permissions.sh

# 设置后端启动脚本权限
if [ -f "start_backend.sh" ]; then
    chmod +x start_backend.sh
fi

if [ -f "start_frontend.sh" ]; then
    chmod +x start_frontend.sh
fi

# 设置后端应用权限
chmod +x BandManager/app_production.py

echo "✅ 权限设置完成！"
echo ""
echo "📋 可用脚本："
echo "  ./deploy.sh          - 完整部署脚本"
echo "  ./quick_deploy.sh    - 快速启动服务"
echo "  ./stop_services.sh   - 停止所有服务"
echo "  ./check_status.sh    - 检查服务状态"
echo ""
echo "🚀 现在可以运行部署脚本了！"
