#!/bin/bash
# 【天工】视频工厂 - v32.0 (硬盘稳定版)

# 修改工作目录到 /root 下，避开 /tmp 内存盘
WORK_DIR="/root"
INPUT_DIR="/root/watch_folder"
OUTPUT_DIR="/root/output"
RAW_DIR="/root/raw_assets"
LOG_FILE="/var/log/tiangong.log"
BG_PNG="$RAW_DIR/bg.png"

# 1. 强制创建所有目录
mkdir -p "$INPUT_DIR" "$OUTPUT_DIR" "$RAW_DIR"

# 2. 如果背景图不存在，自动生成
if [ ! -f "$BG_PNG" ]; then
    echo "[INFO] 背景图不存在，正在生成..."
    ffmpeg -f lavfi -i color=c=black:s=1280x720:d=1 -frames:v 1 "$BG_PNG" -y
    if [ $? -eq 0 ]; then
        echo "[SUCCESS] 背景图生成成功: $BG_PNG"
    else
        echo "[ERROR] 背景图生成失败！"
        exit 1
    fi
fi

echo "[INFO] 环境检查完毕，准备开始任务..."
# 这里可以接您原来的业务逻辑
