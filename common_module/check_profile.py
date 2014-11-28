import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
import sys
import subprocess

from tools.color import inred
from exception.testexception import TestException


PLATFOMR_LIST = ['MFLD', 'MRST']
OS_LIST = ['android', 'meego']
CONNECT_LIST = ['adb', 'ssh']

def check_device_profile(device_profile):
    # only for adb
    try:
        tree = ET.parse(device_profile)
    except IOError, e:
        raise TestException("Error: the file: " + str(device_profile) + " can not be found")
    except ExpatError, e:
        raise TestException("Error: the file: " + str(device_profile) + " is invalid, please check if all tags are matched or missed some signs.")
    try:
        platform = tree.getroot().find('Platform').text
    except AttributeError, e:
         raise TestException("Error: no Platform element found in " + str(device_profile))
    if platform is None or platform.strip() == '' or platform not in PLATFOMR_LIST:
        raise TestException("Error: the text of Platform element is empty in profile: " + str(device_profile) + ' or it should be one of ' + ','.join(PLATFOMR_LIST))
    try:
        os_value = tree.getroot().find('OS').text
    except AttributeError, e:
         raise TestException("Error: no OS element found in " + str(device_profile))
    if os_value is None or os_value.strip() == '' or os_value not in OS_LIST:
        raise TestException("Error: the text of OS element is empty in profile: " + str(device_profile) + ' or it should be one of ' + ','.join(OS_LIST))
    try:
        connect_value = tree.getroot().find('Connect').text
    except AttributeError, e:
         raise TestException("Error: no Connect element found in " + str(device_profile))
    if connect_value is None or connect_value.strip() == '' or connect_value not in CONNECT_LIST:
        raise TestException("Error: the text of Connect element is empty in profile: " + str(device_profile) + ' or it should be one of ' + ','.join(CONNECT_LIST))
    try:
        serialnumber_value = tree.getroot().find('serialNumber').text
    except AttributeError, e:
         raise TestException("Error: no serialNumber element found in " + str(device_profile))
    if serialnumber_value is None or serialnumber_value.strip() == '':
        raise TestException("Error: the text of serialNumber element is empty in profile: " + str(device_profile) + ' or it should be one of ' + ','.join(CONNECT_LIST))
 
def check_adb_connect(device_profile):
    try:
        tree = ET.parse(device_profile)
    except IOError, e:
        raise TestException("Error: the file: " + str(device_profile) + " can not be found")
    except ExpatError, e:
        raise TestException("Error: the file: " + str(device_profile) + " is invalid, please check if all tags are matched or missed some signs.")
    root = tree.getroot()
    connect_way = root.find('Connect')
    if connect_way is None:
        raise TestException("Error: no Connect element found in device file: " + str(device_profile))
    if connect_way.text.strip() == '':
        raise TestException("Error: text of Connect element can't be empty in device file: " + str(device_profile))
    if connect_way.text.strip() == 'adb':
        serial_num = root.find('serialNumber')
        if serial_num is None:
            raise TestException("Error: no serialNumber element found in device profile ")
        if serial_num.text.strip() == '':
            raise TestException("Error: the text of serialNumber element can't be empty in device profile ")
        #if serialNumber has been connected, but the ip changed, the code will block, so we disconnect first
        mycmd = 'adb devices'
        p = subprocess.Popen(mycmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        stdout = ''.join(stdout.split())
        if stdout.find(serial_num.text.strip()) == -1:
            raise TestException("Error: failed to connect adb: " + serial_num.text.strip() + ', no this device')