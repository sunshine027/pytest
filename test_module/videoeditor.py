import sys
import os
import time
import commands
from exceptions import IOError, AttributeError, KeyError
from subprocess import Popen, PIPE
from xml.etree import ElementTree as et

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

FRONT_SENSOR_RESOLUTION = ['720p', '480p']
BACK_SENSOR_RESOLUTION = ['1080p', '720p', '480p']
DEFAULT_CAMERA = 'Default_Camera'
RESOLUTION_DICT = {'1080p': '1920x1088', '720p': '1280x720', '480p': '720x480'}

class utility:
    def __init__(self, step_id, par_dict, dev_dict, crt, caseFolderName, all_monitor_thread_dict, stepType, platform):
        self.step_id = step_id
        self.par_dict = par_dict
        self.dev_dict = dev_dict
        self.crt = crt
        self.caseFolderName = caseFolderName
        self.stepType = stepType
        self.all_monitor_thread_dict = all_monitor_thread_dict
        self.platform = platform
        
        print "Parameter List: "
        for key in self.par_dict:
            print key , ": " , self.par_dict[key]
        print ""
        
        self.rt_dict = {}
        crt_list = list(crt)
        print "Pass Criterion: "
        crt_exist = 0
        for crt_no in crt_list:
            if cmp(crt_no.text.strip().lower(),'off'):
                print crt_no.tag, crt_no.text
                crt_exist = 1
        if crt_exist == 0:
            print "None"
        print ''
        
        if not self.dev_dict.get('Connect', ''):
            raise TestException("Error: no Connect element found in device's profile, while running")
        if not self.dev_dict.get('Connect', '') in ['ssh', 'adb']:
            raise TestException("Error: the text of Connect element should be ssh or adb in device's profile ")            
        if not cmp(self.dev_dict['Connect'], 'ssh'):
            self.prefix = ''  
            from tools.client import sshAccessor as accessor
        elif not cmp(self.dev_dict['Connect'], 'adb'):
            self.prefix = '/system/bin/'
            from tools.client import adbAccessor as accessor
        self.cli = accessor(self.dev_dict)
        self.Clip_Path = get_clip_path()

    def codec(self):
        
        for item in self.par_dict:
            if self.par_dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")

        #obtain clip format
        if self.stepType == 0 or self.stepType == 10:
            if self.stepType == 10:
                return "noResult"
        
        if self.stepType == 0 or self.stepType == 20:
            case_path = path.test_repo + '/case_profile/' + self.caseFolderName.strip() + '/run.xml'
            tree = et.parse(case_path)
            root = tree.getroot()
            try:
                clip_ele_list = root.find('URL').findall('Clip')
            except Exception, e:
                raise TestException("Error: no URL found, VideoEditor case should have at least one xml file to be download.")
            xml_name = ''
            for clip_ele in clip_ele_list:
                clip_url = clip_ele.text.strip()
                clip_name = clip_url.split('/')[-1]
                if clip_name.strip().endswith('.xml'):
                    xml_name = clip_name.strip()
            if xml_name == '':
                raise TestException("Error: No xml file found in Clip element, please check the case profile.")
            format = self.par_dict['Format']
            
            # push xml to /data/, and rename to VideoEditorTest.xml
            cmd = 'mv ' + self.Clip_Path + format + '/' + xml_name + ' /data/'
            stdout, stderr = self.cli.execute(cmd)
            if stdout.find('No such file or directory') != -1:
                raise TestException('Error: fail to run command: ' + cmd)
            cmd = 'mv /data/' + xml_name + ' /data/VideoEditorTest.xml'
            self.cli.execute(cmd)
            check_cmd = "test -f /data/VideoEditorTest.xml  && echo 'File exists' || echo 'File not found'"
            stdout, stderr = self.cli.execute(check_cmd)
            if str(stdout).strip() == 'File not found':
                raise TestException("Error: rename failed: " + cmd)
            
            # check clip should be got by download or by capture
            try:
                clipsource = self.par_dict['ClipSource']
            except KeyError:
                raise TestException("Error: no ClipSource element found.")
            if clipsource.strip() == 'True':
                pass
            else:
                self.capture()
            
            # delete old output file
            try:
                output_file_name = self.par_dict['OutputFile'].strip()
            except KeyError:
                raise TestException("Error: no OutputFile element found.")
            cmd = 'rm -rf ' + self.Clip_Path + format + '/' + output_file_name
            self.cli.execute(cmd)
            
            # run am command
            cmd = 'am instrument -e class com.android.mediaframeworktest.functional.videoeditor.VideoEditorTest#execute -w com.android.mediaframeworktest/.MediaFrameworkTestRunner'
            self.cli.execute(cmd)
            
            # check if output file generate successfully
            result_cmd = "test -f "+ self.Clip_Path + format + '/' + output_file_name + " && echo 'File exists' || echo 'File not found'"
            stdout, stderr = self.cli.execute(result_cmd)
            if str(stdout).strip() == 'File not found':
                print inred('fail to generate outputfile: ' + output_file_name)
            else:
                # pull output file to case result
                os.system("mkdir -p " + path.resultClip_path + '/' + self.caseFolderName + '/')
                self.cli.download(self.Clip_Path + format + '/' + output_file_name + " ", path.resultClip_path + '/' + self.caseFolderName + '/')
                
            # kill monitor not finished
            TestCase(self.stepType).kill_monitor_thread(self.all_monitor_thread_dict, path.result_path + '/' + self.caseFolderName + '/', self.dev_dict, False, self.step_id)
            #waiting for new FILE generated
            print "waiting for logcat file generated ......"
            logcat_file_name = get_locat_file_name(self.all_monitor_thread_dict)
            while(not os.path.exists(path.result_path + '/' + self.caseFolderName + '/' + logcat_file_name)):
                time.sleep(1)
            #rename FILE into step_id.logcat
            os.system("cd " + path.result_path + '/' + self.caseFolderName + " ; mv " + logcat_file_name + " " + str(self.step_id) + ".logcat")
        
            #obtain mediainfo result on result clip            
            mediainfo_dict = parseMediaInfo(path.resultClip_path + '/' + self.caseFolderName + '/' + output_file_name)
            for eachItem in mediainfo_dict:           
                self.rt_dict.setdefault(eachItem, mediainfo_dict[eachItem])
            return self.rt_dict
            
        if self.stepType == 0 or self.stepType == 30:
            if self.stepType == 30:
                return "noResult"
        return self.rt_dict
    
    def capture(self):
        
        SOURCE_CLIP_PATH = '/sdcard/DCIM/Camera/'
        TARGET_CLIP_PATH = get_clip_path() + self.par_dict['Format'] + '/'
        self.cli.execute("rm -rf " + SOURCE_CLIP_PATH + '*')
        self.cli.execute("mkdir -p " + TARGET_CLIP_PATH)
        sensor_flag = self.par_dict.get('Sensor', ' ')
        if sensor_flag is None or sensor_flag.strip() == '' or sensor_flag.strip().lower() not in ['front', 'back']:
            raise TestException('ERROR: No Sensor element found or the value of Sensor element should be Front or Back')
        if sensor_flag.lower() == 'front':
            sensor_resolution = FRONT_SENSOR_RESOLUTION
            script_pre = 'Default_Cam_Front_'
        else:
            sensor_resolution = BACK_SENSOR_RESOLUTION
            script_pre = 'Default_Cam_Back_'
        resolution = self.par_dict.get('Resolution', '')
        if resolution.strip() == '1080p_modified':
            self.cli.execute_on_host('root')
            self.cli.execute_on_host('remount')
            self.cli.upload('resource/settings/media_profiles.xml', '/etc/')
            self.cli.execute_on_host('reboot')
            time.sleep(120)
            self.cli.execute('svc power stayon usb')
            execute_command_on_server('./resource/settings/unlock.sh ' + self.dev_dict['serialNumber'], False)
        if resolution is None or resolution.strip() == '' or resolution.strip() not in sensor_resolution:
            raise TestException("Error:  no Resolution element found or the value of Resolution element  must be the value in " + ','.join(sensor_resolution))
        if self.platform is None:
            script_folder = 'MFLD'
        elif self.platform.lower() == 'ctp':
            script_folder = 'CTP'
        cmd = 'am start -n com.android.camera/.Camera'
        self.cli.execute(cmd)
        cmd = 'resource/monkeyrunner/scripts/monkey_playback.py ' + ' resource/video_caputure_script/' + script_folder + '/default_camera/' + script_pre + resolution.strip() + '.mr'
        print cmd
        stdout, stderr = execute_command_on_server(cmd, False)
        # press back key, and exit camera UI
        cmd = 'input keyevent 4'
        self.cli.execute(cmd)
        self.cli.execute(cmd)
        # get the clip name for mediainfo
        stdout, stderr = self.cli.execute("ls -al " + SOURCE_CLIP_PATH + ' | grep ^-')
        dirList = stdout.split('\n')
        outputName = ''
        for eachdir in dirList:
            outputName = outputName + (eachdir.split(' ')[-1])
        outputName = outputName.strip()
        #pull the clip to test_repo
        os.system("mkdir -p " + path.resultClip_path + '/' + self.caseFolderName + '/')
        self.cli.execute('mv '+ SOURCE_CLIP_PATH + outputName + ' ' + TARGET_CLIP_PATH)
        
        #rename clip
        try:
            cmd = 'mv ' + TARGET_CLIP_PATH + '/' + outputName + ' ' + TARGET_CLIP_PATH + '/' + self.par_dict['InputFile'].strip()
        except KeyError:
            raise TestException("Error: no InputFile element found.")
        self.cli.execute(cmd)
        self.cli.download(TARGET_CLIP_PATH +  self.par_dict['InputFile'].strip() + " ", path.resultClip_path + '/' + self.caseFolderName + '/')
        
        #obtain mediainfo result on result clip            
        mediainfo_dict = parseMediaInfo(path.resultClip_path + '/' + self.caseFolderName + '/' +  self.par_dict['InputFile'].strip())
        
        if mediainfo_dict.get('Resolution').strip() != RESOLUTION_DICT.get(resolution).strip():
            raise TestException("Error: recorded clip's resolution" + mediainfo_dict.get('Resolution').strip() + " isn't right with criteria: " + resolution)
            
            
            
            
            
            
            
            
