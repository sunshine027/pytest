import xml.etree.ElementTree as ET
import commands

from tools.client import execute_command_on_server

def kill_kernel_log(dev_dict):
    pid = ''
    status, output = commands.getstatusoutput("adb -s " + dev_dict['serialNumber'] + " shell ps -ef")
    process_list = output.split('\n')
    for process in process_list:
        if process.find('/proc/kmsg') != -1:
            for item in process.split(' '):
                if item.isdigit():
                    pid = item
                    break
                if pid:
                    cmd = 'kill -9 ' + str(pid)
                    commands.getstatusoutput("adb -s " + dev_dict['serialNumber'] + " shell " + cmd)
                
def kill_logcat(dev_dict):
    pid = ''
    status, output = commands.getstatusoutput("adb -s " + dev_dict['serialNumber'] + " shell ps -ef")
    process_list = output.split('\n')
    for process in process_list:
        if process.find('logcat') != -1:
            for item in process.split(' '):
                if item.isdigit():
                    pid = item
                    break
                if pid:
                    cmd = 'kill -9 ' + str(pid)
                    commands.getstatusoutput("adb -s " + dev_dict['serialNumber'] + " shell " + cmd)
                
def kill_command_on_device(case_profile, dev_dict):
        if case_profile.find('run.xml') == -1:
            case_profile += '/run.xml'
        tree = ET.parse(case_profile)
        root = tree.getroot()
        steps = root.findall('Step')
        for step in steps:
            function = step.get('function')
            command_list = []
            if function.find('va') != -1 and function.find('decode') != -1:
                format = root.find('Step').find('Parameter').find('Format').text.strip()
                if not cmp(format, 'H263'):
                    vld = 'mpeg4vld'
                else:
                    vld = format.lower() + 'vld'
                command_list.append(vld)
            elif function.find('va') != -1 and function.find('decode') != -1:
                command_list.append('va_encode')
            elif function.find('media') != -1 and function.find('decode') != -1:
                command_list.append('mediaplayer')
            elif function.find('media') != -1 and function.find('encode') != -1:
                command_list.append('mediarecorder')
            elif function.find('app') != -1 :
                cmd = 'adb -s ' + dev_dict['serialNumber'] + ' shell input keyevent 4'
                execute_command_on_server(cmd, False)
        monitors = root.findall('Monitor')
        for monitor in monitors:
            if monitor.get('name').strip() == 'kernel_log':
                command_list.append('/proc/kmsg')
            elif monitor.get('name').strip() == 'logcat':
                command_list.append('logcat')
            elif monitor.get('name').strip() == 'matrix':
                command_list.append('matrix')
        status, output = commands.getstatusoutput("adb -s " + dev_dict['serialNumber'] + " shell ps -ef")
        process_list = output.split('\n')
        for process in process_list:
            for command in command_list:
                if process.find(command) != -1:
                    pid = ''
                    for item in process.split(' '):
                        if item.isdigit():
                            pid = item
                            break
                    if pid:
                        cmd = 'kill -9 ' + str(pid)
                        commands.getstatusoutput("adb -s " + dev_dict['serialNumber'] + " shell " + cmd)