#!/bin/bash

# ==========================================
# 【军师·终极修复版】视频合成脚本
# 修复：ffprobe缺失检测、Display报错、路径容错
# ==========================================

# --- 0. 环境自检 (新增) ---
if ! command -v ffmpeg &> /dev/null; then
    echo ">>> [致命错误] 找不到 ffmpeg！请先执行: sudo apt install ffmpeg"
    exit 1
fi
if ! command -v ffprobe &> /dev/null; then
    echo ">>> [致命错误] 找不到 ffprobe！它是获取时长的关键。请执行: sudo apt install ffmpeg"
    exit 1
fi

# 强制关闭图形界面依赖，防止 "unable to open display"
export DISPLAY=:0 

# --- 1. 接收参数 ---
AUDIO_FILE="$1"
shift
IMAGE_FILES=("$@")

OUTPUT_DIR="/root/output"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="${OUTPUT_DIR}/video_${TIMESTAMP}.mp4"
TEMP_IMG_DIR="/tmp/video_factory_imgs"

echo ">>> [启动] 视频合成引擎..."
echo ">>> [音频] $AUDIO_FILE"
echo ">>> [图片数量] ${#IMAGE_FILES[@]}"

# 检查文件是否存在
if [ ! -f "$AUDIO_FILE" ]; then
    echo ">>> [错误] 找不到音频文件: $AUDIO_FILE"
    exit 1
fi

# 清理并创建临时目录
rm -rf "$TEMP_IMG_DIR"
mkdir -p "$TEMP_IMG_DIR"
mkdir -p "$OUTPUT_DIR"

# --- 2. 预处理图片 (统一转为 jpg) ---
echo ">>> [处理] 正在标准化图片格式..."
for i in "${!IMAGE_FILES[@]}"; do
    src="${IMAGE_FILES[$i]}"
    dst="${TEMP_IMG_DIR}/img_${i}.jpg"
    if [ -f "$src" ]; then
        # 增加 -nostdin 防止卡住
        ffmpeg -y -nostdin -i "$src" -q:v 2 "$dst" 2>/dev/null
    else
        echo ">>> [警告] 图片丢失: $src"
    fi
done

# --- 3. 获取音频时长 (核心修复点) ---
echo ">>> [计算] 正在分析音频时长..."
# 使用 ffprobe 获取秒数
DURATION=$(ffprobe -i "$AUDIO_FILE" -show_entries format=duration -v quiet -of csv="p=0")

# 简单的清洗，防止取到空值
if [ -z "$DURATION" ]; then
    echo ">>> [错误] ffprobe 未能获取时长，默认按 5 秒处理"
    DURATION=5
fi

# 取整 (Shell 不支持浮点运算，这里做个简单处理)
DURATION_INT=$(awk "BEGIN {printf \"%d\", $DURATION}") 
if [ "$DURATION_INT" -lt 1 ]; then DURATION_INT=5; fi

echo ">>> [数据] 音频总长: ${DURATION}秒 (取整: ${DURATION_INT})"

# --- 4. 计算每张图片的停留时间 ---
IMG_COUNT=${#IMAGE_FILES[@]}
if [ $IMG_COUNT -eq 0 ]; then
    echo ">>> [错误] 没有图片可供合成！"
    exit 1
fi

# 计算单张时长
PER_IMG_DURATION=$(awk "BEGIN {printf \"%.2f\", $DURATION / $IMG_COUNT}")
echo ">>> [数据] 每张图片展示: ${PER_IMG_DURATION}秒"

# --- 5. 构建 FFmpeg 列表文件 ---
LIST_FILE="${TEMP_IMG_DIR}/list.txt"
> "$LIST_FILE"

for i in "${!IMAGE_FILES[@]}"; do
    # 确保文件存在再写入列表
    if [ -f "${TEMP_IMG_DIR}/img_${i}.jpg" ]; then
        echo "file '${TEMP_IMG_DIR}/img_${i}.jpg'" >> "$LIST_FILE"
        echo "duration ${PER_IMG_DURATION}" >> "$LIST_FILE"
    fi
done
# 最后一张图必须重复一次，否则 concat 模式下最后一张会一闪而过或报错
if [ -f "${TEMP_IMG_DIR}/img_$((IMG_COUNT-1)).jpg" ]; then
    echo "file '${TEMP_IMG_DIR}/img_$((IMG_COUNT-1)).jpg'" >> "$LIST_FILE"
fi

# --- 6. 执行合成 (增加 -nostdin) ---
echo ">>> [渲染] 正在合成视频 (这可能需要一点时间)..."

ffmpeg -y -nostdin \
    -f concat -safe 0 -i "$LIST_FILE" \
    -i "$AUDIO_FILE" \
    -c:v libx264 -pix_fmt yuv420p -r 25 \
    -c:a aac -shortest \
    -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,fade=t=in:st=0:d=0.5,fade=t=out:st=${DURATION_INT}-0.5:d=0.5" \
    "$OUTPUT_FILE"

RET=$?

if [ $RET -eq 0 ] && [ -f "$OUTPUT_FILE" ]; then
    FILE_SIZE=$(stat -c%s "$OUTPUT_FILE")
    if [ "$FILE_SIZE" -gt 1000 ]; then
        echo "SUCCESS: $OUTPUT_FILE"
    else
        echo "FFMPEG_ERROR: 文件生成但过小 (可能为坏文件)"
        exit 1
    fi
else
    echo "FFMPEG_ERROR: 返回码 $RET"
    exit 1
fi