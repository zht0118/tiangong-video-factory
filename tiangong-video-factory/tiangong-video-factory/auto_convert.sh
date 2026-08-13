#!/bin/bash

# --- 配置区域 (主公可根据需要修改) ---
WATCH_DIR="/root/watch_folder"   # 监控文件夹：请把视频传到这里
OUTPUT_DIR="/root/output"        # 成品文件夹：转好的 MP4 会放在这里
DONE_DIR="/root/done"            # 归档文件夹：处理完的原片移到这里
LOG_FILE="/root/convert.log"     # 日志文件
# ----------------------------------

# 初始化文件夹
mkdir -p "$WATCH_DIR" "$OUTPUT_DIR" "$DONE_DIR"

echo "[$(date)] 哨兵启动！正在监控: $WATCH_DIR ..." | tee -a "$LOG_FILE"

while true; do
    # 查找监控目录下的 avi, mov, mkv, flv 文件 (不区分大小写)
    find "$WATCH_DIR" -maxdepth 1 -type f \( -iname "*.avi" -o -iname "*.mov" -o -iname "*.mkv" -o -iname "*.flv" \) | while read -r filepath; do
        
        filename=$(basename "$filepath")
        # 去掉后缀名，准备生成新名字
        basename_no_ext="${filename%.*}"
        output_file="$OUTPUT_DIR/${basename_no_ext}.mp4"

        echo "[$(date)] 发现新目标: $filename，开始转码..." | tee -a "$LOG_FILE"
        
        # --- 核心转码指令 (开启 AVX2 加速) ---
        # -threads 0: 自动调用所有 CPU 核心
        # -preset fast: 牺牲一点点体积换取更快的速度
        # -crf 23: 标准画质
        ffmpeg -i "$filepath" -c:v libx264 -preset fast -crf 23 -threads 0 -c:a aac -b:a 128k "$output_file" -y >> "$LOG_FILE" 2>&1
        
        if [ $? -eq 0 ]; then
            echo "[$(date)] 成功: $filename -> ${basename_no_ext}.mp4" | tee -a "$LOG_FILE"
            # 转码成功，把原片移走，避免下次重复处理
            mv "$filepath" "$DONE_DIR/"
        else
            echo "[$(date)] 失败: $filename，请检查日志 $LOG_FILE" | tee -a "$LOG_FILE"
        fi
    done
    
    # 每 5 秒巡视一次
    sleep 5
done
