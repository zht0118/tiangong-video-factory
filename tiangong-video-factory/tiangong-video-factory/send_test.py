import smtplib
from email.mime.text import MIMEText
from email.header import Header

# ================= 配置区域 (请在此处填入您的信息) =================
smtp_server = "smtpdm.aliyun.com"       # 阿里云服务器
smtp_port = 465                         # SSL端口
sender_email = "notify@taogeonline.cn"  # 发件人
smtp_password = "Taoge2026Mail" # ⚠️ 别忘了填这个！
receiver_email = "taoge0118@qq.com"# 收件人 (先发给自已测试)
# =================================================================

def send_email():
    # 1. 设置邮件内容
    message = MIMEText("主公，恭喜您！这是来自阿里云的第一封测试邮件，配置已成功！", 'plain', 'utf-8')
    message['From'] = Header("阿里云测试", 'utf-8')
    message['To'] = Header("主公", 'utf-8')
    subject = "【测试】邮件推送配置成功"
    message['Subject'] = Header(subject, 'utf-8')

    try:
        # 2. 连接服务器并发送
        # 使用 SMTP_SSL 是因为我们用了 465 端口
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, smtp_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("✅ 发送成功！请去 Outlook 查收。")
        
    except smtplib.SMTPException as e:
        print(f"❌ 发送失败: {e}")
    finally:
        server.quit()

if __name__ == "__main__":
    send_email()