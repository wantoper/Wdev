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
            result = self.callable_obj(**self.kwargs)
            return TaskResult(success=True, output=str(result))
        except Exception as e:
            return TaskResult(success=False, output="", error=str(e))