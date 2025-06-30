from wdev.workflow.advanced import AdvancedWorkflow
from wdev.hosts import SSHHost, LocalHost
from wdev.tasks import ShellTask, PythonTask
from wdev.notifications import EmailNotifier, ConsoleNotifier
import os
import time
from dotenv import load_dotenv

load_dotenv()

def check_website(url="http://example.com"):
    """示例Python任务：检查网站可用性"""
    import requests
    try:
        response = requests.get(url)
        return f"网站状态码: {response.status_code}"
    except Exception as e:
        raise Exception(f"网站检查失败: {str(e)}")

def main():
    # 创建高级工作流（最多4个并行任务）
    workflow = AdvancedWorkflow("监控工作流", "系统和服务监控", max_workers=4)

    # 创建主机
    local_host = LocalHost()
    remote_host = SSHHost(
        hostname="example.com",
        username=os.getenv("SSH_USER"),
        password=os.getenv("SSH_PASSWORD")
    )

    # 创建通知器
    console_notifier = ConsoleNotifier()
    email_notifier = EmailNotifier(
        recipients=os.getenv("NOTIFY_EMAIL"),
        smtp_host=os.getenv("SMTP_HOST"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER"),
        smtp_password=os.getenv("SMTP_PASSWORD")
    )

    # 创建任务
    disk_check = ShellTask("磁盘检查", "df -h")
    memory_check = ShellTask("内存检查", "free -h")
    process_check = ShellTask("进程检查", "ps aux | grep python")
    website_check = PythonTask("网站检查", check_website)
    backup_task = ShellTask("数据备份", "tar -czf /backup/data_$(date +%Y%m%d).tar.gz /data")

    # 配置工作流
    (workflow.add_host(local_host)
             .add_host(remote_host)
             .add_notifier(console_notifier)
             .add_notifier(email_notifier))

    # 添加定时任务
    # 每5分钟执行一次的任务
    workflow.add_scheduled_task(disk_check, 'interval', minutes=5)
    workflow.add_scheduled_task(memory_check, 'interval', minutes=5)
    workflow.add_scheduled_task(process_check, 'interval', minutes=5)
    workflow.add_scheduled_task(website_check, 'interval', minutes=5)

    # 每天凌晨2点执行的备份任务
    workflow.add_scheduled_task(backup_task, 'daily', hour=2, minute=0)

    try:
        print("启动后台工作流...")
        # 启动定时任务
        workflow.start()

        # 立即执行一次所有任务（并行执行）
        print("首次执行所有任务...")
        success = workflow.execute()
        print(f"首次执行{'成功' if success else '失败'}")

        # 保持程序运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n停止工作流...")
        workflow.stop()
        print("工作流已停止")

if __name__ == "__main__":
    main() 