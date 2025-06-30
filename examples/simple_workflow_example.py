from wdev.workflow.simple import SimpleWorkflow
from wdev.hosts import SSHHost, LocalHost
from wdev.tasks import ShellTask
from wdev.notifications import EmailNotifier, ConsoleNotifier
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    # 创建简单工作流
    workflow = SimpleWorkflow("部署工作流", "用于部署和检查服务状态")

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
    backup_data = ShellTask("备份数据", "tar -czf backup.tar.gz /data")

    # 设置任务链
    check_disk.set_next_success(deploy_service)
    deploy_service.set_next_success(check_service)
    deploy_service.set_next_failure(backup_data)  # 如果部署失败，执行备份

    # 创建通知器
    console_notifier = ConsoleNotifier()
    email_notifier = EmailNotifier(
        recipients=os.getenv("NOTIFY_EMAIL"),
        smtp_host=os.getenv("SMTP_HOST"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER"),
        smtp_password=os.getenv("SMTP_PASSWORD")
    )

    # 配置工作流
    (workflow.add_host(local_host)
              .add_host(remote_host)
              .add_task(check_disk)
              .add_task(deploy_service)
              .add_task(check_service)
              .add_task(backup_data)
              .add_notifier(console_notifier)
              .add_notifier(email_notifier))

    # 执行工作流（只执行一次）
    success = workflow.execute()
    print(f"工作流执行{'成功' if success else '失败'}")

if __name__ == "__main__":
    main() 