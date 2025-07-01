from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from wdev.hosts import Host

class TaskResult:
    """任务执行结果"""
    def __init__(self, success: bool, output: str="", error: str = "", data: Dict[str, Any] = None):
        self.success = success
        self.output = output
        self.error = error
        self.data = data or {}

class Task(ABC):
    """任务基类"""
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.pre_task: Optional[Task] = None
        self.next_success: Optional[Task] = None
        self.next_failure: Optional[Task] = None
        self.task_results: Optional[TaskResult] = None

    def set_pre_task(self, task: 'Task') -> 'Task':
        """设置父任务
            后续可以在任务中通过 pre_task.task_results 获取上一个任务的 TaskResult
        """
        self.pre_task = task
        return self

    def set_next_success(self, next_task: 'Task') -> 'Task':
        """设置任务成功后的下一个任务"""
        next_task.set_pre_task(self)
        self.next_success = next_task
        return self

    def set_next_failure(self, next_task: 'Task') -> 'Task':
        """设置任务失败后的下一个任务"""
        next_task.set_pre_task(self)
        self.next_failure = next_task
        return self

    @abstractmethod
    def execute(self,host: Host) -> TaskResult:
        """执行任务"""
        pass