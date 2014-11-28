from xml.etree import ElementTree as ET
import shutil
import os

from exception.testexception import TestException
from tools.color import inred
import conf


def edit_profiles(buildname, platform, deviceOS, connect, serialNumber, executionOS, testsuiteUrl, workDir, clipDir, vaClipDir, systemBoot):
    
    if platform == '' and deviceOS == '' and connect == '' and serialNumber == '' and executionOS == '' and testsuiteUrl == '' and workDir == '' and clipDir == '' and vaClipDir == '' and systemBoot == '':   
        user_input = ''
        while user_input != '0':
            print "\nWhich profile you want to edit? "
            print "1. device profile"
            print "2. execution profile"
            print "0. exit\n"
            user_input = raw_input("please input number: ")
            if user_input == '1':
                edit_device()
            elif user_input == '2':
                edit_execution(buildname)
            elif user_input == '0':
                exit(0)
            else:
                print "invalid number, input again: "
                continue
    else:
        if platform == '' and deviceOS == '' and connect == '' and serialNumber == '':
            autoEdit_execution(buildname, executionOS, testsuiteUrl, workDir, clipDir, vaClipDir, systemBoot)
        elif executionOS == '' and testsuiteUrl == '' and workDir == '' and clipDir == '' and vaClipDir == '' and systemBoot == '':
            autoEdit_device(platform, deviceOS, connect, serialNumber)
        else:
            autoEdit_device(platform, deviceOS, connect, serialNumber)
            autoEdit_execution(buildname, executionOS, testsuiteUrl, workDir, clipDir, vaClipDir, systemBoot)
        
        
def edit_device():
    try:
        tree = ET.parse(conf.DEFAULT_DEVICE_PATH)
        root = tree.getroot()
    except Exception, e:
        raise TestException("Error: cannot parse default device profile.")    
    
    user_input = ''
    while user_input != '0':
        
        #obtain current value
        try:
            ele_platform = root.find("Platform")
            ele_os = root.find("OS")
            ele_connect = root.find("Connect")
            ele_serialNumber = root.find("serialNumber")
        except Exception, e:
            raise TestException("Error: element parsing error in default device profile.") 
            
        if ele_platform.text is None:
            ele_platform.text = ''        
        if ele_os.text is None:
            ele_os.text = ''  
        if ele_connect.text is None:
            ele_connect.text = ''
        if ele_serialNumber.text is None:
            ele_serialNumber.text = ''  
        
        print "\nWhich element you want to edit? "
        print "1. Platform.     current value: " + ele_platform.text
        print "2. OS.           current value: " + ele_os.text
        print "3. Connect.      current value: " + ele_connect.text
        print "4. serialNumber. current value: " + ele_serialNumber.text
        print "0. exit\n"
        user_input = raw_input("please input number: ")
        if user_input == '1':
            ele_platform = root.find("Platform")
            if not ele_platform == None:
                print "Current value: " + ele_platform.text
                new_value = raw_input("please input the new value (MFLD or MRST): ")
                ele_platform.text = new_value
                tree.write(conf.DEFAULT_DEVICE_PATH)
                continue
            else:
                print inred("Error: no Platform element in default device profile.")
                continue
        elif user_input == '2':
            ele_os = root.find("OS")
            if not ele_os == None:
                print "Current value: " + ele_os.text
                new_value = raw_input("please input the new value (android or meego): ")
                ele_os.text = new_value
                tree.write(conf.DEFAULT_DEVICE_PATH)
                continue
            else:
                print inred("Error: no OS element in default device profile.")
                continue
        elif user_input == '3':
            ele_connect = root.find("Connect")
            if not ele_connect == None:
                print "Current value: " + ele_connect.text
                new_value = raw_input("please input the new value (adb or ssh): ")
                ele_connect.text = new_value
                tree.write(conf.DEFAULT_DEVICE_PATH)
                continue
            else:
                print inred("Error: no Connect element in default device profile.")
                continue
        elif user_input == '4':
            ele_serialNumber = root.find("serialNumber")
            if not ele_serialNumber == None:
                print "Current value: " + ele_serialNumber.text
                new_value = raw_input("please input the new value: ")
                ele_serialNumber.text = new_value
                tree.write(conf.DEFAULT_DEVICE_PATH)
                continue
            else:
                print inred("Error: no serialNumber element in default device profile.")
                continue
        elif user_input == '0':
            break
        else:
            print "invalid number, input again: "
            continue
        
