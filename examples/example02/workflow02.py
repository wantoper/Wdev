from wdev.workflow import SimpleWorkflow
from wdev.hosts import SSHHost, LocalHost, Host
from wdev.tasks import ShellTask, PythonTask, Task, TaskResult
from wdev.notifiers import ConsoleNotifier

from examples.example02.hosts import local_host,remote_host

"""
接口约定： callable_obj(task:Task,host: Host,**self.kwargs)
如果确定当前工作流的全部主机都为SSHHost 则可以写成 host:SSHHost 以获得更多的功能支持
```
callable_obj(task:Task,host: SSHHost,**self.kwargs)
host._get_client()               # 获取当前任务主机的paramiko.SSHClient对象
host._get_client().open_sftp()   # 获取当前任务主机的paramiko.SFTPClient对象
```
"""
def myfunc(task:Task,host: Host,param1)-> TaskResult:
    # 获取前一个任务的输出
    data = task.pre_task.task_results.output
    data = data.split("\n")
    frist_pid = data[0].split()[1]

    #可以根据需要 获取到当前的Host 执行命令
    host.execute_command("echo 'hello wdev'> /tmp/test1.out")
    # 传递参数给下一个任务
    resultdata = {
        "command":"echo 'kill -9 {}\n{}' > /tmp/test.out".format(frist_pid,param1),
    }

    task_result = TaskResult(success=True,data=resultdata)
    return task_result

# 创建简单工作流
workflow02 = SimpleWorkflow("example2", "学习PythonTask和ShellTask结合的小示例")
console_notifier = ConsoleNotifier()

init_task = ShellTask("初始化","echo 'hello example2...'> /tmp/wdev.log")

task_1 = (ShellTask("获取Python程序状态", "ps -def|grep python")
            .set_next_success(PythonTask("解析第一个python进程的PID", myfunc,param1="测试参数")
                              .set_next_success(ShellTask("执行命令").with_data_command("command"))) #with_data_command 运行前一个方法的task_results.data["command"]
            .set_next_failure(ShellTask("写出日志", "echo 'error'>/tmp/error.log")))

# 配置工作流
(workflow02.add_host(remote_host)
        .add_host(local_host)
        .add_task(init_task)
        .add_task(task_1)
        .add_notifier(console_notifier))

# workflow.execute()
