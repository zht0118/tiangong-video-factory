import streamlit as st
import subprocess
import os
import time

# 配置路径
WORK_DIR = "/tmp/tiangong_work"
INPUT_DIR = os.path.join(WORK_DIR, "input")
OUTPUT_DIR = os.path.join(WORK_DIR, "output")
LOG_FILE = "/var/log/tiangong.log"

# 确保目录存在
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.set_page_config(page_title="天工·视频工厂", layout="wide")
st.title("🎬 天工·智能视频工厂控制台")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 任务发布台")
    script_text = st.text_area("输入文案内容", height=200, placeholder="请输入您要生成视频的文案...")
    
    if st.button("🚀 立即生成视频", type="primary"):
        if not script_text:
            st.error("文案不能为空！")
        else:
            # 生成任务文件
            task_file = os.path.join(INPUT_DIR, f"task_{int(time.time())}.txt")
            with open(task_file, "w", encoding="utf-8") as f:
                f.write(script_text)
            
            st.success(f"任务已提交！文件：{os.path.basename(task_file)}")
            st.info("天工正在后台处理，请稍候刷新右侧查看...")

with col2:
    st.subheader("🎞️ 成品展示区")
    
    # 获取最新的视频文件
    videos = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.mp4')], reverse=True)
    
    if videos:
        latest_video = os.path.join(OUTPUT_DIR, videos[0])
        st.video(latest_video)
        
        with open(latest_video, "rb") as file:
            st.download_button(
                label="⬇️ 下载视频",
                data=file,
                file_name=videos[0],
                mime="video/mp4"
            )
    else:
        st.info("暂无成品，请在左侧发布任务。")

    st.markdown("---")
    st.subheader("📜 运行日志")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            logs = f.read()
        st.code(logs[-1000:], language="bash") # 显示最后1000字符
    else:
        st.caption("日志文件尚未生成...")
