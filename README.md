# WDev - 运维脚本开发框架

WDev 是一个用于运维脚本开发的Python框架，提供了灵活的主机管理、任务执行和通知功能。

## 特性

- 支持SSH和本地主机操作
- 可扩展的任务系统（Shell任务和Python任务）
- 插件化的通知系统
- 灵活的工作流管理
- 任务链式调用支持

## 安装

```bash
pip install -r requirements.txt
```

## 使用示例

```python
from wdev.workflow import SimpleWorkflow
from wdev.hosts import SSHHost, LocalHost
from wdev.tasks import ShellTask
from wdev.notifiers import EmailNotifier, ConsoleNotifier

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
```

## 项目结构

```
wdev/
├── __init__.py
├── hosts/          # 主机管理模块
├── tasks/          # 任务模块
├── notifiers/      # 通知模块
└── workflow/       # 工作流模块
```

## 许可证

MIT 