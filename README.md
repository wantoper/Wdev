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
from wdev.workflow import Workflow
from wdev.hosts import SSHHost
from wdev.tasks import ShellTask
from wdev.notifications import EmailNotifier

# 创建工作流
workflow = Workflow("deploy_app")

# 添加主机
host = SSHHost("example.com", "user", "password")

# 创建任务
deploy_task = ShellTask("deploy", "docker-compose up -d")

# 添加通知
notifier = EmailNotifier("admin@example.com")

# 配置工作流
workflow.add_host(host)
workflow.add_task(deploy_task)
workflow.add_notifier(notifier)

# 执行工作流
workflow.execute()
```

## 项目结构

```
wdev/
├── __init__.py
├── hosts/          # 主机管理模块
├── tasks/          # 任务模块
├── notifications/  # 通知模块
└── workflow/       # 工作流模块
```

## 许可证

MIT 