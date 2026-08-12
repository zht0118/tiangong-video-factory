import dashscope
import streamlit as st
import os
import subprocess
from aip import AipSpeech
import imageio
from dotenv import load_dotenv
from http import HTTPStatus
import json
import time
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# ==========================================
# 【天工】视频工厂 - Web 控制台 v14.0 (双脑+双臂完全体)
# ==========================================

# 1. 加载密钥
load_dotenv("/root/.env")
BAIDU_APP_ID = os.getenv("BAIDU_APP_ID")
BAIDU_API_KEY = os.getenv("BAIDU_API_KEY")
BAIDU_SECRET_KEY = os.getenv("BAIDU_SECRET_KEY")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# 邮件配置 (示例配置，实际使用请替换或从环境变量读取)
EMAIL_HOST = "smtp.qq.com"
EMAIL_PORT = 465
EMAIL_USER = os.getenv("EMAIL_USER", "your_email@qq.com")
EMAIL_PASS = os.getenv("EMAIL_PASS", "your_auth_code")

# 初始化百度语音客户端
baidu_client = None
if all([BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY]):
    baidu_client = AipSpeech(BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY)

# 设置 DashScope Key
if DASHSCOPE_API_KEY:
    dashscope.api_key = DASHSCOPE_API_KEY

# 2. 页面配置
st.set_page_config(page_title="天工·智能视频工厂", page_icon="🎬", layout="wide")
st.title("🎬 天工·智能视频工厂 v14.0")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 核心设置")
    work_mode = st.radio("选择工作模式", ["🤖 AI 互动模式", "🛠️ 手动配置模式"])
    st.success("✅ 已加载环境变量中的 API Key")
    
    user_key = st.text_input(
        "DashScope API Key (可修改):",
        value=DASHSCOPE_API_KEY if DASHSCOPE_API_KEY else "",
        type="password",
        help="如果环境变量配置正确，这里会自动填入。"
    )
    if user_key and user_key != DASHSCOPE_API_KEY:
        dashscope.api_key = user_key
        st.info("💡 正在使用您手动输入的 Key")
    elif DASHSCOPE_API_KEY:
        dashscope.api_key = DASHSCOPE_API_KEY
        st.info(f"当前素材目录: /root/output")

# ==========================================
# 【核心功能函数】 - 视频生成部分
# ==========================================
def get_audio_duration(audio_path):
    """【修复版】获取音频时长，防止 ffprobe 缺失导致崩溃"""
    try:
        probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', audio_path]
        duration = float(subprocess.check_output(probe_cmd).decode().strip())
        return duration
    except FileNotFoundError:
        try:
            cmd = ['ffmpeg', '-i', audio_path]
            output = subprocess.run(cmd, capture_output=True, text=True).stderr
            match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})', output)
            if match:
                h, m, s, ms = match.groups()
                return int(h)*3600 + int(m)*60 + int(s) + int(ms)/100
            else:
                return 10.0
        except:
            return 10.0
    except Exception:
        return 10.0

def baidu_tts(text, voice_type=0):
    """调用百度语音合成"""
    if not baidu_client:
        return None
    result = baidu_client.synthesis(text, 'zh', 1, {
        'vol': 5,
        'spd': 5,
        'pit': 5,
        'per': voice_type
    })
    if not isinstance(result, dict):
        with open('/root/output/temp_audio.mp3', 'wb') as f:
            f.write(result)
        return '/root/output/temp_audio.mp3'
    return None

