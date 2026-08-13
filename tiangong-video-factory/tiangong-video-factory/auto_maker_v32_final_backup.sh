#!/bin/bash
# 【天工】视频工厂 - v33.0 (有声字幕版)

# --- 1. 基础配置 ---
WORK_DIR="/root" # 统一使用 /root 目录
INPUT_DIR="$WORK_DIR/watch_folder"
OUTPUT_DIR="$WORK_DIR/output"
RAW_DIR="$WORK_DIR/raw"
LOG_FILE="/var/log/tiangong.log"
BG_PNG="$RAW_DIR/bg.png"

# API Key (建议从环境变量或参数传入，这里为演示直接写死或读取环境变量)
# 实际运行时，最好通过 app.py 传入，或者在这里配置
DASHSCOPE_API_KEY="sk-ws-H.ERHYPHM.87Yk.MEUCIEW_JD6R0hgTSfXoYKwVbNECw_vfEOeqTbdhKX8ApMLHAiEA363tvaX4HJkr_ikv_EKh5dHVP4WBN7lvnOty16dNAgw" # <--- 请替换为您的真实 Key，或者保持为空让 Python 传参

mkdir -p "$INPUT_DIR" "$OUTPUT_DIR" "$RAW_DIR"

echo "[INFO] === 开始 v33.0 自动化任务 ==="

# --- 2. 检查素材 ---
IMAGE_COUNT=$(ls -1 "$INPUT_DIR"/*.png 2>/dev/null | wc -l)
if [ "$IMAGE_COUNT" -eq 0 ]; then
    echo "[ERROR] 素材库为空！请先在网页端生成图片。"
    exit 1
fi
echo "[INFO] 发现 $IMAGE_COUNT 张图片素材。"

# --- 3. 获取 Prompt (用于生成语音和字幕) ---
# 简单策略：读取最新一张图片的文件名，或者读取一个 prompt.txt (如果有)
# 这里为了演示，我们假设 prompt 是固定的，或者您可以创建一个 prompt.txt 放在 input 目录
PROMPT_FILE="$INPUT_DIR/prompt.txt"
if [ -f "$PROMPT_FILE" ]; then
    PROMPT_TEXT=$(cat "$PROMPT_FILE")
else
    PROMPT_TEXT="Welcome to the Silicon Video Factory. This is an automated generated video."
    echo "$PROMPT_TEXT" > "$PROMPT_FILE"
fi
echo "[INFO] 当前文案: $PROMPT_TEXT"

# --- 4. 生成语音 (TTS) ---
AUDIO_FILE="$OUTPUT_DIR/audio.mp3"
echo "[INFO] 正在调用 CosyVoice 生成语音..."
# 注意：这里使用 python 调用 dashscope sdk，因为 shell 直接调 api 比较麻烦
python3 - <<EOF
import dashscope
from dashscope.audio.tts_v2 import *

dashscope.api_key = "$DASHSCOPE_API_KEY"

synthesizer = SpeechSynthesizer(
    model='cosyvoice-v1',
    voice='longxiaochun' 
)

audio = synthesizer.call(
    text='$PROMPT_TEXT',
    format='mp3'
)
if audio:
    with open('$AUDIO_FILE', 'wb') as f:
        f.write(audio)
    print("[SUCCESS] 语音生成成功")
else:
    print("[ERROR] 语音生成失败")
EOF

if [ ! -f "$AUDIO_FILE" ]; then
    echo "[WARN] 语音生成失败，将生成无声视频。"
fi

# --- 5. 生成字幕 (SRT) ---
SUBTITLE_FILE="$OUTPUT_DIR/subtitle.srt"
cat > "$SUBTITLE_FILE" <<EOF
1
00:00:00,000 --> 00:00:05,000
$PROMPT_TEXT
EOF
echo "[INFO] 字幕文件已生成。"

# --- 6. FFmpeg 合成视频 ---
OUTPUT_VIDEO="$OUTPUT_DIR/final_video_$(date +%s).mp4"
echo "[INFO] 正在合成最终视频..."

# 构建滤镜链：图片缩放 + 字幕烧录
# 注意：ffmpeg 烧录字幕需要 reencode，速度较慢
if [ -f "$AUDIO_FILE" ]; then
    ffmpeg -y \
        -framerate 0.5 -pattern_type glob -i "$INPUT_DIR/*.png" \
        -i "$AUDIO_FILE" \
        -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,subtitles=$SUBTITLE_FILE" \
        -c:v libx264 -pix_fmt yuv420p \
        -c:a aac -shortest \
        "$OUTPUT_VIDEO"
else
    ffmpeg -y \
        -framerate 0.5 -pattern_type glob -i "$INPUT_DIR/*.png" \
        -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,subtitles=$SUBTITLE_FILE" \
        -c:v libx264 -pix_fmt yuv420p \
        "$OUTPUT_VIDEO"
fi

if [ $? -eq 0 ]; then
    echo "[SUCCESS] 视频合成完成: $OUTPUT_VIDEO"
else
    echo "[ERROR] 视频合成失败！"
    exit 1
fi