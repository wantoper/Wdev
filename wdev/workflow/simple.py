from .workflow import Workflow
from ..hosts import Host
from ..tasks import Task


class TaskNode:
    def __init__(self, task: Task,host: Host):
        self.task = task
        self.host = host
        self.result = None
        self.status = "未执行"
        self.next_success = None
        self.next_failure = None

    def gender_message(self):
        """获取任务执行结果的消息"""
        if self.result:
            self.message = f"""
任务: {self.task.name}
主机: {self.host.name}
状态: {self.status}
输出:
{self.result.output}
    """
            if self.result.error:
                self.message += f"\n错误:\n{self.result.error}"

    def execute(self):
        """执行任务"""
        self.result = self.task.execute(self.host)
        if self.result.success:
            self.status = "成功"
        else:
            self.status = "失败"
        self.gender_message()
        return self.result

    @classmethod
    def create(self, task: Task, host: Host):
        """创建一个新的任务节点"""
        if not isinstance(task, Task):
            return None
        return TaskNode(task, host)

class SimpleWorkflow(Workflow):
    """简单工作流类，按顺序执行一次所有任务"""
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self.task_track = {}

    def print_task_routes(self):
        """以树状结构打印任务执行路径，任务名称带颜色显示状态（不依赖第三方库）"""
        COLOR_GREEN = '\033[92m'
        COLOR_RED = '\033[91m'
        COLOR_YELLOW = '\033[93m'
        COLOR_RESET = '\033[0m'

        STATUS_COLORS = {
            "成功": COLOR_GREEN,
            "失败": COLOR_RED,
            "未执行": COLOR_YELLOW
        }

        # 遍历每个主机的任务跟踪记录
        for host_name, nodes in self.task_track.items():
            print(f"\n主机: {host_name}")
            # 处理该主机上的每个主任务树
            for root_node in nodes:
                # 使用栈实现非递归深度优先遍历
                stack = []
                # 每个元素包含：节点、深度、父节点前缀、是否为最后一个兄弟节点、分支标签
                stack.append((root_node, 0, "", True, ""))

                while stack:
                    node, depth, parent_prefix, is_last, branch_label = stack.pop()

                    # 确定连接符样式
                    if depth == 0:  # 根节点
                        connector = ""
                    else:
                        connector = "└── " if is_last else "└── "

                    # 组装节点显示信息
                    node_info = node.task.name + branch_label
                    color = STATUS_COLORS.get(node.status, COLOR_RESET)
                    print(f"{parent_prefix}{connector}{color}{node_info}{COLOR_RESET}")

                    # 准备子节点（成功分支和失败分支）
                    children = []
                    if node.next_success:
                        children.append((node.next_success, f"[{node.next_success.status}] "))
                    if node.next_failure:
                        children.append((node.next_failure, f"[{node.next_failure.status}] "))

                    # 反转子节点顺序以确保正确的处理顺序（成功分支先处理）
                    children = children[::-1]

                    # 生成子节点的缩进前缀
                    new_parent_prefix = parent_prefix + ("   " if is_last else "│   ")

                    # 将子节点压入栈中
                    for i, (child, label) in enumerate(children):
                        # 当前子节点是否是父节点的最后一个子节点
                        is_last_child = (i == len(children) - 1)
                        stack.append((child, depth + 1, new_parent_prefix, is_last_child, label))

    def run_task(self, task: Task,host: Host):
        #递归运行
        if not task:
            return None
        task_node = TaskNode(task, host)
        result = task_node.execute()

        if result.success:
            task_node.next_success = self.run_task(task.next_success, host)
            task_node.next_failure = TaskNode.create(task.next_failure, host)
        else:
            task_node.next_success = TaskNode.create(task.next_success, host)
            task_node.next_failure = self.run_task(task.next_failure, host)
        return task_node

    def execute(self) -> bool:
        """执行工作流中的所有任务一次"""
        if not self.tasks:
            raise ValueError("工作流中没有任务")
        if not self.hosts:
            raise ValueError("工作流中没有主机")

        overall_success = True
        # 对每个主机执行所有任务
        for host in self.hosts:
            for main_task in self.tasks:
                node = self.run_task(main_task, host)
                self.task_track.setdefault(host.name, []).append(node)

        return overall_success