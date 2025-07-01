# WDev - 运维脚本开发框架

WDev 是一个强大而灵活的 Python 运维自动化框架，专注于简化运维工作流程的开发和管理。它提供了丰富的功能来处理主机操作、任务执行和通知管理，让运维工作更加高效和可控。

## ✨ 主要特性

- 🖥️ **多样化的主机管理**
  - 支持 SSH 远程主机操作
  - 支持本地主机操作
  - 灵活的主机配置管理

- 📋 **强大的任务系统**
  - Shell 命令任务支持
  - Python 脚本任务支持
  - 任务链式调用
  - 任务成功/失败处理机制

- 🔔 **可扩展的通知系统**
  - 控制台输出通知
  - 邮件通知支持
  - 自定义通知器扩展

- 🔄 **工作流管理**
  - 简单直观的工作流定义
  - 任务依赖关系管理
  - 工作流执行状态追踪

## 📦 安装要求

- Python 3.7+
- 依赖包：
  ```bash
  paramiko>=2.7.2    # SSH 连接支持
  pyyaml>=6.0.1      # YAML 配置文件支持
  python-dotenv>=0.19.0  # 环境变量管理
  schedule>=1.2.0    # 任务调度
  PrettyTable>=0.2.1 # 表格输出美化
  ```

## 🚀 快速开始

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 基础示例：
   ```python
   from wdev.workflow import SimpleWorkflow
   from wdev.hosts import SSHHost
   from wdev.tasks import ShellTask
   from wdev.notifiers import ConsoleNotifier

   # 创建工作流
   workflow = SimpleWorkflow("服务检查", "检查远程服务器状态")

   # 配置远程主机
   host = SSHHost(
       hostname="192.168.1.100",
       username="admin",
       password="your_password"
   )

   # 创建任务
   check_disk = ShellTask("检查磁盘", "df -h")
   check_memory = ShellTask("检查内存", "free -h")

   # 配置工作流
   (workflow
       .add_host(host)
       .add_task(check_disk)
       .add_task(check_memory)
       .add_notifier(ConsoleNotifier()))

   # 执行工作流
   workflow.execute()
   ```

## 📁 项目结构

```
wdev/
├── __init__.py
├── hosts/          # 主机管理模块
│   ├── ssh.py     # SSH 主机实现
│   └── local.py   # 本地主机实现
├── tasks/          # 任务模块
│   ├── shell.py   # Shell 任务
│   └── python.py  # Python 任务
├── notifiers/      # 通知模块
│   ├── console.py # 控制台通知
│   └── email.py   # 邮件通知
└── workflow/       # 工作流模块
    └── simple.py  # 简单工作流实现
```

## 🔧 高级用法

### 任务链式调用
```python
task = (ShellTask("主任务", "main_command")
        .set_next_success(ShellTask("成功后执行", "success_command"))
        .set_next_failure(ShellTask("失败后执行", "failure_command")))
```

### 自定义通知器
```python
from wdev.notifiers import BaseNotifier

class CustomNotifier(BaseNotifier):
    def notify(self, message):
        # 实现自定义通知逻辑
        pass
```

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 📮 联系方式

- 作者：Wantoper
- GitHub：[WantoperBlog/WDev](https://github.com/WantoperBlog/WDev) 