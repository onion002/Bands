#!/bin/bash

echo "📊 检查乐队管理系统服务状态..."

# 检查后端
echo "🔍 后端服务 (端口 5000):"
if curl -s http://47.108.249.242:5000/health > /dev/null; then
    echo "  ✅ 后端服务正常运行"
    curl -s http://47.108.249.242:5000/health | python3 -m json.tool 2>/dev/null || echo "  响应格式异常"
else
    echo "  ❌ 后端服务无响应"
fi

# 检查前端
echo ""
echo "🔍 前端服务 (端口 3000):"
if curl -s -o /dev/null -w "%{http_code}" http://47.108.249.242:3000 | grep -q "200"; then
    echo "  ✅ 前端服务正常运行"
else
    echo "  ❌ 前端服务无响应"
fi

# 检查进程
echo ""
echo "🔍 进程状态:"
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "  ✅ 后端进程运行中 (PID: $BACKEND_PID)"
    else
        echo "  ❌ 后端进程已停止"
    fi
else
    echo "  ⚠️  未找到后端PID文件"
fi

if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "  ✅ 前端进程运行中 (PID: $FRONTEND_PID)"
    else
        echo "  ❌ 前端进程已停止"
    fi
else
    echo "  ⚠️  未找到前端PID文件"
fi

# 检查端口占用
echo ""
echo "🔍 端口占用:"
if lsof -i:5000 > /dev/null 2>&1; then
    echo "  ✅ 端口 5000 被占用"
    lsof -i:5000 | head -2
else
    echo "  ❌ 端口 5000 未被占用"
fi

if lsof -i:3000 > /dev/null 2>&1; then
    echo "  ✅ 端口 3000 被占用"
    lsof -i:3000 | head -2
else
    echo "  ❌ 端口 3000 未被占用"
fi

# 检查日志
echo ""
echo "🔍 最近日志:"
if [ -f "backend.log" ]; then
    echo "  📄 后端日志 (最后5行):"
    tail -5 backend.log | sed 's/^/    /'
else
    echo "  ⚠️  未找到后端日志文件"
fi

if [ -f "frontend.log" ]; then
    echo "  📄 前端日志 (最后5行):"
    tail -5 frontend.log | sed 's/^/    /'
else
    echo "  ⚠️  未找到前端日志文件"
fi

echo ""
echo "📋 访问地址:"
echo "  🌐 前端: http://47.108.249.242:3000"
echo "  🔧 后端API: http://47.108.249.242:5000"
echo "  ❤️  健康检查: http://47.108.249.242:5000/health"
