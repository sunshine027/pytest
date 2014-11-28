#!/usr/bin/env python

import os
import sys
from xml.parsers.expat import ExpatError
import xml.etree.ElementTree as ET
from optparse import OptionParser

from exception.testexception import TestException
from tools import XMLParser
from tools.install_dependence_package import install_paramiko, install_android_sdk, push_busybox
from tools.device_configure import connect_wifi, change_avstreaming_ip
from tools.create_configure import create_path_file
from tools.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite
from tools.client import execute_command_on_server, adbAccessor as accessor
from tools.file_directory_tool import clear_unuseful_file
from tools.get_execution_info import get_build_name
from common_module.check_profile import check_device_profile, check_adb_connect
import conf
    
class SetupEnvironment:

    def __init__(self, argv=None):
        if argv is None:
            self.argv = sys.argv[1:]
            
    def run(self):
        try:
            self.args, self.help = self.parseArgs(self.argv)
            self.parse_device_profile()
            check_adb_connect(self.devcfg)
            # pushing busy box must run first, because the following step will use command in it
            if self.args.get('busybox') is not None :
                self._push_busybox()
            if  self.args.get('connect_wifi') is not None:
                self._connect_wifi()
            if  self.args.get('open_fps') is not None:
                self._open_fps()
            if self.args.get('execution') is not None :
                self._run_execution()
            # ip should be written to path.py, so run after execution
            if self.args.get('ip') is not None:
                self.change_ip()
        except TestException, e:
            print inred(e.value)
            
    def _run_execution(self):
        self._open_fps()
        self.parse_execution_profile()
        create_path_file(self.args.get('execution'))
        self.pre_command_run()
        # only video item
        if self.args.get('type') is None:
            EnvironmentForVideo(self.acc, self.devcfg, self.ftpAddress, self.args.get('platform')).run()
        else:
            self.autoSetupVideo()
          
    def change_ip(self):
        ip = self.args.get('ip')
        result = change_avstreaming_ip(ip)
        if result:
            print ingreen('##################### Set IP for AV_Streaming Server Successfully! ####################')
        
    def parse_execution_profile(self):
        #get items in execution.xml
        try:
            root = ET.parse(self.args['execution']).getroot()
        except IOError, e:
            raise TestException("Error: the file: " + str(self.args['execution']) + " can not found")
        except ExpatError, e:
            raise TestException("Error: the file: " + str(self.args['execution']) + " is invalid!") 
        try:
            self.buildname = root.find('name').text
        except AttributeError, e:
            raise TestException("Error: no name element found in " + str(self.args['execution']))
        if self.buildname is None or self.buildname.strip() == '':
            raise TestException("Error: the text of name element can't be empty in " + str(self.args['execution']))
        
        setup_ele = root.find('Setup')
        if setup_ele is None:
            raise TestException("Error: no Setup element found in " + str(self.args['execution']))
        try:
            self.ftpAddress = setup_ele.find('DUTTestsuite').text
        except AttributeError, e:
            raise TestException("Error: no DUTTestsuite element found in " + str(self.args['execution']))
        if self.ftpAddress is None or self.ftpAddress.strip() == '':
            raise TestException("Error: the text of DUTTestsuite element can't be empty in " + str(self.args['execution']))
             
    def parse_device_profile(self):
        if self.args.get('device') is None:
            # if no -d, we'll use the default device profile.
            self.devcfg = conf.DEFAULT_DEVICE_PATH 
        else:
            self.devcfg = self.args.get('device')
        check_device_profile(self.devcfg)
        xmlparser = XMLParser.XMLParser(self.devcfg)
        self.dev_dict = xmlparser.ClientParser() 
        self.acc = accessor(self.dev_dict)
            
    def _connect_wifi(self):
        result = connect_wifi(self.devcfg)
        if result:
            print ingreen('##################### Connect Wifi Successfully #############################')
        else:
            print inred('##################### Fail to Connect Wifi #############################')
                    
    def _open_fps(self):
        self.acc.execute('setprop debug.dump.log 1')
        print ingreen('##################### Open FPS in Logcat Successfully##################### ')
    
    def _push_busybox(self):
        result = push_busybox(self.devcfg)
        if result:
            print ingreen('##################### Push Busybox to Device Successfully #####################')
        else:
            print inred('##################### Fail to Push Busybox to Device #####################')
        
    def pre_command_run(self):
        self.acc.execute_on_host('root')
        self.acc.execute_on_host('remount')
        
    def parseArgs(self, argv): 
        usage = "usage: python %prog [options]"
        parser = OptionParser(usage=usage)
        parser.add_option('-e', '--execution', help="execution's configure file")
        parser.add_option('-d', '--device', help="optional, device's configure file")
        parser.add_option('-t', '--type', help="optional, v(video)")
        parser.add_option('-c', '--connect_wifi', action='store_false', help="connect to wiki")
        parser.add_option('-o', '--open_fps', action='store_false', help="open fps in logcat")
        parser.add_option('-i', '--ip', help="set IP for av streaming")
        parser.add_option('-p', '--platform', help="set platform")
        parser.add_option('-b', '--busybox', action='store_false', help="push busybox to device")
        if len(argv) == 0:
            print parser.print_help()
            sys.exit(0)
        else:
            options, args = parser.parse_args(argv)
            if (options.execution is None and options.connect_wifi is None and options.ip is None) and options.open_fps is None and options.busybox is None:
                print inred("ERROR: make sure you should input one of -e, -c, -o, -b or -i !")
                print parser.print_help()
            else:
                return (options.__dict__, parser.print_help)
            
    def autoSetupVideo(self):
        video = EnvironmentForVideo(self.acc, self.devcfg, self.ftpAddress, self.args.get('platform'))
        video._push_busybox()
        video.download_suite()
        video.push_suite()
        video.chmod_suite()
        video.install_android_sdk()
