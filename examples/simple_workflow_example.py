from wdev.workflow import SimpleWorkflow
from wdev.hosts import SSHHost, LocalHost
from wdev.tasks import ShellTask
from wdev.notifiers import EmailNotifier, ConsoleNotifier
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    # 创建简单工作流
    workflow = SimpleWorkflow("部署工作流", "用于部署和检查服务状态")
    console_notifier = ConsoleNotifier()

    remote_host = SSHHost(hostname="192.168.69.136", username="root", password="")

    init_task = ShellTask("初始化","rm -rf /root/test1")

    task_1 = (ShellTask("创建文件夹1", "mkdir /root/test1")
                .set_next_success(ShellTask("创建文件夹2","mkdir /root/test1/test2"))
                .set_next_failure(ShellTask("删除文件夹1", "rm -rf /root/test1")))

    # 创建任务
    check_disk = (ShellTask("检查磁盘空间", "df -h")
                  .set_next_success(task_1))

    # 配置工作流
    (workflow.add_host(remote_host)
            .add_task(init_task)
            .add_task(check_disk)
            .add_notifier(console_notifier))

    # 执行工作流（只执行一次）
    success = workflow.execute()
    print(f"工作流执行{'成功' if success else '失败'}")
    for item in workflow.task_track.items():
        print(item)



if __name__ == "__main__":
    main() 