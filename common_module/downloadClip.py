import os
import sys
import commands
import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from subprocess import Popen, PIPE

from conf import path
from tools.get_execution_info import get_clip_path
from tools.color import inred, ingreen
from tools.client import execute_command_on_server
from exception.testexception import TestException
from tools.client import adbAccessor as accessor

def downloadClip(caseProfile, dev_dict):
    try:
        xml_tree = ET.parse(caseProfile)
    except ExpatError, e:
        raise  TestException("Error: Cannot parse " + caseProfile)
    root = xml_tree.getroot()
    url_ele = root.find('URL')
    if url_ele is None:
        return "No clip need to download"
    
    clips_eles = url_ele.findall('Clip')
    if len(clips_eles) == 0:
        return "No clip need to download"
    
    for each_ele in clips_eles:
        address = each_ele.text
        if address is None:
            print inred("Clip value is empty, download canceled.")
            continue
        # check if the clip exist, we should use the format in Parameter element, to keep consistent with test module
        format = root.find('Step').find('Parameter').find('Format').text
        inputFile = address.split('/')[-1]
        
        # check if the clip directory exist
        cli = accessor(dev_dict)
        stdout, stderr = cli.execute("test -d " + get_clip_path() + format + "/ && echo 'Directory exists' || echo 'Directory not found'")
        if str(stdout).strip() == 'Directory not found':
            cli.execute("mkdir -p " + get_clip_path() + format + '/')
        # check if clip exist
        stdout, stderr = cli.execute("test -f " + get_clip_path() + format + '/' + inputFile + " && echo 'File exists' || echo 'File not found'")
        if str(stdout).strip() == 'File exists':
            result = check_file_size_in_dut(dev_dict, get_clip_path() + format + '/' + inputFile)
            if result == 'pass':
                continue
            else:
                cli.execute("rm -rf " + get_clip_path() + format + '/' + inputFile)
                
        download_result = 'fail'
        download_count = 0
        while download_result == 'fail':
            download_result = download_clip(address)
            if download_result == 'pass':
                file_size_result = check_file_size('./' + inputFile)
                if file_size_result == 'fail':
                    download_result = 'fail'
            download_count += 1
            if download_count == 3:
                raise TestException("Error: Maybe there is something wrong with network or source clip: " + inputFile + " when downloading")
        print ("Push " + inputFile + " into device ......")
        cli.upload(inputFile, get_clip_path() + format + '/')
        cmd = 'test -f ' + str(get_clip_path() + format + '/' + inputFile) + " && echo 'File exists' || echo 'File not found'"
        stdout, stderr = cli.execute(cmd)
        if str(stdout).strip() == 'File not found':
             raise TestException("Error: push clip failed: " + inputFile)
        os.system("rm -rf " + inputFile)
    return "finished"  
        
def download_clip(address):
    input_file = address.split('/')[-1]
    print '\nDownloading %s ......' %input_file
    cmd = "wget  --no-proxy " + address + " -O " + input_file
    execute_command_on_server(cmd, False)
    cmd = 'test -f ' + str('./' + input_file) + " && echo 'File exists' || echo 'File not found'"
    stdout, stderr = execute_command_on_server(cmd, False)
    if stdout.strip() == 'File exists':
        return 'pass'
    elif stdout.strip() == 'File not found':
        return 'fail'
        

def check_file_size(path):
    cmd = 'du ' + path + ' -sh'
    stdout, stderr = execute_command_on_server(cmd, False)
    file_size = stdout.split()[0]
    if str(file_size).strip() == '0':
        os.remove(path)
        return 'fail'
    else:
        return 'pass'
    
def check_file_size_in_dut(dev_dict, path):
    cli = accessor(dev_dict)
    cmd = 'du ' + path + ' -sh'
    stdout, stderr = cli.execute(cmd)
    file_size = stdout.split()[0]
    if str(file_size).strip() == '0':
        return 'fail'
    else:
        return 'pass'