#!/bin/bash

echo "🛑 停止乐队管理系统服务..."

# 停止后端
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm backend.pid
    else
        echo "后端服务已停止"
        rm -f backend.pid
    fi
else
    echo "未找到后端PID文件，尝试按端口停止..."
    pkill -f "app_production.py"
fi

# 停止前端
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm frontend.pid
    else
        echo "前端服务已停止"
        rm -f frontend.pid
    fi
else
    echo "未找到前端PID文件，尝试按端口停止..."
    pkill -f "vite preview"
fi

# 额外清理：按端口杀死进程
echo "清理端口占用..."
lsof -ti:5000 | xargs -r kill -9 2>/dev/null
lsof -ti:3000 | xargs -r kill -9 2>/dev/null

echo "✅ 服务已停止"
