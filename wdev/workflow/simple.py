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
            current = self.tasks[0]
            task_index = 0
            
            while task_index < len(self.tasks):
                current = self.tasks[task_index]
                # 执行当前任务
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

                if not result.success:
                    overall_success = False
                    # 如果任务失败且有失败处理任务，执行失败处理
                    if current.next_failure:
                        current = current.next_failure
                    else:
                        task_index += 1
                else:
                    # 如果任务成功且有后续任务，执行后续任务
                    if current.next_success:
                        current = current.next_success
                    else:
                        task_index += 1

        return overall_success 