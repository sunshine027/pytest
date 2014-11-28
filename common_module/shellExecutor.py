import subprocess
from common_module.testexception import TestException

def executeShell(cmd, serialNo):
    try:
        Exe_cmd = 'adb -s ' + serialNo + ' shell ' + '"' +  cmd + '"'
    except TypeError, e:
        raise TestException("Error: Invalid serialNumber in device profile!")           
    print Exe_cmd
    p = subprocess.Popen(Exe_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait() != 0:
        raise TestException('Failed:' + Exe_cmd)
    else:
        stdout,stderr = p.communicate()
        return stdout, stderr  