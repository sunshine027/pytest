import sys
import os
import time
import commands
from exceptions import IOError, AttributeError, KeyError
from subprocess import Popen, PIPE

from conf import path
from tools.get_execution_info import get_clip_path, get_result_path
from tools.dataparser import DataParser
from tools.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite
from tools.shellExecutor import executeShell
from tools.mediainfoParser import parseMediaInfo
from tools.logcat import logcat_dec, get_locat_file_name
from tools.client import execute_command_on_server
from tools.install_dependence_package import check_android_sdk
from exception.testexception import TestException
from pytest import TestCase
import conf

FRONT_SENSOR_RESOLUTION = ['720p', '480p', 'high', 'lowqvga', 'low', 'mms', 'youtube', 'D1', 'lowcif']
BACK_SENSOR_RESOLUTION = ['1080p', '720p', '480p', 'high', 'lowqvga', 'low', 'mms', 'youtube', 'D1', 'lowcif', '1080p_modified']

class utility:
    '''
        # real execution, and we will get the actual value here.
        # if can't get value for one item due to tool reason, please set it to 'empty_value'
    '''
    def __init__(self, step_id, par_dict, dev_dict, crt, caseFolderName, all_monitor_thread_dict, stepType, platform):
        self.step_id = step_id
        self.par_dict = par_dict
        self.dev_dict = dev_dict
        self.crt = crt
        self.caseFolderName = caseFolderName
        self.stepType = stepType
        self.platform = platform
        self.all_monitor_thread_dict = all_monitor_thread_dict
 
        print "Parameter List: "
        for key in self.par_dict:
            if key.strip() == 'InputFile':
                if self.par_dict[key].find('http:') != -1 or self.par_dict[key].find('rtp:') != -1:
                    new_url = self.get_http_url(self.par_dict[key])
                    print key, ': ', new_url
                else:
                    print key , ": " , self.par_dict[key]
            else:
                print key , ": " , self.par_dict[key]
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
        if not self.dev_dict.get('Connect', ''):
            raise TestException("Error: no Connect element found in device's profile, while running")
        if not self.dev_dict.get('Connect', '') in ['ssh', 'adb']:
            raise TestException("Error: the text of Connect element should be ssh or adb in device's profile ")            
        if not cmp(self.dev_dict['Connect'], 'ssh'):
            self.prefix = ''  
            from tools.client import sshAccessor as accessor

        if not cmp(self.dev_dict['Connect'], 'adb'):
            self.prefix = '/system/bin/'
            from tools.client import adbAccessor as accessor

        self.cli = accessor(self.dev_dict)
        self.Clip_Path = get_clip_path()
       
    def check_network(self):
        network_connect_flag = False
        count = 0
        try:
            ip = path.IP 
        except AttributeError, e:
            raise TestException("Error: no ip in path.py, please run python setup.py -i 172.16.123.119 first.")
        while not network_connect_flag:
            cmd = 'ping ' + ip + ' -w 5'
            stdout, stderr = self.cli.execute(cmd)
            if stdout.find('bytes from ' + ip.strip()) != - 1 and stdout.find('seq=0') != -1:
                network_connect_flag = True
            else:
                count += 1
                cmd = 'python setup.py -c'
                execute_command_on_server(cmd, False)
                time.sleep(10)
            if count == 3:
                raise TestException("Error: can not connect to 9L02")
    
    def get_ip(self):
        try:
            return path.IP 
        except AttributeError, e:
           raise TestException("Error: no ip in path.py, please run python setup.py -i 172.16.123.114 first.")
       
    def get_http_url(self, input_file):
        ip = self.get_ip()
        # http://172.16.123.119/httplive/kauai_HLS/kauai_Medium_256KB.m3u8
        items = input_file.split('/')[3:]
        http_url = 'http://' + ip + '/' + '/'.join(items)
        return http_url
    
    
    def get_rtp_url(self, input_file):
        ip = self.get_ip()
        # rtsp://172.16.123.119:8088/test26
        items = input_file.split(':')[2:]
        rtp_url = 'rtsp://' + ip + ':' + ':'.join(items)
        return rtp_url
    
    def decode(self):
        for item in self.par_dict:
            if self.par_dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        try:
            duration = float(self.par_dict['Duration'])
        except KeyError:
            raise TestException("Error: no Duration element found in Parameter element ")
        except ValueError:
            raise TestException("Error: the text of Duration element should be number in Parameter element ")
        input_data = self.par_dict['InputFile']
        if (self.caseFolderName.strip().lower().find('av_streaming') != -1 or self.caseFolderName.strip().lower().find('post_process') != -1) and self.caseFolderName.strip().lower().find('http') != -1:
            cmd = 'am start -a android.intent.action.VIEW -d ' + self.get_http_url(input_data) + ' -t video/*'
            self.check_network()
        elif (self.caseFolderName.strip().lower().find('av_streaming') != -1 or self.caseFolderName.strip().lower().find('post_process') != -1) and self.caseFolderName.strip().lower().find('rtp') != -1:
            cmd = 'am start -a android.intent.action.VIEW -d ' + self.get_rtp_url(input_data)
            self.check_network()
        else:
            #obtain clip format
            format = self.par_dict['Format']
            try:
                input = self.Clip_Path + self.par_dict['Format'] + '/' + input_data
            except KeyError:
                raise TestException("Error: no InputFile element found in Parameter element ")
            cmd = "am start -a android.intent.action.VIEW -d file://" + input + " -t video/*"
        self.rt_dict.setdefault('cmd', cmd)

        if self.stepType == 0 or self.stepType == 10:
            if self.stepType == 10:
                return "noResult"
        if self.stepType == 0 or self.stepType == 20:
             #execute in remote device
            print "Execute Output: \n"
            self.cli.execute_test(cmd, self.step_id)
            time.sleep(duration)
            '''
            for get md5 value
#            md5_value = ''
#            cmd = 'sf-yuv -f ' + input + ' -o test'
#            print cmd
#            stdout, stderr = self.cli.execute_test(cmd, self.step_id)
#            print stdout
#            print stderr
#            if stdout.find('sf-yuv fail') != -1:
#                md5_value = 'fail'
#            else:
#                lines = stdout.split(os.linesep)
#                for line in lines:
#                    if line.find('[sf-yuv]md5') != -1:
#                        md5_value = line.split(':')[1]
#            print 'md5_value: ', md5_value
#            self.rt_dict['MD5'] = md5_value
#            cmd = 'rm -rf ' + self.Clip_Path + self.par_dict['Format'] + '/test/'
#            self.cli.execute(cmd)
#            cmd = 'rm -rf ' + input
#            self.cli.execute(cmd)
            '''
            TestCase(self.stepType).kill_monitor_thread(self.all_monitor_thread_dict, path.result_path + '/' + self.caseFolderName + '/', self.dev_dict, False, self.step_id)
            #waiting for new FILE generated
            print "waiting for logcat file generated ......"
            logcat_file_name = get_locat_file_name(self.all_monitor_thread_dict)
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
            
            #rename FILE into step_id.logcat
            os.system("cd " + path.result_path + '/' + self.caseFolderName + " ; mv " + logcat_file_name + " " + str(self.step_id) + ".logcat")
        
         
        if self.stepType == 0 or self.stepType == 30:
            if self.stepType == 30:
                return "noResult"
            
        return self.rt_dict 

    def encode(self):
       pass

    def jpeg_encode(self):
       pass 
        
    def camera(self):
        result = check_android_sdk()
        if not result:
            raise TestException('Error: please run setup.py to install Android SDK')
        if self.stepType == 0 or self.stepType == 10:
            if self.stepType == 10:
                return "noResult"
        
        if self.stepType == 0 or self.stepType == 20:
            print "\nCase preparation: \n"
            SOURCE_CLIP_PATH = '/sdcard/DCIM/Camera/'
            TARGET_CLIP_PATH = get_result_path() + 'VideoCapture/'
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
                
            duration = self.par_dict.get('Duration', '')
            try:
                duration = int(duration)
            except (ValueError, TypeError), e:
                raise TestException("Error:  no Duration element found or the value of Duration element  must be a number")
            
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
            if self.platform is not None and self.platform.lower() == 'mfld_r3':
                cmd = 'am start -n com.android.camera/.Camera'
            elif self.platform is not None and self.platform.lower() == 'mfld_r4':
                cmd = 'am start -n com.android.gallery3d/com.android.camera.CameraLauncher'
            elif self.platform is not None and self.platform.lower() == 'ctp':
                cmd = 'am start -n com.android.gallery3d/com.android.camera.CameraLauncher'
            else:
                raise TestException('Error: please specify platform: ctp or mfld_r3 or mfld_r4')
            self.cli.execute(cmd)
            
            if self.caseFolderName.lower().find('zoom_max') != -1:
                pre_script_directory = 'default_camera_zoom'
                script_name = script_pre + resolution.strip() + '.mr'
            elif self.caseFolderName.lower().find('timelapse') != -1:
                pre_script_directory = 'default_camera_timelapse'
                timelapse = self.par_dict.get('Timelapse', '').strip()
                if timelapse == '':
                    raise TestException("Error: no Timelapse element found.")
                timelapse_dict = {'off': '0s', '1': '1s', '1.5': '1s5', '2': '2s', '2.5': '2s5', 
                                  '3': '3s', '5': '5s', '10': '10s'}
                script_name = script_pre + resolution.strip() + '-' + timelapse_dict[timelapse.strip().lower()] + '.mr'
            else:
                pre_script_directory = 'default_camera'
                script_name = script_pre + resolution.strip() + '.mr'
                
            if self.platform.lower().find('mfld') != -1:
                script_folder = 'MFLD'
            elif self.platform.lower() == 'ctp':
                script_folder = 'CTP'
                
            cmd = 'resource/monkeyrunner/scripts/monkey_playback.py ' + ' resource/video_caputure_script/' + script_folder + '/' + pre_script_directory + '/' + script_name
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
            self.cli.download(TARGET_CLIP_PATH + outputName + " ", path.resultClip_path + '/' + self.caseFolderName + '/')
            
            #obtain mediainfo result on result clip            
            mediainfo_dict = parseMediaInfo(path.resultClip_path + '/' + self.caseFolderName + '/' + outputName)
            for eachItem in mediainfo_dict:           
                self.rt_dict.setdefault(eachItem, mediainfo_dict[eachItem])
            return self.rt_dict 
#            elif self.caseFolderName.lower().find('portrait') != -1:
#                print 'no implement'
#                sys.exit(0)
            

        
    
        
            
            
            
            
            
            
            
            
            
            
