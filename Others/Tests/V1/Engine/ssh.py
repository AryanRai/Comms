from paramiko import SSHClient
import paramiko

client = SSHClient()
#client.load_system_host_keys()
#client.load_host_keys('~/.ssh/known_hosts')
#client.set_missing_host_key_policy(AutoAddPolicy())
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('fastr-pi', username='fastr', password='potato451')


_stdin, _stdout,_stderr = client.exec_command("ls")
print(_stdout.read().decode())
_stdin, _stdout,_stderr = client.exec_command("python3.10 ~/.local/lib/python3.10/site-packages/mavhehe.py")
print(_stdout.read().decode())
_stdin, _stdout,_stderr = client.exec_command("ls")
print(_stdout.read().decode())
client.close()