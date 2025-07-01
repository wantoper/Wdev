from wdev.workflow import SimpleWorkflow
from wdev.hosts import SSHHost, LocalHost, Host
from wdev.tasks import ShellTask, PythonTask, Task, TaskResult
from wdev.notifiers import EmailNotifier, ConsoleNotifier


def main():
    # 创建简单工作流
    workflow = SimpleWorkflow("example1", "最简单的工作流示例")
    #执行结果 输出到控制台
    console_notifier = ConsoleNotifier()

    remote_host = SSHHost(hostname="192.168.108.130", username="root", password="passwd")
    local_host = LocalHost()
    #创建一个普通的Shell命令任务
    task_0 = ShellTask("初始化","echo 'hello example1...'> /tmp/wdev.log")

    #创建一个任务流的Shell命令任务
    task_1 = ((ShellTask("检查nc安装状态", "nc -help")
              .set_next_success(ShellTask("发送数据到端口",'echo "Hello World" | nc 127.0.0.1 7777')))
              .set_next_failure(ShellTask("写出日志","echo '未安装nc...' > /tmp/nc_status.log")))

    # 配置工作流 host和task会按照顺序执行
    (workflow
            .add_host(remote_host)
            .add_host(local_host)
            .add_task(task_0)
            .add_task(task_1)
            .add_notifier(console_notifier))

    workflow.execute()

if __name__ == "__main__":
    main() 