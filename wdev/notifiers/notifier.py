from abc import ABC, abstractmethod

class Notifier(ABC):
    """通知器基类"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def notify(self, subject: str, message: str, **kwargs) -> bool:
        """发送通知"""
        pass