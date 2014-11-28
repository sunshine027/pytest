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
            if key == "VideoCodec":
                self.videocodec = self.dict[key]
            elif key == "Resolution":
                self.resolution = self.dict[key]
            elif key == "Duration":
                self.duration = self.dict[key]
            elif key == "Bitrate":
                self.bitrate = self.dict[key]
            elif key == "FPS":
                self.fps = self.dict[key]

            print key , ": " , self.dict[key]
            print ""
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
        print ''
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

    def play(self):
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        #obtain clip format
        format = self.dict['Format']

        try:
            input = self.Clip_Path + self.dict['Format'] + '/' + self.dict['OutputFile']
	    print input
        except KeyError:
            raise TestException("Error: no InputFile element found in Parameter element ")
        print "test..." 
        #try:
            #duration = float(self.dict['Duration'])
            #print "duration = 10"
        #except KeyError:
            #raise TestException("Error: no Duration element found in Parameter element ")
        
        #if duration == "Off":
            #raise TestException("Error: Duration element cannot be Off ")

        print "cmd called"
        #cmd = "sf-Recorder -f " + input + " "
        cmd = "sf-Recorder -f " + input + " -s " + self.resolution + " -t " + self.duration + " -b " + self.bitrate + " -r " + self.fps + " -v 2"
        #cmd = "sf-Recorder -f /mnt/sdcard/video-tests/Clips/test1.mp4"
        print cmd
        self.rt_dict.setdefault('cmd', cmd)

        if self.stepType == 0 or self.stepType == 10:
            if self.stepType == 10:
                return "noResult"
        
        if self.stepType == 0 or self.stepType == 20:
             #execute in remote device
            print "Execute Output: \n"
            self.cli.execute_test(cmd, self.step_id) 
            cmd = "sf-Playback -f " + input + " "
            print cmd
            stdout,stderr = self.cli.execute_test(cmd, self.step_id) 
	    
            #time.sleep(10)
            #time.sleep(duration)
            #print stdout
            #print stderr
            TestCase(self.stepType).kill_monitor_thread(self.all_monitor_thread_dict, path.result_path + '/' + self.caseFolderName + '/', self.dict1, False, self.step_id)

            print stdout
        #'''
            str_line = stdout.split('\n')
            #self.rt_dict['isPass'] = "pass"
            for linenum in str_line:
                #if linenum.find('play too fast!') != -1 or linenum.find('play too slow!') != -1 or linenum.find('video delay too much!') != -1  or linenum.find('video delay more than 40ms') != -1:
                #self.rt_dict['isPass'] = "fail"
                #else
                #self.rt_dict['isPass'] = "pass"

                if linenum.find('[playback]resolution:') != -1:
                    self.rt_dict['Resolution'] = linenum.split(':')[1]
                if linenum.find('[playback]duration:') != -1:
                    self.rt_dict['Duration'] = linenum.split(':')[1]
                    #print resolution 
                #elif linenum.find('Duration') != -1:
                    #duration = linenum.split(':')[1]
                    #print duration 
                #if linenum.find('Bitrate') != -1:
                    #bitrate = linenum.split(':')[1]
                    #print bitrate 
                #if linenum.find('FPS') != -1:
                    #fps = linenum.split(':')[1]
                    #print fps 
        #'''
            return self.rt_dict 

           
