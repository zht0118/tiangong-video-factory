import streamlit as st
import os
import time
import subprocess
import requests
from dashscope import ImageSynthesis, Generation
from dashscope.audio.tts import SpeechSynthesizer
import dashscope
import re

# ==========================================
# 【配置区】
# ==========================================
# 建议在此处硬编码 Key，防止环境变量丢失导致服务中断
# 如果留空，则使用侧边栏输入
DASHSCOPE_API_KEY = "" 

WATCH_FOLDER = "/root/watch_folder"
OUTPUT_VIDEO_FOLDER = "/root/output"
SCRIPT_PATH = "/root/auto_maker.sh" # 指向上面的 Shell 脚本
TEMP_AUDIO = "/root/temp_audio.mp3" 

os.makedirs(WATCH_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_VIDEO_FOLDER, exist_ok=True)

st.set_page_config(page_title="硅基视频工厂", layout="wide")
st.title("🎬 硅基视频工厂 - 中央控制台")

# --- 侧边栏设置 ---
with st.sidebar:
    st.header("⚙️ 系统状态")
    
    # 优先使用代码里的 Key，如果没有，再让用户输
    current_key = DASHSCOPE_API_KEY or os.getenv("DASHSCOPE_API_KEY", "")
    
    api_key_input = st.text_input("DashScope API Key:", type="password", value=current_key)
    
    if api_key_input:
        dashscope.api_key = api_key_input
        st.success("✅ 密钥已加载")
    else:
        st.warning("⚠️ 请输入 API Key")

# --- 核心功能函数 ---

def generate_script(prompt):
    """调用通义千问写文案"""
    try:
        rsp = Generation.call(
            model="qwen-turbo",
            messages=[{'role': 'system', 'content': '你是一个广告文案专家。'},
                      {'role': 'user', 'content': f"请为'{prompt}'写一段30秒的短视频旁白文案，只要纯文本，不要标题，不要emoji。"}]
        )
        if rsp.status_code == 200:
            return rsp.output.text.strip()
        else:
            return None
    except Exception as e:
        return f"Error: {str(e)}"

def generate_audio(text):
    """调用 Sambert 生成语音"""
    if not text: return None
    try:
        audio = SpeechSynthesizer.call(
            model='sambert-zhichu-v1', 
            text=text,
            sample_rate=48000,
            format='mp3'
        )
        if audio.get_audio_data() is not None: 
            with open(TEMP_AUDIO, 'wb') as f:
                f.write(audio.get_audio_data())
            return TEMP_AUDIO
        else:
            return None
    except Exception as e:
        st.error(f"语音异常: {str(e)}")
        return None

def generate_images(topic):
    """生成图片并保存到 watch_folder"""
    clean_topic = re.sub(r'[^\w\s\u4e00-\u9fff]', '', topic)
    prompt = f"High quality commercial photography, {clean_topic}, cinematic lighting, 8k resolution, photorealistic."
    
    try:
        rsp = ImageSynthesis.call(model="wanx-v1", prompt=prompt, n=4, size='1024*1024')
        if rsp.status_code == 200:
            paths = []
            for i, res in enumerate(rsp.output.results):
                img_data = requests.get(res.url).content
                path = os.path.join(WATCH_FOLDER, f"{int(time.time())}_{i}.png")
                with open(path, 'wb') as f: f.write(img_data)
                paths.append(path)
            return paths
        else:
            st.error(f"绘图失败: {rsp.message}")
            return []
    except Exception as e:
        st.error(f"绘图异常: {str(e)}")
        return []

# --- 主界面逻辑 ---
tab1, tab2 = st.tabs(["🎨 AI 绘图车间", "🎞️ 视频合成车间"])

with tab1:
    st.header("AI 绘图")
    p = st.text_area("画面描述:", "A futuristic city...")
    if st.button("生成图片"):
        if not dashscope.api_key: st.error("无 Key"); st.stop()
        with st.spinner("绘画中..."):
            paths = generate_images(p)
            if paths:
                cols = st.columns(4)
                for i, path in enumerate(paths):
                    cols[i].image(path)
                st.success("图片已入库！")

with tab2:
    st.header("自动化视频合成 (智能版)")
    topic = st.text_input("请输入视频主题/广告词:", "30秒茶叶广告")
    
    if st.button("🔥 立即启动合成引擎", type="primary"):
        if not dashscope.api_key:
            st.error("请先在左侧配置 API Key！")
        else:
            with st.status("正在创作中...", expanded=True) as status:
                # 1. 写文案
                st.write("🧠 正在构思文案...")
                script_text = generate_script(topic)
                if not script_text or "Error" in script_text:
                    st.error(f"文案失败: {script_text}"); status.update(label="文案失败", state="error"); st.stop()
                st.info(f"📝 **生成的文案：**\n{script_text}")
                
                # 2. 生成语音
                st.write("🗣️ 正在录制旁白...")
                audio_path = generate_audio(script_text)
                if not audio_path:
                    st.error("语音失败"); status.update(label="语音失败", state="error"); st.stop()
                st.success("✅ 语音已就绪")
                
                # 3. 生成图片
                st.write("🖼️ 正在定制配图...")
                image_paths = generate_images(topic)
                if not image_paths:
                    st.error("图片生成失败"); status.update(label="配图失败", state="error"); st.stop()
                
                st.success(f"✅ 已生成 {len(image_paths)} 张关于 '{topic}' 的图片")
                
                # 4. 调用 Shell 脚本合成 (关键：显式传递文件列表)
                st.write("🎬 正在渲染视频 (调用 auto_maker.sh)...")
                
                # 构造命令：bash script.sh audio.mp3 img1.jpg img2.jpg ...
                cmd_list = ["bash", SCRIPT_PATH, audio_path] + image_paths
                
                try:
                    # 使用 subprocess.run 阻塞等待，确保合成完再往下走
                    process = subprocess.run(cmd_list, capture_output=True, text=True, timeout=300)
                    
                    # 检查 Shell 脚本的返回值
                    if process.returncode == 0 and "SUCCESS" in process.stdout:
                        status.update(label="🎉 合成完成！", state="complete", expanded=False)
                        st.success("视频已生成！请在服务器 /root/output 查看。")
                        
                        # 展示最新视频
                        files = sorted([os.path.join(OUTPUT_VIDEO_FOLDER, f) for f in os.listdir(OUTPUT_VIDEO_FOLDER) if f.endswith('.mp4')])
                        if files: 
                            st.video(files[-1])
                    else:
                        status.update(label="❌ 渲染失败", state="error", expanded=True)
                        st.error(f"脚本报错:\n{process.stderr}\n{process.stdout}")
                        
                except subprocess.TimeoutExpired:
                    st.error("⏳ 渲染超时 (超过5分钟)，请检查服务器负载。")
                except Exception as e:
                    st.error(f"执行出错: {str(e)}")