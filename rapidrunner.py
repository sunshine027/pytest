#!/usr/bin/python
"""
    it's a new interface for run test, you can use it like the following:
    1. python rapidrunner.py -d        download execution from tms
    2. python rapidrunner.py -l        list the execution cases
    3. python rapidrunner.py -c        configure the device and execution profile
    4. python rapidrunner.py -p        upload clip to mediaserver
    #5. python rapidrunner.py -e        run a execution
    #6. python rapidrunner.py -r        create a test_report for all the case result
    7. python rapidrunner.py -u        upload the result to tms
    PS: rapidrunner.py -e is the same with pytest.py -e execution_path -d device_path,
        and rapidrunner thought the build xml profile in config.EXECUTION_PATH is the execution profile, 
        and device xml profile in config.DEVICE_PATH is the device profile. rapidrunner.py -p
        is the same as python setup.py -d device_path, -e execution_path, the parameter is like
        rapidrunner.py -e.
"""
from optparse import OptionParser
import os
import sys
import commands

from common_module import download_execution, list_cases, upload_result, edit_profile, upload_clip
from report import case_result_report
from tools.color import inred, ingreen, inblue
from tools.device_configure import get_device_serialnumber
from tools.get_execution_info import get_build_name
from exception.testexception import TestException
import conf


def check_if_config_device():
    # check if user has configured the device profile and execution profile
    device_path = ''
    execution_path = ''
    args = ''
    # at the beginning, config.DEVICE_PATH doesn't exist, only if the users have configured the device profile, the
    # directory will be created.
    if not os.path.isdir(conf.DEVICE_PATH):
        print inred("Warning: you haven't configure device profile, please run python rapidrunner.py -c first")
        sys.exit(0)
    else:
        if os.path.isfile(conf.DEVICE_PATH + conf.DEVICE_PROFILE_NAME):
            device_path = conf.DEVICE_PATH + conf.DEVICE_PROFILE_NAME
        else:
            print inred("please run python rapidrunner.py -c first to configure device profile")
            sys.exit(0)
    build_name = get_build_name()
    if os.path.isfile(conf.EXECUTION_PATH + build_name + '.xml'):
        args = args + ' -e ' + conf.EXECUTION_PATH + build_name + '.xml'
    else:
        raise TestException("Error: no execution profile under %s" %conf.EXECUTION_PATH)
    if device_path:
        args = args + ' -d %s' %device_path
    else:
        print inred("please run python rapidrunner.py -c first to configure device profile")
        sys.exit(0)
    connect_way, serial_number = get_device_serialnumber(device_path)
    ip_or_serialnumber = connect_way == 'adb' and 'serialNumber' or 'IP'
    print inblue('TIP: you will run with execution: %s.xml on DUT with %s: %s' %(build_name, ip_or_serialnumber, serial_number))
    return args
        
def test_download(option, opt_str, value, parser, *args, **kwargs):
    print "***** Download test_repo and execution profiles to local from TMS *****"
    try:
        download_execution.download(args[0], args[1])
    except Exception, e:
        raise TestException("Error: Cannot download.")
        
        
def test_list(option, opt_str, value, parser):
    print "***** Execution case list *****"
    try:
        list_cases.list_cases(True, get_buildname())
    except TestException, e:
        print inred(e.value)


def test_configure(option, opt_str, value, parser, *args, **kwargs):
    print "***** Configure Device and Execution Profile *****"
    try:
#        configure_profile.config_profiles()
        edit_profile.edit_profiles(get_buildname(), args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])
    except TestException, e:
        print inred(e.value)

'''    
def test_prepare(option, opt_str, value, parser):
    print "***** Prepare for Automation Test *****"
    print("")
    try:
        args = check_if_config_device()
        print args.split()
        SetupEnvironment(args.split())
    except TestException, e:
        print inred(e.value)
    print "Done..."


def test_execute(option, opt_str, value, parser):
    print "***** Execute Test Case *****"
    try:
        args = check_if_config_device()
        user_input = raw_input('do you want to switch module, y/n?')
        if user_input.lower() == 'y':
            print ('1. va \
                        2. omx')
            user_input = raw_input('please select the number or quit(q): ')
            while True:
                if str(user_input) == '1':
                    args = args + ' -m va'
                    break
                elif str(user_input) == '2':
                    args = args + ' -m omx'
                    break
                elif user_input.lower() == 'q':
                    break
                else:
                    user_input = raw_input('invalid number, input again:')
        TestProgram(args.split())
    except TestException, e:
        print inred(e.value) 
        
    
def test_report(option, opt_str, value, parser):
    build_name = get_build_name()
    print "***** Summarize Test Result to %s%s/test_report*****" %(config.RESULT_PATH, build_name)
    case_result_report.test_report()
    print "done..."
'''

