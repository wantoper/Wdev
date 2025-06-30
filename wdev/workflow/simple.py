from typing import List
from .base import BaseWorkflow
from ..hosts import Host
from ..tasks import Task

class SimpleWorkflow(BaseWorkflow):
    """简单工作流类，按顺序执行一次所有任务"""

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
                sub_task = None
                while main_task or sub_task:
                    if sub_task:
                        current = sub_task
                    else:
                        current = main_task
                    result = current.execute(host)
                    self.task_results[f"{current.name}_{host.name}"] = result

                    # 发送任务执行结果通知
                    status = "成功" if result.success else "失败"
                    message = f"""
    任务: {current.name}
    主机: {host.name}
    状态: {status}
    输出:
    {result.output}
    """
                    if result.error:
                        message += f"\n错误:\n{result.error}"

                    self.notify_all(
                        f"任务 {current.name} 在 {host.name} 上执行{status}",
                        message
                    )
                    main_task = None
                    if result.success:
                        sub_task = current.next_success
                    else:
                        overall_success = False
                        sub_task = current.next_failure
                    self.task_track[f"{current.name}_{host.name}_{result.success}"] = current
        return overall_success