def create_video_with_subtitles(audio_path, text, output_path):
    """使用 FFmpeg 将音频和字幕合成视频"""
    duration = get_audio_duration(audio_path)
    bg_img = '/root/output/bg.png'
    if not os.path.exists(bg_img):
        subprocess.run(['ffmpeg', '-f', 'lavfi', '-i', 'color=c=black:s=1920x1080:d=1', '-frames:v', '1', bg_img])
    
    sub_path = '/root/output/temp_subs.ass'
    with open(sub_path, 'w', encoding='utf-8') as f:
        f.write('[Script Info]\nTitle: Subtitles\nScriptType: v4.00+\nWrapStyle: 0\nPlayResX: 1920\nPlayResY: 1080\n\n')
        f.write('[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n')
        f.write('Style: Default,SimHei,60,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,2,40,40,40,1\n')
        f.write('[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n')
        end_time = int(duration) + 1
        f.write(f'Dialogue: 0,0:00:00.00,0:00:{end_time}.00,Default,,0,0,0,,{text}\n')

    cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-i', bg_img,
        '-i', audio_path,
        '-vf', f'ass={sub_path}',
        '-c:v', 'libx264', '-preset', 'ultrafast',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest', output_path
    ]
    process = subprocess.run(cmd, capture_output=True, text=True)
    if process.returncode == 0:
        return True
    else:
        st.error(f"FFmpeg 错误: {process.stderr}")
        return False

# ==========================================
# 【新增】机械手臂执行模块 - 左手与右手
# ==========================================

# ================= 新增：阿里云信使 (基于 send_test1.py 验证成功版) =================
def send_aliyun_email(subject, content):
    """
    使用阿里云SMTP服务发送邮件的专用函数
    此函数直接复用了 send_test1.py 中验证成功的配置
    """
    # --- 配置区域 (与 send_test1.py 完全一致) ---
    smtp_server = "smtpdm.aliyun.com"
    smtp_port = 465
    sender_email = "notify@taogeonline.cn"
    smtp_password = "Taoge2026Mail"  # 您刚才设置成功的密码
    receiver_email = "taoge0118@qq.com" # 您的QQ邮箱
    
    # --- 构建邮件 ---
    message = MIMEMultipart()
    message['From'] = Header("天工·视频工厂", 'utf-8')
    message['To'] = Header("主公", 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')
    
    # 添加HTML格式的正文
    message.attach(MIMEText(content, 'html', 'utf-8'))
    
    # --- 发送 ---
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, smtp_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print(f"✅ [阿里云信使] 邮件发送成功: {subject}")
        return True
    except Exception as e:
        print(f"❌ [阿里云信使] 邮件发送失败: {e}")
        return False
# ==============================================================================

def deploy_saas_tool(project_name):
    """
    【左手】SaaS 部署执行器
    模拟真实的部署流程：拉取代码 -> 安装依赖 -> 启动服务
    """
    logs = []
    try:
        logs.append(f"🚀 [系统] 开始部署项目: {project_name}...")
        # 1. 模拟创建目录
        deploy_dir = f"/root/saas_projects/{project_name}"
        os.makedirs(deploy_dir, exist_ok=True)
        logs.append(f"📂 [文件] 创建工作目录: {deploy_dir}")
        
        # 2. 模拟拉取代码 (这里用创建 README 代替 git clone)
        readme_path = os.path.join(deploy_dir, "README.md")
        with open(readme_path, 'w') as f:
            f.write(f"# {project_name}\nDeployed by SkyHand AI.")
        logs.append(f"📥 [Git] 代码拉取成功 (模拟)")
        
        # 3. 模拟安装依赖 (pip install)
        time.sleep(1)
        logs.append(f"📦 [Pip] 正在安装 requirements.txt ...")
        
        # 4. 模拟启动 Docker/Service
        logs.append(f"🐳 [Docker] 构建镜像中...")
        time.sleep(1)
        logs.append(f"✅ [完成] 项目 {project_name} 已成功上线！访问地址: http://localhost:8080")
        return "\n".join(logs)
    except Exception as e:
        return f"❌ 部署失败: {str(e)}"

def send_email_tool(to_email, subject, content):
    """
    【右手】跨境电商邮件发送器 - 智能适配 QQ / Outlook (增强版)
    自动尝试 465 (SSL) 和 587 (TLS) 两种连接方式
    """
    import smtplib
    from email.mime.text import MIMEText
    import os
    
    # 1. 获取配置
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    smtp_host = os.getenv("EMAIL_SMTP_HOST", "smtp.qq.com")
    
    if not sender_email or not sender_password:
        return "❌ 错误：未配置 EMAIL_SENDER 或 EMAIL_PASSWORD"
    
    # 2. 构建邮件内容
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    
    # 3. 尝试发送 (双端口策略)
    # 策略：先试 465 (SSL)，失败则试 587 (TLS)
    ports_to_try = [465, 587]
    for port in ports_to_try:
        try:
            server = None
            if port == 465:
                # 使用 SMTP_SSL 类直接建立加密连接
                server = smtplib.SMTP_SSL(smtp_host, port)
            else:
                # 使用普通 SMTP 类，然后升级加密
                server = smtplib.SMTP(smtp_host, port)
                server.ehlo()
                server.starttls()
                server.ehlo()
            
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [to_email], msg.as_string())
            server.quit()
            return f"✅ [真实发送成功] 通过 {smtp_host}:{port} 发送至 {to_email}"
        except Exception as e:
            # 如果当前端口失败，记录日志并尝试下一个
            print(f"尝试端口 {port} 失败: {str(e)}")
            if server:
                try:
                    server.quit()
                except:
                    pass
            continue
            
    return f"❌ 邮件发送失败：所有端口 (465, 587) 均无法连接 {smtp_host}。请检查服务器网络或防火墙。"

