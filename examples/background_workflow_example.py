from wdev.workflow.background import BackgroundWorkflow, WorkflowNode
from wdev.hosts import LocalHost
from wdev.tasks import ShellTask
from wdev.notifications import ConsoleNotifier
import time

def main():
    # 创建后台工作流
    workflow = BackgroundWorkflow("系统监控工作流")

    # 创建主机
    local_host = LocalHost()

    # 创建通知器
    console_notifier = ConsoleNotifier()

    # 创建监控节点
    disk_monitor = WorkflowNode(
        name="磁盘监控",
        task=ShellTask("检查磁盘空间", "df -h"),
        host=local_host,
        notifier=console_notifier,
        interval=300  # 每5分钟执行一次
    )

    memory_monitor = WorkflowNode(
        name="内存监控",
        task=ShellTask("检查内存使用", "free -h"),
        host=local_host,
        notifier=console_notifier,
        interval=180  # 每3分钟执行一次
    )

    # 添加节点到工作流
    workflow.add_node(disk_monitor)
    workflow.add_node(memory_monitor)

    try:
        print("启动后台工作流...")
        workflow.start_all()
        
        # 保持主程序运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n停止后台工作流...")
        workflow.stop_all()
        print("工作流已停止")

if __name__ == "__main__":
    main() 