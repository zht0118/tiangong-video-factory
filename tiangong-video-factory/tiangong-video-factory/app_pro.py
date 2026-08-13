import streamlit as st
import psutil
import time
import plotly.graph_objects as go
from streamlit.components.v1 import html

# 1. 页面设置：宽屏模式
st.set_page_config(page_title="终极指挥仓", layout="wide", page_icon="🚀")

# 2. 注入 CSS 魔法：变身赛博朋克风
st.markdown("""
<style>
    /* 全局背景设为深空黑 */
    .stApp {
        background-color: #0b0c15;
        color: #00f3ff;
    }
    /* 标题发光效果 */
    h1, h2, h3 {
        color: #00f3ff !important;
        text-shadow: 0 0 10px #00f3ff;
        font-family: 'Courier New', monospace;
    }
    /* 指标卡片样式 */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #00f3ff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
    }
    /* 隐藏默认的页脚 */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 3. 顶部标题栏
st.title("🛸 碳硅共创 · 终极指挥仓 v2.0")
st.markdown("---")

# 4. 布局：三列布局 (左-中-右)
col1, col2, col3 = st.columns([1, 2, 1])

# --- 左侧：系统状态 ---
with col1:
    st.subheader("📡 系统遥测")
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    
    # 使用 Plotly 画一个仪表盘
    fig_cpu = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = cpu,
        title = {'text': "CPU 负载", 'font': {'color': '#00f3ff'}},
        gauge = {'axis': {'range': [None, 100], 'tickcolor': "#00f3ff"},
                 'bar': {'color': "#00f3ff"},
                 'bgcolor': "white",
                 'borderwidth': 2,
                 'bordercolor': "#00f3ff"}))
    fig_cpu.update_layout(paper_bgcolor = "rgba(0,0,0,0)", plot_bgcolor = "rgba(0,0,0,0)", font={'color': "#00f3ff"})
    st.plotly_chart(fig_cpu, use_container_width=True)

# --- 中间：核心拓扑图 (模拟截图一的中间部分) ---
with col2:
    st.subheader("🕸️ AI+跨境黑客松巅峰赛 · 实时拓扑")
    
    # 模拟一个网络拓扑图
    fig_net = go.Figure(data=[go.Scatter(
        x=[1, 2, 3, 4, 2, 3], 
        y=[2, 3, 2, 3, 1, 4],
        mode='markers+text',
        text=["主控", "节点A", "节点B", "节点C", "AI核心", "数据库"],
        marker=dict(size=20, color='#00f3ff', line=dict(width=2, color='white'))
    )])
    
    # 添加连线
    fig_net.add_trace(go.Scatter(
        x=[1, 2, 3, 4, 2, 3, 1], 
        y=[2, 3, 2, 3, 1, 4, 2],
        mode='lines',
        line=dict(color='#00f3ff', width=1, dash='dot')
    ))
    
    fig_net.update_layout(
        paper_bgcolor = "rgba(0,0,0,0)", 
        plot_bgcolor = "rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=500
    )
    st.plotly_chart(fig_net, use_container_width=True)

# --- 右侧：实时日志 ---
with col3:
    st.subheader("📜 军团聊天室")
    st.info("系统初始化完成...")
    st.success("连接至阿里云节点...成功")
    st.warning("检测到外部访问...")
    if cpu > 50:
        st.error("警告：CPU 负载过高！")
    else:
        st.text("系统运行平稳...")

