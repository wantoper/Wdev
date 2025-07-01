from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from wdev.tasks import Task, TaskResult
from wdev.hosts import Host
from wdev.notifiers import Notifier

class Workflow(ABC):
    """工作流基类，定义基本接口和共同功能"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.tasks: List[Task] = []
        self.notifiers: List[Notifier] = []
        self.task_results: Dict[str, TaskResult] = {}
        self.hosts: List[Host] = []

    def add_host(self, host: Host):
        """添加主机"""
        self.hosts.append(host)
        return self

    def add_task(self, task: Task):
        """添加任务"""
        self.tasks.append(task)
        return self

    def add_notifier(self, notifier: Notifier):
        """添加通知器"""
        self.notifiers.append(notifier)
        return self

    def notify_all(self, subject: str, message: str):
        """向所有通知器发送通知"""
        for notifier in self.notifiers:
            notifier.notify(subject, message)

    @abstractmethod
    def print_task_routes(self) -> str:
        """返回日志"""
        pass

    @abstractmethod
    def execute(self) -> bool:
        """执行工作流"""
        pass 