'''
Created on Apr 15, 2014

@author: sshuster
'''
from paramiko import SFTPClient
import paramiko

class ParamikoWrapper(object):
    
    def __init__(self, server, username, password):
        self.ssh, self.sftp = createClients(server, username, password)
        
    def exec_command(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        stdin.close()
        return stdout.read(), stderr.read()
    
    def mkdir(self, dest_dir):
        self.sftp.mkdir(dest_dir)
        
    def put(self, local_dir, dest_dir):
        self.sftp.put(local_dir,dest_dir)
    
    
def createSSHClient(server, user, password):
    '''Creates an SSH client'''
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, username=user, password=password)
    return client

def createClients(server, username, password):
    '''Creates an SSH and SFTP client'''
    ssh = createSSHClient(server, username, password)
    sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
    return ssh, sftp