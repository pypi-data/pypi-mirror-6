'''
Created on Apr 15, 2014

@author: sshuster
'''
import os
import subprocess

class CygwinSSH(object):
    ssh_root = "ssh {0}@{1} "
    scp_root = "scp {0} {1}:{2}"
    mkdir = "mkdir {0}"
    
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.ssh_rootf = self.ssh_root.format(user,host)
    
    def make_ssh_command(self, command):
        return self.ssh_rootf + "'" + command + "'"
    
    def mkdir(self, dest_folder):
        os.system(self.make_ssh_command(self.mkdir.format(dest_folder)))
        
    def put(self, src, dest):
        os.system(self.scp_root.format(src,self.host,dest))
        
    def exec_command(self, command):
        output = ""
        try:
            output = subprocess.check_output(self.make_ssh_command(command), shell=True)
        except subprocess.CalledProcessError:
            pass
        return output, ""