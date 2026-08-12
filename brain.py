import os
import subprocess

class SmartBrain:
    def __init__(self):
        self.status = "待命"
        print("军师报告：智能大脑已启动！")

    def listen(self, command_text):
        """
        听指令：分析主公说的话
        """
        self.status = "思考中..."
        print(f"收到指令：{command_text}")
        
        # 简单的关键词匹配（以后我们会换成真正的大模型AI）
        if "部署" in command_text or "安装" in command_text:
            return self.action_deploy_saas()
        elif "邮件" in command_text or "发信" in command_text:
            return "功能开发中：邮件模块尚未装配"
        else:
            return "主公，军师暂未听懂此指令，请尝试说'部署SaaS'"

    def action_deploy_saas(self):
        """
        SaaS部署手：自动执行部署命令
        """
        try:
            log = "正在启动SaaS部署程序...\n"
            # 这里写具体的部署逻辑，比如检查Docker
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                log += f"检测到Docker环境：{result.stdout}"
                log += "环境正常，准备开始部署..."
                return log
            else:
                log += "警告：未检测到Docker，正在尝试安装..."
                # 这里可以放自动安装Docker的脚本
                return log
        except Exception as e:
            return f"部署出错：{str(e)}"

# 测试一下
if __name__ == "__main__":
    ai = SmartBrain()
    print(ai.listen("帮我部署一下SaaS"))
