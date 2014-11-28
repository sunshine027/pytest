import os
import time

from tools.client import execute_command_on_server
from tools import XMLParser
from tools.client import adbAccessor as accessor

def install_paramiko():
    check_crypto = _check_crypto()
    if check_crypto:
        check_paramiko = _check_paramiko()
        if check_paramiko:
            return True
        else:
            return _install_paramiko()
    else:
        crypto_result = _install_crypto()
        if crypto_result:
            check_paramiko = _check_paramiko()
            if check_paramiko:
                return True
            else:
                return _install_paramiko()
        else:
            return False

def _check_paramiko():
    stdout, stderr = execute_command_on_server('python tools/import_paramiko.py', False)
    if stdout.find('No module named paramiko') != -1 or stderr.find('No module named paramiko') != -1:
        return False
    else:
        return True
    
def _install_paramiko():
    stdout, stderr = execute_command_on_server('cd resource/paramiko-1.7.4/ ; python setup.py install', False)
    return _check_paramiko()
    
def _check_crypto():
    try:
        exec('import Crypto')
    except ImportError, e:
        return False
    else:
        return True
        
def _install_crypto():
    execute_command_on_server("cd resource/pycrypto-2.3/ ; python setup.py install", False)
    return _check_crypto()

def check_jpeg():
    result = os.system('cd /opt/jpeg-8b')
    if result != 0:
        print inred("jpeg-8b hasn't been installed ")
        
def install_android_sdk(device_profile):
    xmlparser_2 = XMLParser.XMLParser(device_profile)
    dev_dict = xmlparser_2.ClientParser()
    cmd = 'tar -zxf ./resource/android-sdk_r18-linux.tgz'   
    execute_command_on_server(cmd, False)
    cmd = 'which adb'
    stdout, stderr = execute_command_on_server(cmd, False)
    cmd = 'ln -s ' + stdout + ' ./android-sdk-linux/tools/adb'
    execute_command_on_server(cmd, False)
    cmd = 'pwd'
    execute_command_on_server(cmd, False)
    stdout, stderr = execute_command_on_server(cmd, False)
    monkeryrunner_env = '#!/usr/bin/env ' + stdout.strip() + '/android-sdk-linux/tools/monkeyrunner'
    # modify monkey_plackback.py
    source_file = open('./resource/monkeyrunner/scripts/monkey_playback.py')
    str = ''
    for line in source_file:
        if line.find('#!/usr/bin/env') != -1:
            continue
        else:
            if line.find('device = MonkeyRunner.waitForConnection') != -1:
                space_str = line[:line.find('device = MonkeyRunner.waitForConnection')]
                line = space_str + 'device = MonkeyRunner.waitForConnection(60, ' + '"' + dev_dict['serialNumber'] + '")\n'
            str += line
    target_file = open('./resource/monkeyrunner/scripts/monkey_playback.py', 'w')
    target_file.write(monkeryrunner_env + '\n' + str)
    # modify monkey_recorder.py
    source_file = open('./resource/monkeyrunner/scripts/monkey_recorder.py')
    str = ''
    for line in source_file:
        if line.find('#!/usr/bin/env') != -1:
            continue
        else:
            if line.find('device = mr.waitForConnection') != -1:
                space_str = line[:line.find('device = mr.waitForConnection')]
                line = space_str + 'device = mr.waitForConnection(60, ' + '"' + dev_dict['serialNumber'] + '")\n'
            str += line
    target_file = open('./resource/monkeyrunner/scripts/monkey_recorder.py', 'w')
    target_file.write(monkeryrunner_env + '\n' + str)
    result = check_android_sdk()
    if result:
        return True
    else:
        return False
                
def check_android_sdk():
    if os.path.isdir('./android-sdk-linux'):
        return True
    else:
        return False
    
def push_busybox(device_profile):
    xmlparser_2 = XMLParser.XMLParser(device_profile)
    dev_dict = xmlparser_2.ClientParser()
    acc = accessor(dev_dict)
    cmd = "test -f /system/bin/busybox && echo 'File exists' || echo 'File not found'" 
    stdout, stderr = acc.execute(cmd)
    if stdout.find('File not found') != -1:
        acc.execute_on_host('root')
        acc.execute_on_host('remount')
        acc.upload("./resource/busybox", '/system/')
        cmd = "test -f /system/bin/busybox && echo 'File exists' || echo 'File not found'" 
        stdout, stderr = acc.execute(cmd)
        if stdout.find('File not found') != -1:
            return False
        else:
            return True
    else:
        return True