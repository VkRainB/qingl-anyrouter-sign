#!/bin/bash

# AnyRouter 青龙自动签到脚本安装配置脚本
# 使用方法: bash install.sh

echo "🚀 开始安装 AnyRouter 青龙自动签到脚本..."

# 检查是否在青龙环境中
if [ ! -d "/ql" ]; then
    echo "❌ 错误: 未检测到青龙面板环境 (/ql 目录不存在)"
    echo "请在青龙面板容器中运行此脚本"
    exit 1
fi

# 创建脚本目录
mkdir -p /ql/scripts/anyrouter

# 复制脚本文件
echo "📁 复制脚本文件..."
cp anyrouter_checkin.py /ql/scripts/anyrouter/
cp ql_notify.py /ql/scripts/anyrouter/
cp requirements.txt /ql/scripts/anyrouter/

# 安装Python依赖
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt

# 检查是否已安装playwright
if ! command -v playwright &> /dev/null; then
    echo "🎭 安装Playwright..."
    playwright install chromium
    
    # 安装系统依赖
    echo "🔧 安装系统依赖..."
    apt-get update > /dev/null 2>&1
    apt-get install -y \
        libglib2.0-0 libnss3 libnspr4 libxss1 libdrm2 \
        libgtk-3-0 libasound2 libxcomposite1 libxdamage1 \
        libxrandr2 libatk1.0-0 libcups2 libatspi2.0-0 > /dev/null 2>&1
    
    echo "✅ Playwright 安装完成"
else
    echo "✅ Playwright 已安装"
fi

# 创建定时任务
echo "⏰ 配置定时任务..."

# 检查是否已存在任务
TASK_EXISTS=$(grep -c "anyrouter_checkin.py" /ql/db/crontab.db 2>/dev/null || echo "0")

if [ "$TASK_EXISTS" -eq "0" ]; then
    # 添加定时任务 (每天上午8点执行)
    echo "INSERT INTO crontab (name, command, schedule, timestamp, status) VALUES ('AnyRouter自动签到', 'python3 /ql/scripts/anyrouter/anyrouter_checkin.py', '0 8 * * *', $(date +%s), 1);" | sqlite3 /ql/db/crontab.db
    echo "✅ 定时任务已添加 (每天上午8点执行)"
else
    echo "✅ 定时任务已存在，跳过创建"
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "📋 接下来需要手动配置："
echo "1. 在青龙面板「环境变量」中添加 ANYROUTER_ACCOUNTS"
echo "2. (可选) 配置通知相关环境变量"
echo "3. 在「定时任务」中启用 'AnyRouter自动签到' 任务"
echo ""
echo "📚 详细配置说明请查看 README.md"
echo ""
echo "🔍 安装位置:"
echo "   - 主脚本: /ql/scripts/anyrouter/anyrouter_checkin.py"
echo "   - 通知模块: /ql/scripts/anyrouter/ql_notify.py"
echo "   - 依赖文件: /ql/scripts/anyrouter/requirements.txt"
echo ""
echo "✨ 享受自动签到吧！"