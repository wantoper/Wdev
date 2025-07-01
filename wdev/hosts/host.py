from abc import ABC, abstractmethod
from typing import Tuple


class Host(ABC):
    """主机基类，定义主机操作的接口"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """执行命令并返回退出码、标准输出和标准错误"""
        pass