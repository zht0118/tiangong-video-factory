import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def send_aliyun_mail(to_email, subject, content):
    # ================= 配置区（请修改这里） =================
    smtp_server = "smtpdm.aliyun.com"   # 阿里云 SMTP 服务器
    smtp_port = 465                     # 推荐使用 465 端口 (SSL加密)
    sender = "notify@taogeonline.cn"    # 您的发信地址
    password = "Zht306309TAOGE" # 注意：不是阿里云登录密码！
    # =====================================================

    # 1. 构造邮件内容
    message = MIMEMultipart()
    message['From'] = Header("AI助手", 'utf-8')  # 发件人昵称
    message['To'] = Header("主公", 'utf-8')      # 收件人昵称
    message['Subject'] = Header(subject, 'utf-8')
    
    # 邮件正文（支持 HTML）
    html_content = f"""
    <p>主公您好：</p>
    <p>{content}</p>
    <br>
    <p style="color:gray; font-size:12px;">此邮件由 AI 自动发送，请勿直接回复。</p>
    """
    message.attach(MIMEText(html_content, 'html', 'utf-8'))

    try:
        # 2. 连接服务器并发送
        # 使用 SMTP_SSL 协议，对应 465 端口
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender, password)
        server.sendmail(sender, [to_email], message.as_string())
        server.quit()
        print(f"✅ 发送成功！邮件已发送至：{to_email}")
        return True
    except Exception as e:
        print(f"❌ 发送失败：{str(e)}")
        return False

# ================= 测试运行 =================
if __name__ == "__main__":
    # 测试发送给您的 Outlook 邮箱
    send_aliyun_mail(
        to_email="taoge0118@outlook.com", 
        subject="来自 AI 的第一封战报", 
        content="恭喜主公！域名验证通过，Python 接口调通，万事大吉！"
    )