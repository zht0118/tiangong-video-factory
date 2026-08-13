#!/bin/bash

echo "=========================================="
echo "   【天工】视频工厂 - 一键重启脚本 v1.0   "
echo "=========================================="

# 第一步：清理旧进程
echo ">>> 正在清理旧进程..."
# 查找所有包含 video_app.py 的 python 进程并强制杀掉
PIDS=$(ps -ef | grep video_app.py | grep -v grep | awk '{print $2}')
if [ -z "$PIDS" ]; then
    echo "    [OK] 没有发现正在运行的旧进程。"
else
    echo "    [!] 发现旧进程 PID: $PIDS，正在强制终止..."
    kill -9 $PIDS
    sleep 2
    echo "    [OK] 旧进程已清理。"
fi

# 第二步：检查关键文件是否存在
echo ">>> 正在检查核心文件..."
if [ ! -f "/root/video_app.py" ]; then
    echo "    [ERROR] 找不到 /root/video_app.py！请确认代码已写入。"
    exit 1
fi
echo "    [OK] 核心代码文件存在。"

# 第三步：启动新服务
echo ">>> 正在启动服务 (端口 8502)..."
nohup streamlit run /root/video_app.py --server.port=8502 --server.address=0.0.0.0 > /root/streamlit.log 2>&1 &

# 等待 3 秒让服务初始化
sleep 3

# 第四步：验证结果
echo ">>> 正在验证启动状态..."
NEW_PID=$(ps -ef | grep video_app.py | grep -v grep | awk '{print $2}')

if [ -n "$NEW_PID" ]; then
    echo "=========================================="
    echo "    🎉 启动成功！"
    echo "    进程 PID: $NEW_PID"
    echo "    访问地址: http://您的服务器IP:8502"
    echo "=========================================="
else
    echo "=========================================="
    echo "    💥 启动失败！请查看下方错误日志："
    echo "------------------------------------------"
    tail -n 20 /root/streamlit.log
    echo "=========================================="
fi
