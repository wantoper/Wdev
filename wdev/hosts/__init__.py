from abc import ABC, abstractmethod
import paramiko
import subprocess
from typing import Tuple, Optional

class Host(ABC):
    """主机基类，定义主机操作的接口"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """执行命令并返回退出码、标准输出和标准错误"""
        pass

class SSHHost(Host):
    """SSH远程主机实现"""
    
    def __init__(self, hostname: str, username: str, password: Optional[str] = None, 
                 key_filename: Optional[str] = None, port: int = 22):
        super().__init__(hostname)
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.port = port
        self._client = None

    def _get_client(self) -> paramiko.SSHClient:
        if not self._client:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                key_filename=self.key_filename
            )
            self._client = client
        return self._client

    def execute_command(self, command: str) -> Tuple[int, str, str]:
        client = self._get_client()
        stdin, stdout, stderr = client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        return exit_code, stdout.read().decode(), stderr.read().decode()

    def __del__(self):
        if self._client:
            self._client.close()

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