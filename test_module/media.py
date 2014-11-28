import sys
import os
import time
from conf import path
from exceptions import IOError, AttributeError, KeyError
from multiprocessing import Process

from tools.dataparser import DataParser
from exception.testexception import TestException
from tools.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite
from tools.logcat import logcat_dec, get_locat_file_name
from tools.mediainfoParser import parseMediaInfo
from tools.get_execution_info import get_clip_path, get_result_path
from pytest import TestCase

class utility:
    def __init__(self, step_id, par_dict, dev_dict, crt, caseFolderName, all_monitor_thread_dict, stepType, platform):
        self.step_id = step_id
        self.dict = par_dict
        self.dict1 = dev_dict
        self.crt = crt
        self.caseFolderName = caseFolderName
        self.all_monitor_thread_dict = all_monitor_thread_dict
        self.stepType = stepType
        self.platform = platform
        
        print "Parameter List: "
        for key in self.dict:
            print key , ": " , self.dict[key]
        #print self.dict
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

    def decode(self):
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        
        #obtain clip format
        format = self.dict['Format']
        
        #obtain inputfile
        input = self.Clip_Path + self.dict['Format'] + '/' + self.dict['InputFile']
        
        #obtain mode
        if not cmp(self.dict['Mode'], 'Off'):
            mode = ''
        elif not cmp(self.dict['Mode'], 'gt'):
            mode = "--mode \\>"
        elif not cmp(self.dict['Mode'], 'lt'):
            mode = "--mode \\<"  
        else:  
            mode = "--mode " + self.dict['Mode']
        
        #obtain render
        if not cmp(self.dict['Render'], 'ov'):
            render = "--render ov"
        elif not cmp(self.dict['Render'], 'ts'):
            render = "--render ts"
        else:
            render = ''
            
        '''    
        #obtain hdmi
        if not cmp(self.dict['HDMI'], 'clone'):
            hdmi = "--hdmi clone"
        elif not cmp(self.dict['HDMI'], 'extend'):
            hdmi = "--hdmi extend"
        else:
            hdmi = ''
        '''
            
        #obtain seedTo
        if not cmp(self.dict['SeekTo'], None) or not cmp(self.dict['SeekTo'], 'Off') or not cmp(self.dict['SeekTo'], 'off'):
            seedTo = ''
        else:
            seedTo = "--seekto " + self.dict['SeekTo']
            
        #obtain SeekInterval
        if not cmp(self.dict['SeekInterval'], None) or not cmp(self.dict['SeekInterval'], 'Off') or not cmp(self.dict['SeekInterval'], 'off'):
            duration = ''
        else:
            duration = "--duration " + self.dict['SeekInterval']    
            
        #generate cmd
        cmd = "mediaplayer --input_file " + input + ' ' + mode + ' ' + render + ' ' + seedTo + ' ' + duration
        print ""
        self.rt_dict.setdefault('cmd', cmd)
        
        if self.stepType == 0 or self.stepType == 10:
            if self.stepType == 10:
                return "noResult"
        
        if self.stepType == 0 or self.stepType == 20:
            #delete old logcat file
            try:
                logcat_file_name = get_locat_file_name(self.all_monitor_thread_dict)
                os.system("rm -rf " + path.result_path + '/' + self.caseFolderName + '/' + logcat_file_name)
            except Exception, e:
                pass
            
            #execute in remote device
            print "Execute Output: \n"
            self.cli.execute_test(cmd, self.step_id)
            try:
                outfile = open('log' + str(self.step_id), 'r') 
            except IOError, e:
                print inred("Error: cannot generate log.")
                os.system("touch log" + str(self.step_id))
            stdout = outfile.read()
            outfile.close()
            
            TestCase(self.stepType).kill_monitor_thread(self.all_monitor_thread_dict, path.result_path + '/' + self.caseFolderName + '/', self.dict1, False, self.step_id)
            
            #waiting for new logcat FILE generated
            print "waiting for logcat file generated ......"
            while(not os.path.exists(path.result_path + '/' + self.caseFolderName + '/' + logcat_file_name)):
                time.sleep(1)
                       
            #obtain values from logcat 
            logcat_dict = {}
            logcat_dict = logcat_dec(path.result_path + '/' + self.caseFolderName + '/' + logcat_file_name)
            try:
                for item in logcat_dict:
                    self.rt_dict.setdefault(item, logcat_dict[item])
            except TypeError:
                #raise TestException ("No logcat FILE found")
                pass
            
            #rename logcat FILE into step_id.logcat
            os.system("cd " + path.result_path + '/' + self.caseFolderName + " ; mv  " + logcat_file_name + "  "+ str(self.step_id) + ".logcat")
        
        if self.stepType == 0 or self.stepType == 30:
            if self.stepType == 30:
                return "noResult"
            
        return self.rt_dict
    
    def encode(self):
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        
        #obtain outputfile
        output = get_result_path() + self.dict['OutputFile']
        
        # check if output exist
        cmd = 'test -d ' + get_result_path() + " && echo 'directory exists' || echo 'directory not found'"
        stdout, stderr = self.cli.execute(cmd)
        print stdout, stderr
        if stdout.strip() == 'directory not found':
            cmd = 'mkdir -p ' + get_result_path()
            self.cli.execute(cmd)
        #obtain bitrate
        if not cmp(self.dict['VideoBitrate'], 'Off'):
            bitrate = '' 
        else:  
            bitrate = "--bitrate " + self.dict['VideoBitrate']
            
        #obtain framerate
        if not cmp(self.dict['Framerate'], 'Off'):
            framerate = '' 
        else:  
            framerate = "--framerate " + self.dict['Framerate']
            
        #obtain audiocodec
        if not cmp(self.dict['Audiocodec'].replace(' ',''), 'amr'):
            ac = "--audiocodec amr"
        elif not cmp(self.dict['Audiocodec'].replace(' ',''), 'awb'):
            ac = "--audiocodec awb"
        elif not cmp(self.dict['Audiocodec'].replace(' ',''), 'aac'):
            ac = "--audiocodec aac"
        else:
            ac = '--audiocodec aac'
            
        #obtain videocodec
        if not cmp(self.dict['Videocodec'], 'h263'):
            vc = "--videocodec h263"
        elif not cmp(self.dict['Videocodec'], 'h264'):
            vc = "--videocodec h264"
        elif not cmp(self.dict['Videocodec'], 'mpeg4'):
            vc = "--videocodec mpeg4"
        else:
            vc = ''
            
        #obtain format
        if not cmp(self.dict['Format'], '3gp'):
            format = "--format 3gp"
        elif not cmp(self.dict['Format'], 'mp4'):
            format = "--format mp4"
        else:
            format = ''
            
        #obtain resolution
        if not cmp(self.dict['Resolution'], 'Off'):
            resolution = '' 
        else:  
            resolution = "--resolution " + self.dict['Resolution']
            
        #obtain duration
        if not cmp(self.dict['Duration'], 'Off'):
            duration = '' 
        else:  
            duration = "--duration " + self.dict['Duration']
            
        #obtain mode
        if not cmp(self.dict['Mode'], 'av'):
            mode = "--mode av"
        elif not cmp(self.dict['Mode'], 'vo'):
            mode = "--mode vo"
        elif not cmp(self.dict['Mode'], 'ao'):
            mode = "--mode ao"
        else:
            mode = ''

        #obtain audio bitrate
        if not cmp(self.dict['AudioBitrate'], 'Off'):
            audiobitrate = ''
        else:
            audiobitrate = "--audiobitrate " + self.dict['AudioBitrate']

        #obtain audio sampling rate
        if not cmp(self.dict['AudioSampleRate'], 'Off'):
            audiosamplerate = ''
        else:
            audiosamplerate = "--samplingrate " + self.dict['AudioSampleRate'] + " --EnableChSampling"
            
        #generate cmd
        cmd = "mediarecorder --output " + output + ' ' + bitrate + ' ' + framerate + ' ' + ac + ' ' + vc + ' ' + format + ' ' + resolution + ' ' + duration + ' ' + mode + ' ' + audiobitrate + ' ' + audiosamplerate
