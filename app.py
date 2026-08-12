import streamlit as st
import os
import time
import subprocess
from dashscope import ImageSynthesis
import dashscope

# --- 1. 基础配置 ---
WATCH_FOLDER = "/root/watch_folder"
OUTPUT_VIDEO_FOLDER = "/root/output"
SCRIPT_PATH = "/root/auto_maker.sh"

# 确保文件夹存在
os.makedirs(WATCH_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_VIDEO_FOLDER, exist_ok=True)

st.set_page_config(page_title="硅基视频工厂", layout="wide")
st.title("🎬 硅基视频工厂 - 中央控制台")

# --- 2. 侧边栏设置 ---
with st.sidebar:
    st.header("⚙️ 核心设置")
    api_key = st.text_input("请输入 DashScope API Key:", type="password")
    if api_key:
        dashscope.api_key = api_key
        st.success("密钥已就绪")
    
    st.divider()
    st.info("当前素材目录: " + WATCH_FOLDER)

# --- 3. 主功能区 ---
tab1, tab2 = st.tabs(["🎨 AI 绘图车间", "🎞️ 视频合成车间"])

# 【Tab 1: 生成图片】
with tab1:
    prompt = st.text_area("请输入画面描述 (Prompt):", "A futuristic city with flying cars, cyberpunk style, 8k resolution")
    col1, col2 = st.columns([1, 4])
    
    if col1.button("🚀 开始生成图片", type="primary"):
        if not api_key:
            st.error("请先在左侧输入 API Key！")
        else:
            with st.spinner("AI 正在绘画中，请稍候..."):
                try:
                    rsp = ImageSynthesis.call(model="wanx-v1",
                                              prompt=prompt,
                                              n=4, # 一次生成4张
                                              size='1024*1024')
                    results = rsp.output.results
                    file_paths = []
                    for i, result in enumerate(results):
                        # 保存到本地
                        save_path = os.path.join(WATCH_FOLDER, f"{int(time.time())}_{i}.png")
                        # 这里简化处理，实际需下载图片，此处假设直接展示URL或下载逻辑
                        # 为演示方便，这里仅做逻辑展示，实际需配合 requests 下载
                        import requests
                        img_data = requests.get(result.url).content
                        with open(save_path, 'wb') as handler:
                            handler.write(img_data)
                        file_paths.append(save_path)
                    
                    st.success(f"成功生成 {len(file_paths)} 张图片！已存入素材库。")
                    # 展示生成的图片
                    cols = st.columns(4)
                    for idx, path in enumerate(file_paths):
                        cols[idx].image(path)
                        
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")

# 【Tab 2: 合成视频】
with tab2:
    st.header("🎞️ 自动化视频合成")
    st.write("点击下方按钮，系统将自动把【绘图车间】产出的图片合成带特效的长视频。")
    
    if st.button("🔥 立即启动合成引擎", type="primary", use_container_width=True):
        if not os.path.exists(SCRIPT_PATH):
            st.error("未找到合成脚本 auto_maker.sh，请先部署脚本！")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🚀 正在启动 FFmpeg 引擎...")
            progress_bar.progress(10)
            
            try:
                # 执行 Shell 脚本
                process = subprocess.Popen(
                    ['bash', SCRIPT_PATH],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # 模拟进度（因为 FFmpeg 标准输出解析较复杂，这里做简化演示）
                for i in range(90):
                    time.sleep(0.5) # 假装在忙碌
                    progress_bar.progress(10 + i)
                    status_text.text(f"⚙️ 正在渲染帧... {i}%")
                    
                    # 检查进程是否结束
                    if process.poll() is not None:
                        break
                
                process.wait()
                
                if process.returncode == 0:
                    progress_bar.progress(100)
                    status_text.text("✅ 合成完成！")
                    st.success("视频已生成！请去服务器 /root/output 目录查看。")
                    
                    # 尝试自动播放最新视频
                    files = sorted([os.path.join(OUTPUT_VIDEO_FOLDER, f) for f in os.listdir(OUTPUT_VIDEO_FOLDER) if f.endswith('.mp4')])
                    if files:
                        st.video(files[-1])
                else:
                    error_msg = process.stderr.read()
                    st.error(f"合成失败，请检查脚本日志。\n错误信息: {error_msg}")
                    
            except Exception as e:
                st.error(f"执行出错: {str(e)}")

st.divider()
st.caption("Silicon Video Factory v2.0 | Powered by Streamlit & FFmpeg")
