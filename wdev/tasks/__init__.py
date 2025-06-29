from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from ..hosts import Host

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
        self.hosts: List[Host] = []

    def set_next_success(self, task: 'Task') -> 'Task':
        """设置任务成功后的下一个任务"""
        self.next_success = task
        return task

    def set_next_failure(self, task: 'Task') -> 'Task':
        """设置任务失败后的下一个任务"""
        self.next_failure = task
        return task

    def add_host(self, host: Host):
        """添加任务执行的目标主机"""
        self.hosts.append(host)

    @abstractmethod
    def execute(self) -> TaskResult:
        """执行任务"""
        pass

class ShellTask(Task):
    """Shell命令任务"""
    def __init__(self, name: str, command: str, description: str = ""):
        super().__init__(name, description)
        self.command = command

    def execute(self) -> TaskResult:
        all_output = []
        all_errors = []
        success = True

        for host in self.hosts:
            exit_code, output, error = host.execute_command(self.command)
            if exit_code != 0:
                success = False
                all_errors.append(f"Host {host.name}: {error}")
            all_output.append(f"Host {host.name}: {output}")

        return TaskResult(
            success=success,
            output="\n".join(all_output),
            error="\n".join(all_errors)
        )

class PythonTask(Task):
    """Python可调用对象任务"""
    def __init__(self, name: str, callable_obj, description: str = "", **kwargs):
        super().__init__(name, description)
        self.callable_obj = callable_obj
        self.kwargs = kwargs

    def execute(self) -> TaskResult:
        try:
            result = self.callable_obj(**self.kwargs)
            return TaskResult(success=True, output=str(result))
        except Exception as e:
            return TaskResult(success=False, output="", error=str(e)) 