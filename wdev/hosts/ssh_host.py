import paramiko
from typing import Tuple, Optional
from wdev.hosts import Host


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