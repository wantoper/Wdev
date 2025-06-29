from typing import List, Optional, Dict, Union
from ..tasks import Task, TaskResult
from ..hosts import Host
from ..notifications import Notifier
class Workflow:
    """工作流类，用于管理和执行任务链"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.tasks: List[Task] = []
        self.notifiers: List[Notifier] = []
        self.task_results: Dict[str, TaskResult] = {}
        self.hosts: List[Host] = []

    def add_host(self, host: Host):
        self.hosts.append(host)

    def add_task(self, task: Task, hosts: Union[Host, List[Host]]) -> Task:
        """添加一个新的任务流节点"""
        if isinstance(hosts, Host):
            hosts = [hosts]
        return task

    def add_notifier(self, notifier: Notifier) -> Notifier:
        """添加一个通知器"""
        self.notifiers.append(notifier)
        return notifier

    def notify_all(self, subject: str, message: str):
        """向所有通知器发送通知"""
        for notifier in self.notifiers:
            notifier.notify(subject, message)

    def execute(self) -> bool:
        """执行工作流"""
        if not self.tasks:
            raise ValueError("No tasks in workflow")

        overall_success = True
        for host in self.hosts:

            current = self.tasks[0]

            while current:
                # 执行当前任务
                result = current.execute(host)
                self.task_results[current.name] = result

                # 发送任务执行结果通知
                status = "成功" if result.success else "失败"
                message = f"""
任务: {current.name}
状态: {status}
输出:
{result.output}
"""
                if result.error:
                    message += f"\n错误:\n{result.error}"

                self.notify_all(
                    f"任务 {current.name} {status}",
                    message
                )

                # 确定下一个任务
                if result.success:
                    current = current.next_success
                    if not result.success:
                        overall_success = False
                else:
                    current = current.next_failure
                    overall_success = False

        return overall_success 