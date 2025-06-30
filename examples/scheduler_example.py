from wdev.workflow.simple import SimpleWorkflow
from wdev.workflow.scheduler import WorkflowScheduler
from wdev.hosts import SSHHost
from wdev.tasks import ShellTask
from wdev.notifications import ConsoleNotifier
import time

def main():
    # 创建调度器
    scheduler = WorkflowScheduler()
    console_notifier = ConsoleNotifier()

    remote_host = SSHHost(hostname="192.168.108.130", username="root", password="passwd")
    workflow = SimpleWorkflow("部署工作流", "用于部署和检查服务状态")
    check_disk = ShellTask("检查磁盘空间", "df -h")
    (workflow.add_host(remote_host)
            .add_task(check_disk)
            .add_notifier(console_notifier))



    # 添加工作流到调度器，使用不同的调度策略
    # workflow1: 每30秒执行一次，异步执行
    scheduler.add_workflow(workflow, interval=30, async_mode=True)
    
    # workflow2: 每60秒执行一次，同步执行
    # scheduler.add_workflow(workflow, interval=60, async_mode=False)
    
    # workflow3: 在指定时间执行，异步执行
    # scheduler.add_workflow(workflow, at_time="14:00", async_mode=True)
    
    try:
        # 启动调度器
        scheduler.start()
        
        # 手动运行一个工作流
        # print("\nManually running DiskCheck workflow...")
        # scheduler.run_workflow("部署工作流")
        
        # 让程序运行5分钟
        # print("\nScheduler will run for 5 minutes...")
        # time.sleep(300)
        
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, stopping scheduler...")
    finally:
        # 停止调度器
        scheduler.stop()

if __name__ == "__main__":
    main() 