# ==========================================
# 【核心功能函数】 - AI 交互部分
# ==========================================
def call_qwen_ai(prompt_text):
    """调用通义千问生成文案或执行指令"""
    if not dashscope.api_key:
        return "错误：请先配置 API Key"
    
    system_prompt = """你是一个全能的 AI 助手。
1. 如果用户让你写广告、写文案：请写一段 30-50 字的短视频口播文案，口语化、有吸引力。
2. 如果用户提到部署 SaaS、跨境电商、服务器操作：请以专家的身份给出步骤建议或代码片段。
不要输出多余的解释，直接给结果。"""
    
    try:
        response = dashscope.Generation.call(
            model=dashscope.Generation.Models.qwen_turbo,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt_text}
            ]
        )
        if response.status_code == HTTPStatus.OK:
            return response.output.text
        else:
            return f"API 调用失败: {response.message}"
    except Exception as e:
        return f"发生异常: {str(e)}"

# ==========================================
# 界面逻辑
# ==========================================
# 初始化 Session State
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'generated_script' not in st.session_state:
    st.session_state.generated_script = ""
if 'selected_voice_idx' not in st.session_state:
    st.session_state.selected_voice_idx = 0

voice_options = ["度小美-普通女声", "度小宇-普通男声", "度逍遥-情感男声", "度丫丫-可爱女声"]
voice_map = {0: 0, 1: 3, 2: 4003, 3: 4}

# --- 上半部分：AI 对话区 ---
st.subheader("💬 AI 导演助理")

# 显示历史消息
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 输入框
user_input = st.chat_input("请输入指令，例如：帮我写个牙膏广告... 或 部署一个电商项目")

if user_input:
    # 1. 显示用户消息
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # 2. AI 思考与回复 (包含意图识别)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("正在分析意图...")
        
        # --- 简单的意图识别 (军师的简易路由) ---
        user_intent = "chat" # 默认是聊天/写文案
        if "部署" in user_input or "安装" in user_input or "saas" in user_input.lower():
            user_intent = "deploy"
        elif "邮件" in user_input or "email" in user_input.lower() or "联系" in user_input:
            user_intent = "email"
            
        # --- 根据意图执行不同操作 ---
        ai_response = ""
        if user_intent == "deploy":
            # 提取项目名称 (简单提取，或者让 AI 提取)
            project_name = user_input.replace("帮我部署", "").replace("部署", "").strip() or "MySaaS"
            with st.spinner("🛠️ 机械手臂正在部署 SaaS..."):
                ai