def edit_execution(buildname):
    try:
        tree = ET.parse(conf.EXECUTION_PATH + buildname + ".xml")
        root = tree.getroot()
    except Exception, e:
        raise TestException("Error: cannot parse execution profile.")
    
    user_input = ''
    while user_input != '0':
        
        #obtain current value
        try:
            ele_os = root.find("Setup").find("OS")
            ele_DUTTestsuite = root.find("Setup").find("DUTTestsuite")
            ele_DUTWorkDirectory = root.find("Setup").find("DUTWorkDirectory")
            ele_ClipsDirectory = root.find("Setup").find("ClipsDirectory")
            ele_VAClipsDirectory = root.find("Setup").find("VAClipsDirectory")
            ele_SystemBoot = root.find("Setup").find("SystemBoot")
        except Exception, e:
            raise TestException("Error: element parsing error in execution profile.")
        
        if ele_os.text is None:
            ele_os.text = ''
        if ele_DUTTestsuite.text is None:
            ele_DUTTestsuite.text = ''
        if ele_DUTWorkDirectory.text is None:
            ele_DUTWorkDirectory.text = ''
        if ele_ClipsDirectory.text is None:
            ele_ClipsDirectory.text = ''
        if ele_SystemBoot.text is None:
            ele_SystemBoot.text = ''
        
        print "\nWhich element you want to edit? "
        print "1. OS.               current value: " + ele_os.text
        print "2. DUTTestsuite url. current value: " + ele_DUTTestsuite.text
        print "3. DUTWorkDirectory. current value: " + ele_DUTWorkDirectory.text
        print "4. ClipsDirectory.   current value: " + ele_ClipsDirectory.text
        print "5. SystemBoot.       current value: " + ele_SystemBoot.text
        print "0. exit\n"
        user_input = raw_input("please input number:")
        if user_input == '1':
            ele_os = root.find("Setup").find("OS")
            if not ele_os == None:
                print "Current value: " + ele_os.text
                new_value = raw_input("please input the new value (android or meego): ")
                ele_os.text = new_value
                tree.write(conf.EXECUTION_PATH + buildname + ".xml")
                continue
            else:
                print inred("Error: no OS element in " + conf.EXECUTION_PATH + buildname + ".xml.")
                continue
        if user_input == '2':
            ele_DUTTestsuite = root.find("Setup").find("DUTTestsuite")
            if not ele_DUTTestsuite == None:
                print "Current value: " + ele_DUTTestsuite.text
                new_value = raw_input("please input the new value: ")
                ele_DUTTestsuite.text = new_value
                tree.write(conf.EXECUTION_PATH + buildname + ".xml")
                continue
            else:
                print inred("Error: no DUTTestsuite element in " + conf.EXECUTION_PATH + buildname + ".xml.")
                continue
        if user_input == '3':
            ele_DUTWorkDirectory = root.find("Setup").find("DUTWorkDirectory")
            if not ele_DUTWorkDirectory == None:
                print "Current value: " + ele_DUTWorkDirectory.text
                new_value = raw_input("please input the new value: ")
                ele_DUTWorkDirectory.text = new_value
                tree.write(conf.EXECUTION_PATH + buildname + ".xml")
                continue
            else:
                print inred("Error: no DUTWorkDirectory element in " + conf.EXECUTION_PATH + buildname + ".xml.")
                continue
        if user_input == '4':
            ele_ClipsDirectory = root.find("Setup").find("ClipsDirectory")
            if not ele_ClipsDirectory == None:
                print "Current value: " + ele_ClipsDirectory.text
                new_value = raw_input("please input the new value: ")
                ele_ClipsDirectory.text = new_value
                tree.write(conf.EXECUTION_PATH + buildname + ".xml")
                continue
            else:
                print inred("Error: no ClipsDirectory element in " + conf.EXECUTION_PATH + buildname + ".xml.")
                continue
        if user_input == '5':
            ele_SystemBoot = root.find("Setup").find("SystemBoot")
            if not ele_SystemBoot == None:
                print "Current value: " + ele_SystemBoot.text
                new_value = raw_input("please input the new value (eMMC or sdcard): ")
                ele_SystemBoot.text = new_value
                tree.write(conf.EXECUTION_PATH + buildname + ".xml")
                continue
            else:
                print inred("Error: no SystemBoot element in " + conf.EXECUTION_PATH + buildname + ".xml.")
                continue
        elif user_input == '0':
            break
        else:
            print "invalid number, input again: "
            continue


