from wdev.workflow import Workflow
from wdev.hosts import SSHHost, LocalHost
from wdev.tasks import ShellTask, PythonTask
from wdev.notifications import EmailNotifier, ConsoleNotifier
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    # 创建工作流
    workflow = Workflow("服务部署和监控")

    # 创建主机
    local_host = LocalHost()
    remote_host = SSHHost(
        hostname="example.com",
        username=os.getenv("SSH_USER"),
        password=os.getenv("SSH_PASSWORD")
    )

    # 创建任务
    check_disk = ShellTask("检查磁盘空间", "df -h")
    deploy_service = ShellTask("部署服务", "docker-compose up -d")
    check_service = ShellTask("检查服务状态", "docker ps")
    notify_error = ShellTask("发送错误日志", "tail -n 50 /var/log/error.log")

    # 创建通知器
    console_notifier = ConsoleNotifier()
    email_notifier = EmailNotifier(
        recipients=os.getenv("NOTIFY_EMAIL"),
        smtp_host=os.getenv("SMTP_HOST"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER"),
        smtp_password=os.getenv("SMTP_PASSWORD")
    )

    # 使用流式接口构建工作流
    (workflow.add_task(check_disk, [local_host, remote_host])
     .set_next_success(deploy_service)
     .set_next_success(check_service)
     .set_next_failure(notify_error))

    workflow.add_notifier(email_notifier)
    workflow.add_notifier(console_notifier)

    # 执行工作流
    success = workflow.execute()
    print(f"工作流执行{'成功' if success else '失败'}")

if __name__ == "__main__":
    main() 