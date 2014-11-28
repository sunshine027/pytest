import os
import sys
from xml.etree import ElementTree as ET
from tools.client import execute_command_on_server

from exception.testexception import TestException
from tools.color import inred, ingreen
import conf

def chDev(device_numer):
    try:
        tree = ET.parse(conf.DEFAULT_DEVICE_PATH)
        root = tree.getroot()
    except Exception, e:
        print inred("Error: cannot parse device profile: " + conf.DEFAULT_DEVICE_PATH)
        exit(-1)
                
    ele_serialNumber = root.find("serialNumber")
    ele_serialNumber.text = device_numer
    tree.write(conf.DEFAULT_DEVICE_PATH)

def get_device_list():
    stdout, stderr = execute_command_on_server('adb devices', False)
    line_list = stdout.split(os.linesep)[1:]
    device_list = [line.split('\t')[0] for line in line_list if line]
    return device_list

def print_device(device_list):
    for device in device_list:
        print str(device_list.index(device) + 1) + '. ' + device
    print str(len(device_list) + 1) + '. no your device, refresh'
        
def main():
    device_list = get_device_list()
    if len(device_list) == 0:
        print 'No Device Connected to Host'
        sys.exit(0)
    elif len(device_list) == 1:
        print ingreen('Only One Device ' + device_list[0] + ' Connected to Host')
        chDev(device_list[0])
        print ingreen("Default Set " + device_list[0] + " in Device Profile.")
        sys.exit(0)
    else:
        print_device(device_list)
        user_input = ''
        while user_input == '':
            user_input = raw_input('Please select the device number:')
            try:
                if int(user_input) < 0 or int(user_input) > (len(device_list) + 1):
                    raise ValueError
                elif int(user_input) == len(device_list) + 1:
                    main()
                chDev(device_list[int(user_input) -1])
                print ingreen('Set ' + device_list[int(user_input) -1] + ' in Device Profile Successfully')
                sys.exit(0)
            except ValueError, e:
                print 'invalid user input'
                user_input = ''
            
if __name__ == "__main__":
    main()