def autoEdit_device(platform, deviceOS, connect, serialNumber):
    try:
        tree = ET.parse(conf.DEFAULT_DEVICE_PATH)
        root = tree.getroot()
    except Exception, e:
        print inred(e)
        
    if not platform == '':
        ele_platform = root.find("Platform")
        if not ele_platform == None:
            ele_platform.text = platform
            tree.write(conf.DEFAULT_DEVICE_PATH)
            print "element Platform changed in default device profile."
        else:
            print inred("Error: no Platform element in default device profile.")
            
    if not deviceOS == '':
        ele_os = root.find("OS")
        if not ele_os == None:
            ele_os.text = deviceOS
            tree.write(conf.DEFAULT_DEVICE_PATH)
            print "element OS changed in default device profile."
        else:
            print inred("Error: no OS element in default device profile.")
            
    if not connect == '':
        ele_connect = root.find("Connect")
        if not ele_connect == None:
            ele_connect.text = connect
            tree.write(conf.DEFAULT_DEVICE_PATH)
            print "element Connect changed in default device profile."
        else:
            print inred("Error: no Connect element in default device profile.")
            
    if not serialNumber == '':
        ele_serialNumber = root.find("serialNumber")
        if not ele_serialNumber == None:
            ele_serialNumber.text = serialNumber
            tree.write(conf.DEFAULT_DEVICE_PATH)
            print "element serialNumber changed in default device profile."
        else:
            print inred("Error: no serialNumber element in default device profile.")
            
    
def autoEdit_execution(buildname, executionOS, testsuiteUrl, workDir, clipDir, vaClipDir, systemBoot):
    
    try:
        tree = ET.parse(conf.EXECUTION_PATH + buildname + ".xml")
        root = tree.getroot()
    except Exception, e:
        print inred(e)
        
    if not executionOS == '':
        ele_os = root.find("Setup").find("OS")
        if not ele_os == None:
            ele_os.text = executionOS
            tree.write(conf.EXECUTION_PATH + buildname + ".xml")
            print "element OS changed in " + conf.EXECUTION_PATH + buildname + ".xml."
        else:
            print inred("Error: no OS element in " + conf.EXECUTION_PATH + buildname + ".xml.")
            
    if not testsuiteUrl == '':
        ele_DUTTestsuite = root.find("Setup").find("DUTTestsuite")
        if not ele_DUTTestsuite == None:
            ele_DUTTestsuite.text = testsuiteUrl
            tree.write(conf.EXECUTION_PATH + buildname + ".xml")
            print "element DUTTestsuite changed in " + conf.EXECUTION_PATH + buildname + ".xml."
        else:
            print inred("Error: no DUTTestsuite element in " + conf.EXECUTION_PATH + buildname + ".xml.")
            
    if not workDir == '':
        ele_DUTWorkDirectory = root.find("Setup").find("DUTWorkDirectory")
        if not ele_DUTWorkDirectory == None:
            ele_DUTWorkDirectory.text = workDir
            tree.write(conf.EXECUTION_PATH + buildname + ".xml")
            print "element DUTWorkDirectory changed in " + conf.EXECUTION_PATH + buildname + ".xml."
        else:
            print inred("Error: no DUTWorkDirectory element in " + conf.EXECUTION_PATH + buildname + ".xml.")
            
    if not clipDir == '':
        ele_ClipsDirectory = root.find("Setup").find("ClipsDirectory")
        if not ele_ClipsDirectory == None:
            ele_ClipsDirectory.text = clipDir
            tree.write(conf.EXECUTION_PATH + buildname + ".xml")
            print "element ClipsDirectory changed in " + conf.EXECUTION_PATH + buildname + ".xml."
        else:
            print inred("Error: no ClipsDirectory element in " + conf.EXECUTION_PATH + buildname + ".xml.")
            
    if not vaClipDir == '':
        ele_VAClipsDirectory = root.find("Setup").find("VAClipsDirectory")
        if not ele_VAClipsDirectory == None:
            ele_VAClipsDirectory.text = vaClipDir
            tree.write(conf.EXECUTION_PATH + buildname + ".xml")
            print "element VAClipsDirectory changed in " + conf.EXECUTION_PATH + buildname + ".xml."
        else:
            print inred("Error: no VAClipsDirectory element in " + conf.EXECUTION_PATH + buildname + ".xml.")
            
    if not systemBoot == '':
        ele_SystemBoot = root.find("Setup").find("SystemBoot")
        if not ele_SystemBoot == None:
            ele_SystemBoot.text = systemBoot
            tree.write(conf.EXECUTION_PATH + buildname + ".xml")
            print "element SystemBoot changed in " + conf.EXECUTION_PATH + buildname + ".xml."
        else:
            print inred("Error: no SystemBoot element in " + conf.EXECUTION_PATH + buildname + ".xml.")
                








    