#        cmd = "mediarecorder --output " + output + ' ' + bitrate + ' ' + framerate + ' ' + ac + ' ' + vc + ' ' + format + ' ' + resolution + ' ' + duration + ' ' + mode + ' ' + audiosamplerate
        print ""
        print cmd
        print ""
        self.rt_dict.setdefault('cmd', cmd)
        
        if self.stepType == 0 or self.stepType == 10:
            if self.stepType == 10:
                return "noResult"
        
        if self.stepType == 0 or self.stepType == 20:
            
            #execute in remote device
            print "Execute Output: \n"
            self.cli.execute_test(cmd, self.step_id)
            try:
                outfile = open('log' + str(self.step_id), 'r') 
            except IOError, e:
                print inred("Error: cannot generat log.")
                os.system("touch log" + str(self.step_id)) 
            stdout = outfile.read()
            outfile.close()
            
            #pull result clip to host
            os.system("mkdir -p " + path.resultClip_path + '/' + self.caseFolderName + '/')
            self.cli.download(output, path.resultClip_path + '/' + self.caseFolderName + '/')
            
            #obtain mediainfo result from result clip
            mediainfo_dict = parseMediaInfo(path.resultClip_path + '/' + self.caseFolderName + '/' + self.dict['OutputFile'])
            for eachItem in mediainfo_dict:
                self.rt_dict.setdefault(eachItem, mediainfo_dict[eachItem])
                               
        if self.stepType == 0 or self.stepType == 30:
            if self.stepType == 30:
                return "noResult"
            
        return self.rt_dict
    




