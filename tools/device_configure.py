import time
import os

from tools.client import adbAccessor as accessor
from tools import XMLParser
from tools.create_configure import create_path_file
from tools.get_execution_info import get_build_name
import conf

IP_Of_Lab = '192.168.11.8'

def connect_wifi(device_profile):
    # connect 9L02
    xmlparser_2 = XMLParser.XMLParser(device_profile)
    dev_dict = xmlparser_2.ClientParser() 
    acc = accessor(dev_dict)
    acc.upload('resource/settings/wpa_supplicant.conf', '/data/misc/wifi/')
    acc.execute('svc wifi disable')
    acc.execute('svc wifi enable')
    time.sleep(60)
    stdout, sterr = acc.execute('ping ' + IP_Of_Lab + ' -w 5')
    if stdout.find('bytes from ' + IP_Of_Lab.strip()) != - 1 and stdout.find('seq=0') != -1:
        return True
    else:
        return False
    
def change_avstreaming_ip(new_ip):
    if os.path.isfile('./conf/path.py'):
        path_file = open('./conf/path.py')
        content = ''
        for line in path_file:
            if line.find('IP') != -1:
                continue
            else:
                content += line
        content += 'IP = "' + new_ip + '"'
        path_file = open('./conf/path.py', 'w')
        path_file.write(content + '\n')
        path_file.close()
        return True
    else:
        build_name = get_build_name()
        execution_profile = conf.EXECUTION_PATH + build_name + '.xml'
        create_path_file(execution_profile)
        change_avstreaming_ip(new_ip)
        
def get_device_serialnumber(device_path):
    try:
        tree = ET.parse(device_path)
    except IOError, e:
        raise TestException("Error: the file: " + str(device_path) + " can not be found")
    except ExpatError, e:
        raise TestException("Error: the file: " + str(device_path) + " is invalid, please check if all tags are matched or missed some signs.")
    root = tree.getroot()
    connect_way = root.find('Connect')
    if connect_way is None:
        raise TestException("Error: Connect element can't be found in file: %s" %device_path)
    if connect_way.text is None or connect_way.text.strip() == '':
        raise TestException("Error: text of Connect element can't be empty in file: %s" %device_path)
    
    if not connect_way.text in ['ssh', 'adb']:
        raise TestException("Error: the text of Connect element should be ssh or adb in file: %s" %device_path)            
    if connect_way.text == 'adb':
        serialNumber = root.find('serialNumber')
        if serialNumber is None:
            raise TestException("Error: serialNumber element can't be found in file: %s" %device_path)
        if serialNumber.text is None or serialNumber.text.strip() == '':
            raise TestException("Error: text of serialNumber element can't be empty in file: %s" %device_path) 
        return ('adb', serialNumber.text)
    elif connect_way.text == 'ssh':
        serialNumber = root.find('IP')
        if serialNumber is None:
            raise TestException("Error: IP element can't be found in file: %s" %device_path)
        if serialNumber.text is None or serialNumber.text.strip() == '':
            raise TestException("Error: text of IP element can't be empty in file: %s" %device_path) 
        return ('ssh', serialNumber.text)