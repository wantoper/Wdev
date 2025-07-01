import threading
import time
import schedule
from typing import Dict, Optional, List
from datetime import datetime
from .workflow import Workflow
from prettytable import PrettyTable

class WorkflowJob:
    def __init__(self, workflow: Workflow, interval: Optional[int] = None,
                 at_time: Optional[str] = None, async_mode: bool = False):
        self.workflow = workflow
        self.interval = interval  # 间隔时间（秒）
        self.at_time = at_time   # 指定时间（格式：HH:MM）
        self.async_mode = async_mode
        self.last_run: Optional[datetime] = None
        self.is_running: bool = False
        self.thread: Optional[threading.Thread] = None
        self._schedule_job = None

    def _run_workflow(self):
        self.is_running = True
        self.last_run = datetime.now()
        try:
            success = self.workflow.execute()
            print(f"Workflow {self.workflow.name} executed {'successfully' if success else 'with failures'}")
        except Exception as e:
            print(f"Error executing workflow {self.workflow.name}: {str(e)}")
        finally:
            self.is_running = False

    def run(self):
        if self.async_mode:
            if self.is_running:
                print(f"Workflow {self.workflow.name} is already running")
                return
            self.thread = threading.Thread(target=self._run_workflow)
            self.thread.start()
        else:
            self._run_workflow()

class WorkflowScheduler:
    def __init__(self):
        self.jobs: Dict[str, WorkflowJob] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def add_workflow(self, workflow: Workflow, interval: Optional[int] = None,
                    at_time: Optional[str] = None, async_mode: bool = False) -> None:
        """
        添加工作流到调度器
        :param workflow: 工作流实例
        :param interval: 运行间隔（秒）
        :param at_time: 指定运行时间（HH:MM格式）
        :param async_mode: 是否异步执行
        """
        if workflow.name in self.jobs:
            raise ValueError(f"Workflow {workflow.name} already exists in scheduler")

        job = WorkflowJob(workflow, interval, at_time, async_mode)
        
        if interval is not None:
            job._schedule_job = schedule.every(interval).seconds.do(job.run)
        elif at_time is not None:
            job._schedule_job = schedule.every().day.at(at_time).do(job.run)
            
        self.jobs[workflow.name] = job

    def remove_workflow(self, workflow_name: str) -> None:
        """从调度器中移除工作流"""
        if workflow_name in self.jobs:
            job = self.jobs[workflow_name]
            if job._schedule_job:
                schedule.cancel_job(job._schedule_job)
            del self.jobs[workflow_name]

    def _print_status(self):
        """打印所有工作流状态（表格形式）"""
        x = PrettyTable(["Workflow Name", "Status", "Last Run", "Schedule", "Async", "Log"])
        x.align["Log"]= "l"
        # 打印每个工作流的状态
        for name, job in self.jobs.items():
            status = "Running" if job.is_running else "Waiting"
            last_run = job.last_run.strftime("%Y-%m-%d %H:%M:%S") if job.last_run else "Never"
            
            schedule_info = []
            if job.interval:
                schedule_info.append(f"Every {job.interval}s")
            if job.at_time:
                schedule_info.append(f"At {job.at_time}")
            schedule_str = " and ".join(schedule_info) if schedule_info else "Manual"

            x.add_row([name, status, last_run, schedule_str, job.async_mode, job.workflow.print_task_routes()])
        print("\033c", end="")
        print(x,end='\n')

    def _run_scheduler(self):
        """运行调度器主循环"""
        while self._running:
            schedule.run_pending()
            self._print_status()
            time.sleep(1)

    def start(self):
        """启动调度器"""
        if self._running:
            print("Scheduler is already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_scheduler)
        self._thread.daemon = True  # 设置为守护线程
        self._thread.start()
        while True:
            time.sleep(1)

    def stop(self):
        """停止调度器"""
        self._running = False
        if self._thread:
            self._thread.join()
        print("Workflow Scheduler stopped")

    def run_workflow(self, workflow_name: str):
        """手动运行指定工作流"""
        if workflow_name not in self.jobs:
            raise ValueError(f"Workflow {workflow_name} not found in scheduler")
        self.jobs[workflow_name].run() 