#        video.install_paramiko()

         
class EnvironmentForVideo(SetupEnvironment):
    
    def __init__(self, acc, dev_profile, ftpAddress, platform):
        self.acc = acc
        self.platform = platform
        self.devcfg = dev_profile
        xmlparser_2 = XMLParser.XMLParser(dev_profile)
        self.dev_dict = xmlparser_2.ClientParser() 
        self.ftpAddress = ftpAddress
        self.download_item_pass_list = []
        self.fail_download_variable_tool_list = []
        self.fail_download_constant_tool_list = []
        
    def run(self):
        print inpurple('Welcome to RapidRunner Framework!')
        print '1. Push Busybox to Device'
        print '2. Download and Push TestTools to Device'
        print '3. Install Android SDK'
        print '4. Run All Step'
        print '0. Exit'
        userInput = ''
        self.pre_command_run()
        while userInput != '0':
            userInput = raw_input ('Please select your operation:')
            if userInput == '1':
                self._push_busybox()
            elif userInput == '2':
                self.download_suite()
                self.push_suite()
                self.chmod_suite()
            elif userInput == '3':
                self.install_android_sdk()
            elif userInput == '4':
                self._push_busybox()
                self.download_suite()
                self.push_suite()
                self.chmod_suite()
                self.install_android_sdk()
#                self.install_paramiko()
            elif userInput == '0':
                pass
            else:
                print inred("Wrong operation number!")
                       
    def install_android_sdk(self):
        result = install_android_sdk(self.devcfg)
        if result:
            print ingreen('##################### Install Android SDK Successfully #######################')
        else:
            print inred('##################### Fail to Install Android SDK ##########################')
    
    def download_suite(self):
        self.download_item_pass_list = []
        self.fail_download_variable_tool_list = []
        self.fail_download_constant_tool_list = []
        platform = self.dev_dict['Platform']
        if platform == 'MFLD': 
            file_list = ['h264vld', 'libtestsuite_common.so', 'mpeg4vld', 'penwell_jpegEncode',  'va_encode', 'vc1vld', 'mediarecorder', 'mediaplayer', 'mediaframeworktest.apk','sf-yuv' ,'sf-playback','sf-recorder', 'imageencoder']
        elif platform == 'MRST': 
            file_list = ['h264vld', 'libtestsuite_common.so', 'mpeg4vld', 'va_encode', 'vc1vld']
        #delete old files 
        for item in file_list:
            clear_unuseful_file('./' + item)
        ip = self.get_ip()
        if ip:
            result = self.check_connection(ip)
            if result:
                for item in file_list:
                    execute_command_on_server('wget --no-proxy %s%s -t 1 -T 20' %(self.ftpAddress, item), False)
                    cmd = 'test -f ' + str('./' + item) + " && echo 'File exists' || echo 'File not found'"
                    stdout, stderr = execute_command_on_server(cmd, False)
                    if stdout.strip().find('File not found') != -1:
                        self.fail_download_variable_tool_list.append(item)
                    elif stdout.strip().find('File exists') != -1:
                        self.download_item_pass_list.append(item)
            else:
                self.fail_download_variable_tool_list.extend(file_list)
        else:
            self.fail_download_variable_tool_list.extend(file_list)
        if self.fail_download_variable_tool_list:
            print inred('##################### Fail to Download tool(s): ' + ', '.join(self.fail_download_variable_tool_list) + inred('  ######################'))
            print inred('Warning: Please check if they exist under ' + self.ftpAddress + ', you can ignore this error message if these tools are not required for your execution')
        
        # download tools that doesn't need to be compiled for every build
        tool_list = ['matrix', 'cjpeg', 'djpeg']
        another_tool = 'imagedecoder'
        result = self.check_connection('172.16.123.192')
        if result:
            if self.platform is not None and self.platform.strip().lower() == 'ctp':
                url = 'http://172.16.123.192/media_resource/rapidrunner_tool/ctp/'
            else:
                url = 'http://172.16.123.192/media_resource/rapidrunner_tool/mfld/' 
            
            for tool in tool_list:
                execute_command_on_server("wget --no-proxy %s%s -t 1 -T 30 " %(url, tool), False)
                cmd = 'test -f ' + str('./') + tool + " && echo 'File exists' || echo 'File not found'"
                stdout, stderr = execute_command_on_server(cmd, False)
                if stdout.strip().find('File not found') != -1:
                    self.fail_download_constant_tool_list.append(tool)
                elif stdout.strip().find('File exists') != -1:
                    self.download_item_pass_list.append(tool)
            
            folder = ''
            build_name = get_build_name()
            if build_name.lower().strip().find('r3') != -1:
                folder = 'ICS/'
            elif build_name.lower().strip().find('r4') != -1:
                folder = 'JB/'
            if folder:
                downloadurl = url + folder + another_tool
                execute_command_on_server("wget --no-proxy %s -T 30" %downloadurl, False)
                cmd = 'test -f ' + str('./') + another_tool + " && echo 'File exists' || echo 'File not found'"
                stdout, stderr = execute_command_on_server(cmd, False)
                if stdout.strip().find('File not found') != -1:
                    self.fail_download_constant_tool_list.append(another_tool)
                elif stdout.strip().find('File exists') != -1:
                    self.download_item_pass_list.append(another_tool)
        else:
            self.fail_download_constant_tool_list.extend(tool_list)
            self.fail_download_constant_tool_list.extend(another_tool)
        if self.fail_download_constant_tool_list:
            print inred('##################### Fail to Download tool(s) ' + ','.join(self.fail_download_constant_tool_list) +' ######################')
            print inred('Warning: Contact developer if you need these tools in execution, or else ignore this error.')
