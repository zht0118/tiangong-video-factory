from faster_whisper import WhisperModel
import os

print("军师禀报：正在启动 Faster-Whisper 引擎...")

# 1. 加载本地模型 (不再联网下载)
# 指定刚才下载好的路径
model_path = "/root/models/faster-whisper-base"
model = WhisperModel(model_path, device="cpu", compute_type="int8") 

print("军师禀报：正在聆听视频音频，请稍候...")

# 2. 转录视频
# beam_size=5 可以提高准确率
segments, info = model.transcribe("/root/final_video.mp4", language="zh", beam_size=5)

print(f"检测到的语言: {info.language} (置信度: {info.language_probability:.2f})")

# 3. 生成 SRT 字幕文件
output_path = "/root/output_sub.srt"
with open(output_path, "w", encoding="utf-8") as f:
    for i, segment in enumerate(segments, start=1):
        # 格式化时间
        start_time = segment.start
        end_time = segment.end
        
        def format_time(seconds):
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millisecs = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

        f.write(f"{i}\n")
        f.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
        f.write(f"{segment.text.strip()}\n\n")

print(f"军师禀报：字幕文件 {output_path} 已生成完毕！")
