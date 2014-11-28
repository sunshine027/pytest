import sys
import subprocess
import os
import time

from exception.testexception import TestException
from tools.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite
from common_module import DEVICE_COMMAND_PREFIX
'''
try:
    import paramiko
except ImportError, e:
    result = os.system('cd ./resource/paramiko-1.7.4/ ; python setup.py install')
    if result != 0:
        raise TestException("Error: no paramiko installed on system, we try to install it, but failed, please run setup.py again")
'''

class sshAccessor:
    def __init__(self, dict):
        try:
            self.ip = dict['IP']
        except KeyError, e:
            raise TestException("Error: no IP element found in device's profile ")
        try:
            self.user = dict['Username']
        except KeyError, e:
            raise TestException("Error: no Username element found in device's profile ")
        try:
            self.pwd = dict['Password']
        except KeyError, e:
            raise TestException("Error: no Password element found in device's profile ")
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(self.ip,username=self.user,password=self.pwd)
        except Exception, e:
            raise TestException("Error: the Username or Password is wrong, we can't connect by ssh ")

    def execute(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        return stdout, stderr
    
    def execute_on_host(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        return stdout, stderr
    
    def download(self, source, dest):
        sftp = self.ssh.open_sftp()
        sftp.get(source,dest)
        #self.ssh.close()
        
    def upload(self,source,dest):
        sftp = self.ssh.open_sftp()
        sftp.put(source,dest)
        #self.ssh.close()

    def teardown(self):
        self.ssh.close()


class adbAccessor:
    def __init__(self, dict):
        try:
            self.num = dict['serialNumber']
        except KeyError, e:
            raise TestException("Error: no serialNumber element found in device profile ")
        if self.num is None or self.num.strip() == '':
            raise TestException("Error: the text of serialNumber element can't be empty in device profile ")

    def execute(self, cmd):
        # if there is quote in cmd, please use single quote, because we will run the command like adb shell " cmd "
        try:
            mycmd = 'adb -s ' + self.num + ' shell ' + '"' +  cmd + '"'
            mycmd = mycmd.replace('\n', '')
        except TypeError, e:
            raise TestException("Error: Invalid serialNumber in device profile!")
#            sys.exit(2)           
#        print mycmd
        p = subprocess.Popen(mycmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout,stderr = p.communicate()
        return stdout, stderr
        
    def execute_test(self, cmd, step_id):
        # if there is quote in cmd, please single quotes, because we will run the command like adb shell " cmd "
        try:
            mycmd = 'adb -s ' + self.num + ' shell ' + '"' +  cmd + '"' + " | tee log" + str(step_id)
            mycmd = mycmd.replace('\n', '')
        except TypeError, e:
            raise TestException("Error: Invalid serialNumber in device profile!")
#            sys.exit(2)           
#        print mycmd
        p = subprocess.Popen(mycmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout,stderr = p.communicate()
        return stdout, stderr
#            sys.exit(2)
        
    def execute_on_host(self, cmd):
        try:
            mycmd = 'adb -s ' + self.num  +  ' ' + cmd
            mycmd = mycmd.replace('\n', '')
        except TypeError, e:
            raise TestException("Error: Invalid serialNumber in device profile!")
#            sys.exit(2)           
        p = subprocess.Popen(mycmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.wait() != 0:
            print inred('Failed:' + mycmd)
#            sys.exit(2)
        else:
            stdout,stderr = p.communicate()
            return stdout, stderr
        
    def download(self,source,dest):
        cmd = 'adb -s ' + self.num + ' pull ' + source + ' ' + dest
        cmd = cmd.replace('\n', '')
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        return stdout, stderr 
    

    def upload(self, source, dest):
        check_desk_cmd = 'adb -s ' + self.num + ' shell "test -d ' + dest  + " && echo 'Directory exists' || echo 'Directory not found'\""
        p = subprocess.Popen(check_desk_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if stdout.strip().find('Directory exists') != -1:
            pass
        elif stdout.strip().find('Directory not found') != -1:
            mkdir_cmd = 'adb -s ' + self.num + ' shell mkdir -p ' + dest
            p = subprocess.Popen(mkdir_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        upload_cmd = 'adb -s ' + self.num + ' push ' + source + ' ' + dest
        upload_cmd = upload_cmd.replace('\n', '')
        p = subprocess.Popen(upload_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        return stdout, stderr 

    def teardown(self):
        pass

def execute_command_on_server(cmd, output_flag):
    '''
        just execute, didn't judge the result.
    '''
    if output_flag:
        print cmd
    cmd = cmd.replace('\n', '')
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout,stderr = p.communicate()
    return stdout,stderr
     
def get_connect_way(device_dict):
    if not device_dict.get('Connect', ''):
        raise TestException("Error: no Connect element found in device's profile, while running")
    elif not device_dict.get('Connect', '') in ['ssh', 'adb']:
        raise TestException("Error: the text of Connect element should be ssh or adb in device's profile ")            
    if not cmp(device_dict['Connect'], 'ssh'):
        accessor = sshAccessor
        prefix = ''
    elif not cmp(device_dict['Connect'], 'adb'):
        accessor = adbAccessor
        prefix = DEVICE_COMMAND_PREFIX
    return prefix, accessor