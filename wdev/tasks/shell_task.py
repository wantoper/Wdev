from wdev.hosts import Host
from wdev.tasks import TaskResult, Task


class ShellTask(Task):
    """Shell命令任务"""
    def __init__(self, name: str, command: str, description: str = ""):
        super().__init__(name, description)
        self.command = command

    def execute(self,host: Host) -> TaskResult:
        all_output = []
        all_errors = []
        success = True

        exit_code, output, error = host.execute_command(self.command)
        if exit_code != 0:
            success = False
            all_output.append(error)
            # all_errors.append(f"Host {host.name}: {error}")
        # all_output.append(f"Host {host.name}: ===========\n{output}\n===========")
        all_output.append(output)

        return TaskResult(
            success=success,
            output="".join(all_output),
            error="".join(all_errors)
        )