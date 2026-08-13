#!/bin/bash
#
echo ">>> [军师] 正在初始化云端环境..."
#
## 1. 安装必要的软件 (Python3, pip, git)
#yum install -y python3 python3-pip git || apt-get install -y python3 python3-pip git
#
## 2. 安装 Streamlit 和 阿里云SDK
#pip3 install streamlit alibabacloud_tea_openapi alibabacloud_tea_util
#
## 3. 创建军师的Web界面代码 (app.py)
#cat > app.py << 'EOF'
#import streamlit as st
#import os
#
#st.set_page_config(page_title="碳硅共生体·军师", page_icon="🧠")
#
#st.title("🧠 碳硅共生体 · 军师指挥舱")
#st.markdown("---")
#st.write("欢迎千总！系统运行状态：**正常**")
#st.write("当前环境：**阿里云 ECS**")
#
## 模拟读取密钥（实际业务中用于调用API）
#access_key_id = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID')
#if access_key_id:
#    st.success(f"✅ 密钥已加载 (ID: {access_key_id[:10]}...)")
#    else:
#        st.error("❌ 未检测到密钥，请检查环境变量配置")
#
#        st.markdown("---")
#        st.caption("Powered by Qianwen & Alibaba Cloud")
#        EOF
#
#        # 4. 【关键】配置环境变量（将您的密钥注入系统）
#        # ⚠️ 千总请注意：请务必将下方的 '您的AccessKeyID' 和 '您的AccessKeySecret' 替换为您本地保存的真实字符串！
#        echo "export ALIBABA_CLOUD_ACCESS_KEY_ID='LTAI5t9kSB9z7Mh6tXrZjTCH'" >> /etc/profile
#        echo "export ALIBABA_CLOUD_ACCESS_KEY_SECRET='zsmMqXngXTPAcwrtbMAbcmOspxtJavS'" >> /etc/profile
#
#        # 让环境变量立即生效
#        source /etc/profile
#
#        # 5. 启动军师 (后台运行，端口8501)
#        echo ">>> [军师] 正在启动 Web 交互舱..."
#        nohup streamlit run app.py --server.port=8501 --server.address=0.0.0.0 > junshi.log 2>&1 &
#
#        echo ">>> [军师] 部署完成！请访问 http://您的服务器公网IP:8501"