def test_upload(option, opt_str, value, parser, *args, **kwargs):
    print "***** Update Test Result in TMS*****"
    upload_result.upload_result_to_tms(args[0], args[1])
    
def get_buildname():
    status, output = commands.getstatusoutput("ls -l " + conf.TEST_REPO)
    if output.find("No such file or directory") != -1:
        print output
        exit(-1)
    if output == '':
        exit(-1)
    dirList = output.split('\n')
    casefolderList = []
    for eachdir in dirList:
        casefolderList.append(eachdir.split(' ')[-1])
    i = 0
    for each_path in casefolderList:
        if os.path.isfile(conf.TEST_REPO + each_path):
            print each_path[:-4]
            return each_path[:-4]
            
def clip_upload(option, opt_str, value, parser, *args, **kwargs):
    upload_clip.upload_clip_to_mediaserver(args[1])

def main(argv):
    
    #obtain build name and ingredient name
    build = ''
    ingredient = ''
    platform = ''
    deviceOS = ''
    connect = ''
    serialNumber = ''
    executionOS = ''
    testsuiteUrl = ''
    workDir = ''
    clipDir = ''
    vaClipDir = ''
    systemBoot = ''
    try:
        for arg in argv:
            if arg == "--build":
                build = argv[argv.index(arg) + 1]
            if arg == "--ingredient":
                ingredient = argv[argv.index(arg) + 1]
            if arg == "--platform":
                platform = argv[argv.index(arg) + 1]
            if arg == "--deviceOS":
                deviceOS = argv[argv.index(arg) + 1]
            if arg == "--connect":
                connect = argv[argv.index(arg) + 1]
            if arg == "--serialNumber":
                serialNumber = argv[argv.index(arg) + 1]
            if arg == "--executionOS":
                executionOS = argv[argv.index(arg) + 1]
            if arg == "--testsuiteUrl":
                testsuiteUrl = argv[argv.index(arg) + 1]
            if arg == "--workDir":
                workDir = argv[argv.index(arg) + 1]
            if arg == "--clipDir":
                clipDir = argv[argv.index(arg) + 1]
            if arg == "--vaClipDir":
                vaClipDir = argv[argv.index(arg) + 1]
            if arg == "--systemBoot":
                systemBoot = argv[argv.index(arg) + 1]
    except IndexError, e:
        print inred("Error: you must input the parameter value of " + arg)
        exit(-1)
    
    try:
        usage = "usage: python %prog [options]"
        rapidrunner = OptionParser(usage=usage)
        rapidrunner.add_option("-d", "--download", action="callback", callback=test_download, callback_args=(ingredient, build), help="Download execution case list to local from TMS.")
        rapidrunner.add_option("-l", "--list", action="callback", callback=test_list, help="check the execution case list.")
        rapidrunner.add_option("-c", "--configure", action="callback", callback=test_configure, callback_args=(platform, deviceOS, connect, serialNumber, executionOS, testsuiteUrl, workDir, clipDir, vaClipDir, systemBoot), help="configure device and execution profile.")
#        rapidrunner.add_option("-r", "--report", action="callback", callback=test_report, help="report test result.")
        rapidrunner.add_option("-u", "--upload", action="callback", callback=test_upload, callback_args=(ingredient, build), help="update execution result to TMS.")
#        rapidrunner.add_option("-p", "--prepare", action="callback", callback=test_prepare, help="prepare for test.")
#        rapidrunner.add_option("-e", "--execute", action="callback", callback=test_execute, help="test execution.")
        rapidrunner.add_option("-p", "--uploadClip", action="callback", callback=clip_upload, callback_args=(ingredient, build), help="upload result clips to media server.")
        rapidrunner.add_option("--build", help="build name in TMS")
        rapidrunner.add_option("--ingredient", help="ingredient name in TMS")
        rapidrunner.add_option("--platform", help="element Platform in device profile")
        rapidrunner.add_option("--deviceOS", help="element OS in device profile")
        rapidrunner.add_option("--connect", help="element Connect in device profile")
        rapidrunner.add_option("--serialNumber", help="element serialNumber in device profile")
        rapidrunner.add_option("--executionOS", help="element OS in execution profile")
        rapidrunner.add_option("--testsuiteUrl", help="element DUTTestsuite in execution profile")
        rapidrunner.add_option("--workDir", help="element DUTWorkDirectory in execution profile")
        rapidrunner.add_option("--clipDir", help="element ClipsDirectory in execution profile")
        rapidrunner.add_option("--vaClipDir", help="element VAClipsDirectory in execution profile")
        rapidrunner.add_option("--systemBoot", help="element SystemBoot in execution profile")
        
        (options, args) = rapidrunner.parse_args()
        
    except TestException, e:
        print inred(e.value)

if __name__ == "__main__":
    main(sys.argv)