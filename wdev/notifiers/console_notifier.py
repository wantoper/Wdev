from wdev.notifiers import Notifier


class ConsoleNotifier(Notifier):
    """控制台通知器，用于测试和开发"""

    def __init__(self):
        super().__init__("console")

    def notify(self, subject: str, message: str, **kwargs) -> bool:
        # print(f"\n=== {subject} ===")
        print(message)
        # print("=" * (len(subject) + 8))
        return True