#        if (not self.fail_download_variable_tool_list) and (not self.fail_download_constant_tool_list):
#            print ingreen('##################### Download TestTool Successfully ######################')

    def get_ip(self):
        if self.ftpAddress.startswith('http://'):
            items = self.ftpAddress.split('/')[2]
            if len(items.split('.')) == 4:
                if len([item for item in items.split('.') if item.isdigit()]) == 4:
                    return items
        return ''
            
    def check_connection(self, ip):
        cmd = 'ping ' + ip + ' -w 3'
        stdout, stderr = execute_command_on_server(cmd, False)
        if stdout.find('bytes from ' + ip.strip()) != - 1:
            return True
        else:
            return False
         
    def push_suite(self): 
        target_path = ''
        push_fail_list = []
        push_success_list = []
        for file_num in self.download_item_pass_list:
            if file_num.endswith('apk'):
                self.pre_command_run()
                cmd = ' install -r ' + file_num
                stdout, stderr = self.acc.execute_on_host(cmd)
                if stdout.lower().find('success') == -1:
                    push_fail_list.append(file_num)
            else:
                if file_num[-2:] == 'so':
                    target_path = '/system/lib/'
                elif (file_num[-2:]== 'ko' or file_num == 'adbd.sh') and file_num != "matrix.ko":
                    target_path = '/data/'
                else:
                    target_path = '/system/bin/'
                self.acc.upload(file_num, target_path)
                cmd = 'test -f ' + str( target_path + file_num) + " && echo 'File exists' || echo 'File not found'"
                stdout, stderr = self.acc.execute(cmd)
                if stdout.strip().find('File not found') != -1:
                    push_fail_list.append(file_num)
        if push_fail_list:
            print inred('##################### Fail to Push ' + ','.join(push_fail_list) + ' to Device ##############')
#        else:
#            print ingreen('##################### Push ' + ', '.join( [item for item in self.download_item_pass_list if item not in push_fail_list] ) + ' to Device Successfully ################')
       #delete old files 
        for item in self.download_item_pass_list:
            clear_unuseful_file('./' + item)
             
    def chmod_suite(self):
        fail_chmod_list = []
        for file_num in self.download_item_pass_list:
            if file_num[-2:] in ['so', 'ko'] or file_num.strip().endswith('apk'):
                pass
            else:
                result = self.acc.execute('chmod 4777 /system/bin/%s'%(file_num) )
                if result == ('', ''):
                    pass
                else:
                    fail_chmod_list.appand(file_num)
        if fail_chmod_list:
            print inred('##################### Fail to change mode' + ', '.join(fail_chmod_list) + ' ####################')
        if len(self.download_item_pass_list) != 0:
           print ingreen('##################### Push  ' + ', '.join([item for item in self.download_item_pass_list if item not in fail_chmod_list]) + ' into Device Successfully ##############')
    
    def install_paramiko(self):
        result = install_paramiko()
        if result:
            print ingreen('##################### Install Paramiko Successfully.#####################')
        else:
            print inred('##################### Fail to Install Paramiko, Check If You Run This by Root #####################')
        
if __name__ == "__main__":
    SetupEnvironment().run()

