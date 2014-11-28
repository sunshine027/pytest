import sys
import os
import time
import commands
from exceptions import IOError, AttributeError, KeyError
from subprocess import Popen, PIPE

from conf import path
from tools.dataparser import DataParser
from exception.testexception import TestException
from tools.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite
from tools.shellExecutor import executeShell
from tools.mediainfoParser import parseMediaInfo
from pytest import TestCase
from tools.logcat import logcat_dec, get_locat_file_name
from tools.client import execute_command_on_server
from tools.get_execution_info import get_clip_path

FRONT_SENSOR_RESOLUTION = ['720p', '480p', 'high', 'lowqvga', 'low', 'mms', 'youtube', 'D1', 'lowcif']
BACK_SENSOR_RESOLUTION = ['1080p', '720p', '480p', 'high', 'lowqvga', 'low', 'mms', 'youtube', 'D1', 'lowcif']
DEFAULT_CAMERA = 'Default_Camera'

class utility:
    def __init__(self, step_id, par_dict, dev_dict, crt, caseFolderName, all_monitor_thread_dict, stepType, platform):
    #def __init__(self, step_id, par_dict, dev_dict, crt, caseFolderName, all_monitor_thread_dict, stepType):
        self.step_id = step_id
        self.dict = par_dict
        self.dict1 = dev_dict
        self.crt = crt
        self.caseFolderName = caseFolderName
        self.stepType = stepType
        self.platform = platform
        self.all_monitor_thread_dict = all_monitor_thread_dict
         
        print "Parameter List: "
        for key in self.dict:
            print key , ": " , self.dict[key]
        self.rt_dict = {}

        crt_list = list(crt)
        print "Pass Criterion: "
        crt_exist = 0
        for crt_no in crt_list:
            if cmp(crt_no.text,'Off'):
                print crt_no.tag, crt_no.text
                crt_exist = 1
        if crt_exist == 0:
            print "None"
        print ' '
        if not self.dict1.get('Connect', ''):
            raise TestException("Error: no Connect element found in device's profile, while running")
        if not self.dict1.get('Connect', '') in ['ssh', 'adb']:
            raise TestException("Error: the text of Connect element should be ssh or adb in device's profile ")            
        if not cmp(self.dict1['Connect'], 'ssh'):
            self.prefix = ''  
            from tools.client import sshAccessor as accessor

        if not cmp(self.dict1['Connect'], 'adb'):
            self.prefix = '/system/bin/'
            from tools.client import adbAccessor as accessor

        self.cli = accessor(self.dict1)
        self.Clip_Path = get_clip_path()

    def decode(self):
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        #obtain clip format
        format = self.dict['Format']

        try:
            input = self.Clip_Path + self.dict['Format'] + '/' + self.dict['InputFile']
            inputpath = self.Clip_Path + self.dict['Format']
	    print inputpath
        except KeyError:
            raise TestException("Error: no InputFile element found in Parameter element ")
        print "test..." 
        
        cmd = "sf-yuv -f " + input + " -o test"
        print cmd
        self.rt_dict.setdefault('cmd', cmd)

        if self.stepType == 0 or self.stepType == 10:
            if self.stepType == 10:
                return "noResult"
        
        if self.stepType == 0 or self.stepType == 20:
             #execute in remote device
            print "Execute Output: \n"
            stdout,stderr = self.cli.execute_test(cmd, self.step_id) 
	    
            print stdout
            #print stderr
            TestCase(self.stepType).kill_monitor_thread(self.all_monitor_thread_dict, path.result_path + '/' + self.caseFolderName + '/', self.dict1, False, self.step_id)

        #'''
            str_line = stdout.split('\n')
            
            for linenum in str_line:
                if linenum.find('[sf-yuv]md5:') != -1:
                    self.rt_dict['MD5'] = linenum.split(':')[1]
            if not self.rt_dict.has_key('MD5'):
                self.rt_dict['MD5'] = ''
                
            cmd = 'rm -rf ' + self.Clip_Path + self.dict['Format'] + '/test/'
            self.cli.execute(cmd)
            cmd = 'rm -rf ' + input
            self.cli.execute(cmd)
        #'''
            return self.rt_dict 

           
