from wdev.hosts import Host
from wdev.tasks import TaskResult, Task

class PythonTask(Task):
    """Python可调用对象任务"""
    def __init__(self, name: str, callable_obj, description: str = "", **kwargs):
        super().__init__(name, description)
        self.callable_obj = callable_obj
        self.kwargs = kwargs

    def execute(self,host: Host) -> TaskResult:
        try:
            self.task_results = self.callable_obj(self,host,**self.kwargs)
        except Exception as e:
            # print("执行Python任务时发生错误:", e)
            self.task_results = TaskResult(success=False, output="", error=str(e))

        return self.task_results