import subprocess
from typing import Tuple, Optional

from wdev.hosts import Host


class LocalHost(Host):
    """本地主机实现"""

    def __init__(self):
        super().__init__("localhost")

    def execute_command(self, command: str) -> Tuple[int, str, str]:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr