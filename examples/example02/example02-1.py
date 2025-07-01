from wdev.workflow import WorkflowScheduler

from examples.example02.workflow01 import workflow01
from examples.example02.workflow02 import workflow02

def main():
    # 创建调度器
    scheduler = WorkflowScheduler()

    #10秒运行一次 使用非阻塞运行
    scheduler.add_workflow(workflow01, interval=10, async_mode=True)

    #每天14:00运行一次 使用非阻塞运行
    scheduler.add_workflow(workflow02, at_time="14:00", async_mode=True)

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, stopping scheduler...")
    finally:
        # 停止调度器
        scheduler.stop()

if __name__ == "__main__":
    main()