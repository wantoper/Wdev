from wdev.hosts import Host
from wdev.tasks import TaskResult, Task


class ShellTask(Task):
    """Shell命令任务"""
    def __init__(self, name: str, command: str= "", description: str = ""):
        super().__init__(name, description)
        self.command = command
        self.command_field = None

    def with_data_command(self,field):
        "用于从前置任务的结果中获取命令"
        self.command_field = field
        return self

    def execute(self,host: Host) -> TaskResult:
        all_output = []
        all_errors = []
        success = True

        if self.command_field is not None:
            if self.pre_task is None:
                raise ValueError("无上游任务，with_data_command 失效")
            if self.pre_task.task_results is None or self.pre_task.task_results.data is None:
                raise ValueError("无法从上游任务中获取结果")
            self.command = self.pre_task.task_results.data.get(self.command_field, self.command)
        exit_code, output, error = host.execute_command(self.command)
        if exit_code != 0:
            success = False
            all_output.append(error)
        all_output.append(output)

        self.task_results = TaskResult(
            success=success,
            output="".join(all_output),
            error="".join(all_errors)
        )
        return self.task_results