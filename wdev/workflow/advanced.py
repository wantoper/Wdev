import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Union
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor
from .base import BaseWorkflow
from ..tasks import Task
from ..hosts import Host

class ScheduledTask:
    """定时任务配置"""
    def __init__(self, task: Task, schedule_type: str, **schedule_params):
        """
        初始化定时任务
        :param task: 要执行的任务
        :param schedule_type: 调度类型 ('interval' 或 'daily')
        :param schedule_params: 调度参数
            - 对于 'interval': minutes (int) - 间隔分钟数
            - 对于 'daily': hour (int), minute (int) - 每天执行的时间
        """
        self.task = task
        self.schedule_type = schedule_type
        self.schedule_params = schedule_params
        self._last_run: Optional[datetime] = None
        self._next_run: Optional[datetime] = None
        self._update_next_run()

    def _update_next_run(self):
        """更新下次运行时间"""
        now = datetime.now()
        if self.schedule_type == 'interval':
            minutes = self.schedule_params.get('minutes', 60)
            if not self._last_run:
                self._next_run = now
            else:
                self._next_run = self._last_run + timedelta(minutes=minutes)
        elif self.schedule_type == 'daily':
            hour = self.schedule_params.get('hour', 0)
            minute = self.schedule_params.get('minute', 0)
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            self._next_run = next_run

    def should_run(self) -> bool:
        """检查是否应该运行任务"""
        return datetime.now() >= self._next_run if self._next_run else True

    def mark_executed(self):
        """标记任务已执行"""
        self._last_run = datetime.now()
        self._update_next_run()

class AdvancedWorkflow(BaseWorkflow):
    """高级工作流类，支持定时任务和并行执行"""
    
    def __init__(self, name: str, description: str = "", max_workers: int = 4):
        super().__init__(name, description)
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        self.max_workers = max_workers
        self.is_running = False
        self._thread: Optional[Thread] = None
        self._lock = Lock()

    def add_scheduled_task(self, task: Task, schedule_type: str, **schedule_params) -> 'AdvancedWorkflow':
        """
        添加定时任务
        :param task: 要执行的任务
        :param schedule_type: 'interval' 或 'daily'
        :param schedule_params: 调度参数
        """
        scheduled_task = ScheduledTask(task, schedule_type, **schedule_params)
        self.scheduled_tasks[task.name] = scheduled_task
        return self

    def _execute_task(self, task: Task, host: Host):
        """执行单个任务"""
        with self._lock:
            result = task.execute(host)
            self.task_results[f"{task.name}_{host.name}"] = result

            status = "成功" if result.success else "失败"
            message = f"""
任务: {task.name}
主机: {host.name}
状态: {status}
输出:
{result.output}
"""
            if result.error:
                message += f"\n错误:\n{result.error}"

            self.notify_all(
                f"任务 {task.name} 在 {host.name} 上执行{status}",
                message
            )
            return result.success

    def _run_scheduled_tasks(self):
        """运行定时任务的主循环"""
        while self.is_running:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                for scheduled_task in self.scheduled_tasks.values():
                    if scheduled_task.should_run():
                        for host in self.hosts:
                            executor.submit(self._execute_task, scheduled_task.task, host)
                        scheduled_task.mark_executed()
            time.sleep(1)  # 避免过度消耗CPU

    def start(self):
        """启动工作流"""
        if not self.is_running:
            if not self.scheduled_tasks:
                raise ValueError("没有添加定时任务")
            if not self.hosts:
                raise ValueError("没有添加主机")

            self.is_running = True
            self._thread = Thread(target=self._run_scheduled_tasks, daemon=True)
            self._thread.start()

    def stop(self):
        """停止工作流"""
        self.is_running = False
        if self._thread:
            self._thread.join()
            self._thread = None

    def execute(self) -> bool:
        """立即执行所有任务一次（并行）"""
        if not self.tasks and not self.scheduled_tasks:
            raise ValueError("没有添加任务")
        if not self.hosts:
            raise ValueError("没有添加主机")

        all_tasks = list(self.tasks)
        all_tasks.extend(st.task for st in self.scheduled_tasks.values())
        
        overall_success = True
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for task in all_tasks:
                for host in self.hosts:
                    futures.append(executor.submit(self._execute_task, task, host))
            
            for future in futures:
                if not future.result():
                    overall_success = False

        return overall_success