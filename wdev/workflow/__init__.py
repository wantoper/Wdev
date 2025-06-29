from typing import List, Optional, Dict, Union
from ..tasks import Task, TaskResult
from ..hosts import Host
from ..notifications import Notifier

class FlowNode:
    """工作流节点，用于构建任务流"""
    def __init__(self, workflow: 'Workflow', task: Task, hosts: List[Host]):
        self.workflow = workflow
        self.task = task
        self.hosts = hosts
        for host in hosts:
            task.add_host(host)
        self.workflow.tasks.append(task)

    def set_next_success(self, task: Task, hosts: Optional[List[Host]] = None) -> 'FlowNode':
        """设置任务成功后的下一个任务"""
        hosts = hosts or self.hosts
        self.task.next_success = task
        return FlowNode(self.workflow, task, hosts)

    def set_next_failure(self, task: Task, hosts: Optional[List[Host]] = None) -> 'FlowNode':
        """设置任务失败后的下一个任务"""
        hosts = hosts or self.hosts
        self.task.next_failure = task
        return FlowNode(self.workflow, task, hosts)

    def add_notifier(self, notifier: Notifier) -> 'FlowNode':
        """添加通知器"""
        if notifier not in self.workflow.notifiers:
            self.workflow.notifiers.append(notifier)
        return self

    def end(self) -> 'Workflow':
        """结束流程定义，返回工作流实例"""
        return self.workflow

class Workflow:
    """工作流类，用于管理和执行任务链"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.tasks: List[Task] = []
        self.notifiers: List[Notifier] = []
        self.task_results: Dict[str, TaskResult] = {}

    def add_flow(self, task: Task, hosts: Union[Host, List[Host]]) -> FlowNode:
        """添加一个新的任务流节点"""
        if isinstance(hosts, Host):
            hosts = [hosts]
        return FlowNode(self, task, hosts)

    def notify_all(self, subject: str, message: str):
        """向所有通知器发送通知"""
        for notifier in self.notifiers:
            notifier.notify(subject, message)

    def execute(self) -> bool:
        """执行工作流"""
        if not self.tasks:
            raise ValueError("No tasks in workflow")

        overall_success = True
        current = self.tasks[0]

        while current:
            # 执行当前任务
            result = current.execute()
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