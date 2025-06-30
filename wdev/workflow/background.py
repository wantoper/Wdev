import time
from typing import Optional
from threading import Thread
from ..tasks import Task
from ..hosts import Host
from ..notifications import Notifier

class WorkflowNode:
    """工作流节点类，将单个任务、主机和通知器组合在一起"""
    
    def __init__(self, name: str, task: Task, host: Host, notifier: Notifier, interval: int = 60):
        self.name = name
        self.task = task
        self.host = host
        self.notifier = notifier
        self.interval = interval  # 执行间隔（秒）
        self.is_running = False
        self._thread: Optional[Thread] = None

    def execute_once(self):
        """执行一次任务"""
        result = self.task.execute(self.host)
        status = "成功" if result.success else "失败"
        message = f"""
节点: {self.name}
任务: {self.task.name}
主机: {self.host.name}
状态: {status}
输出:
{result.output}
"""
        if result.error:
            message += f"\n错误:\n{result.error}"

        self.notifier.notify(
            f"节点 {self.name} 执行{status}",
            message
        )
        return result.success

    def _run_loop(self):
        """后台运行循环"""
        while self.is_running:
            self.execute_once()
            time.sleep(self.interval)

    def start(self):
        """开始后台运行"""
        if not self.is_running:
            self.is_running = True
            self._thread = Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def stop(self):
        """停止后台运行"""
        self.is_running = False
        if self._thread:
            self._thread.join()
            self._thread = None

class BackgroundWorkflow:
    """后台工作流类，管理多个工作流节点"""
    
    def __init__(self, name: str):
        self.name = name
        self.nodes = {}

    def add_node(self, node: WorkflowNode):
        """添加工作流节点"""
        self.nodes[node.name] = node
        return self

    def start_all(self):
        """启动所有节点"""
        for node in self.nodes.values():
            node.start()

    def stop_all(self):
        """停止所有节点"""
        for node in self.nodes.values():
            node.stop()

    def get_node(self, name: str) -> Optional[WorkflowNode]:
        """获取指定名称的节点"""
        return self.nodes.get(name) 