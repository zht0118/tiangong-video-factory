import streamlit as st
import os
from aip import AipSpeech
import subprocess
from datetime import datetime

# ==========================================
# 【天工】视频工厂 - Web 控制台 v7.0 (百度AI真人语音版)
# ==========================================

# 【主公请在此处填入您的百度AI密钥】
APP_ID = '124119086'
API_KEY = '5xfLiZTpfAYAYsUVoekkD8yH'
SECRET_KEY = '3MaQjDBRquCnymIRsSp8J2ZEshtkHSHJ'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

st.set_page_config(page_title="天工·视频工厂", page_icon="🎬", layout="wide")
st.title("🎬 天工·智能视频工厂 (Baidu AI Edition)")
st.markdown("---")

# 侧边栏配置
st.sidebar.header("⚙️ 参数配置")
video_text = st.sidebar.text_area("📝 视频文案", height=200, value="李总您好，这是为您生成的最新企业宣传片演示。我们的自动化视频工厂已经正式运转，效率提升了十倍。")

# 百度支持的音色选择
voice_type = st.sidebar.selectbox("🗣️ 选择音色", [
    ("度小美-普通女声", 0), 
    ("度小宇-普通男声", 1), 
    ("度逍遥-情感男声", 3), 
    ("度丫丫-情感女声", 4)
], format_func=lambda x: x[0])

# 主界面按钮
col1, col2 = st.columns([1, 2])

with col1:
    st.header("🚀 任务控制台")
    if st.button("🔴 开始生成视频", type="primary"):
        if not video_text.strip():
            st.error("文案不能为空！")
        else:
            try:
                # 1. 调用百度接口生成音频
                result = client.synthesis(video_text, 'zh', 1, {
                    'vol': 5,      # 音量
                    'spd': 5,      # 语速
                    'pit': 5,      # 音调
                    'per': voice_type[1] # 音色
                })
                
                if not isinstance(result, dict):
                    audio_path = "output_audio.mp3"
                    with open(audio_path, 'wb') as f:
                        f.write(result)
                    st.success(f"✅ 配音生成成功！时长: {len(result)/16000:.1f}秒")
                    
                    # 2. 生成视频 (这里假设您有ffmpeg，如果没有，我们之前已经装过了)
                    video_path = "final_video.mp4"
                    # 使用 ffmpeg 将音频转为视频（黑屏+音频）
                    cmd = [
                        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=1280x720:d=10', 
                        '-i', audio_path, 
                        '-shortest', '-c:v', 'libx264', '-c:a', 'aac', 
                        '-pix_fmt', 'yuv420p', video_path
                    ]
                    subprocess.run(cmd, check=True)
                    
                    st.success("✅ 视频生成成功！")
                else:
                    st.error(f"❌ 百度API报错: {result}")
                    
            except Exception as e:
                st.error(f"生成失败: {str(e)}")

with col2:
    st.header("🎬 成品展示区")
    if os.path.exists("final_video.mp4"):
        st.video("final_video.mp4")
    else:
        st.info("等待任务提交...")
