#!/bin/bash

echo "🚀 Flask Admin Pro - Vue 前端开发启动脚本"
echo "========================================"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js"
    exit 1
fi

echo "✅ Node.js 版本：$(node -v)"
echo "✅ npm 版本：$(npm -v)"

# 进入项目目录
cd "$(dirname "$0")/ui"

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 首次运行，正在安装依赖..."
    npm install
fi

# 启动开发服务器
echo ""
echo "🌐 启动 Vue 开发服务器..."
echo "📍 访问地址：http://localhost:3000/admin/"
echo ""
echo "💡 提示：请确保 Flask 后端已在 5000 端口运行"
echo ""

npm run dev
