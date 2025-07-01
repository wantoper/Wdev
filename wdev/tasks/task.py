from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from wdev.hosts import Host

class TaskResult:
    """任务执行结果"""
    def __init__(self, success: bool, output: str, error: str = "", data: Dict[str, Any] = None):
        self.success = success
        self.output = output
        self.error = error
        self.data = data or {}

class Task(ABC):
    """任务基类"""
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.next_success: Optional[Task] = None
        self.next_failure: Optional[Task] = None

    def set_next_success(self, task: 'Task') -> 'Task':
        """设置任务成功后的下一个任务"""
        self.next_success = task
        return self

    def set_next_failure(self, task: 'Task') -> 'Task':
        """设置任务失败后的下一个任务"""
        self.next_failure = task
        return self

    @abstractmethod
    def execute(self,host: Host) -> TaskResult:
        """执行任务"""
        pass