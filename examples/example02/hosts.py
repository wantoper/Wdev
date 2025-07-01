from wdev.hosts import SSHHost, LocalHost

remote_host = SSHHost(hostname="192.168.108.130", username="root", password="passwd")
local_host = LocalHost()