import sys
import os
import commands
from conf import path
import conf
from exceptions import IOError, AttributeError, KeyError

from tools.dataparser import DataParser
from exception.testexception import TestException
from tools.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite
from tools.get_execution_info import get_clip_path, get_result_path

class utility:
    def __init__(self, step_id, par_dict, dev_dict, crt, caseFolderName, all_monitor_thread_dict, stepType, platform):
        self.step_id = step_id
        self.dict = par_dict
        self.dict1 = dev_dict
        self.crt = crt
        self.caseFolderName = caseFolderName
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
       
       
    def audioDecode(self):
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        try:
            if self.dict['Format'] in ['mp3', 'amr', 'awb', 'aac']:
                pass
            else:
                print inred("Error: Invalid text in Format element in case configuration file. You may not find the clip.")
            format = self.dict['Format']
        except KeyError:
            raise TestException("Error: no Format element found in Parameter element.")
        try:
            input = self.Clip_Path + self.dict['Format'] + '/' + self.dict['InputFile']
        except KeyError:
            raise TestException("Error: no InputFile element found in Parameter element ")
        try:
            output = get_result_path() + self.dict['OutputFile']
        except KeyError:
            raise TestException("Error: no OutputFile element found in Parameter element ")
        try:
            playback = self.dict['Playback'] 
            if playback == 'Off':
                playback = '0'
        except KeyError:
            raise TestException("Error: no Playback element found in Parameter element ")
        
        typeString = input.split('.')[-1]
        if typeString == 'mp3':
            type = '0'
        elif typeString == 'amr':
            type = '1'
        elif typeString == 'awb':
            type = '2'
        elif typeString == 'aac':
            type = '3'
        else:
            print inred("Unknown input file extension name, type set to 0.")
            type = '0'
        
        cmd = "AudioDecTest " + input + ' ' + output + ' ' + type + ' ' + playback
        print "Command:"
        print cmd
        print ""
        self.rt_dict.setdefault('cmd', cmd)
        
        if self.stepType == 0 or self.stepType == 10:
            if self.stepType == 10:
                return "noResult"
        
        if self.stepType == 0 or self.stepType == 20:
            #execute in remote device 
            '''
            print "Execute Output: "
            stdout,stderr = self.cli.execute(cmd)
            if stdout == '':
                raise TestException("Error: No content in log. You may use a wrong test tool or wrong platform ")
            outfile = open('log' + str(self.step_id), 'w+')
            outfile.writelines(stderr)
            outfile.writelines(stdout)
            outfile.close()
            '''
            
            print "Execute Output: \n"
            self.cli.execute_test(cmd, self.step_id)
            try:
                outfile = open('log' + str(self.step_id), 'r') 
            except IOError, e:
                print inred("Error: cannot generat log.")
                os.system("touch log" + str(self.step_id)) 
            stdout = outfile.read()
            outfile.close()
            
            #download output file
            self.cli.download(get_result_path() + self.dict['OutputFile'], path.result_path + '/' + self.caseFolderName + '/')
            
            #obtain MD5 value
            status, output = commands.getstatusoutput("md5sum " + path.result_path + '/' + self.caseFolderName + '/' + self.dict['OutputFile'])
            if status == 0:
                md5 = output.split(' ')[0]
            else:
                md5 = ''
                print inred("cannot obtain MD5 value because no result clip generated or no md5sum command!")
                
            #delete result clip
            status, output = commands.getstatusoutput("rm -rf " + path.result_path + '/' + self.caseFolderName + '/' + self.dict['OutputFile'])
            self.cli.execute("rm " + get_result_path() + self.dict['OutputFile'])
                            
            self.rt_dict.setdefault('MD5', md5)  
       
        if self.stepType == 0 or self.stepType == 30:
            if self.stepType == 30:
                return "noResult"
            
        return self.rt_dict
        
    def audioEncode(self):
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        try:
            if not cmp(self.dict['Format'], 'wav'):
                pass
            else:
                raise TestException("Error: Invalid text in Codec element in case configuration file.")
        except KeyError:
            raise TestException("Error: no Format element found in Parameter element.")
        try:
            input = self.Clip_Path + self.dict['Format'] + '/' + self.dict['InputFile']
        except KeyError:
            raise TestException("Error: no InputFile element found in Parameter element ")
        try:
            output = get_result_path() + self.dict['OutputFile']
        except KeyError:
            raise TestException("Error: no OutputFile element found in Parameter element ")
        
        typeString = output.split('.')[-1]
        if typeString == 'aac':
            type = '0'
        elif typeString == 'amr':
            type = '1'
        elif typeString == 'awb':
            type = '2'
        else:
            print inred("Unknown output file extension name, type set to 0.")
            type = '0'
                
        cmd = "AudioEncTest " + input + ' ' + output + ' ' + type
        print "Command:"
        print cmd
        print ""
        self.rt_dict.setdefault('cmd', cmd)
        
        if self.stepType == 0 or self.stepType == 10:
            if self.stepType == 10:
                return "noResult"
        
        if self.stepType == 0 or self.stepType == 20:
            #execute in remote device
            '''
            print "Execute Output: "
            stdout,stderr = self.cli.execute(cmd)
            if stdout == '':
                raise TestException("Error: No content in log. You may use a wrong test tool or wrong platform ")
            outfile = open('log' + str(self.step_id), 'w+')
            outfile.writelines(stderr)
            outfile.writelines(stdout)
            outfile.close()
            '''
            
            print "Execute Output: \n"
            self.cli.execute_test(cmd, self.step_id)
            try:
                outfile = open('log' + str(self.step_id), 'r') 
            except IOError, e:
                print inred("Error: cannot generat log.")
                os.system("touch log" + str(self.step_id)) 
            stdout = outfile.read()
            outfile.close()
            
            #download output file
            self.cli.download(get_result_path() + self.dict['OutputFile'], path.result_path + '/' + self.caseFolderName + '/')
            
            #obtain MD5 value
            status, output = commands.getstatusoutput("md5sum " + path.result_path + '/' + self.caseFolderName + '/' + self.dict['OutputFile'])
            if status == 0:
                md5 = output.split(' ')[0]
            else:
                md5 = ''
                print inred("cannot obtain MD5 value because no result clip generated or no md5sum command!")
                
            #delete result clip
            status, output = commands.getstatusoutput("rm -rf " + path.result_path + '/' + self.caseFolderName + '/' + self.dict['OutputFile'])
            self.cli.excute("rm " + get_result_path() + self.dict['OutputFile'])
                            
            self.rt_dict.setdefault('MD5', md5)  
        
        if self.stepType == 0 or self.stepType == 30:
            if self.stepType == 30:
                return "noResult"
            
        return self.rt_dict
    
    def encode(self):
        
        print "Command for va_log detection:"
                
        #enable va_log
        stdout,stderr = self.cli.execute("echo \\\"LIBVA_TRACE=/data/1\\\" > /etc/libva.conf")
        
        #delete original 
        stdout,stderr = self.cli.execute("rm -rf /data/1.*")
        
        print ""
        
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        
        try:
            if not cmp(self.dict['Format'], 'H264'):
                encodeFormat = 7
            elif not cmp(self.dict['Format'], 'MPEG4'):
                encodeFormat = 4
            elif not cmp(self.dict['Format'], 'H263'):
                encodeFormat = 3
            else:
                raise TestException("Error: Invalid text in Format element in case configuration file.")
        except KeyError:
            raise TestException("Error: no Format element found in Parameter element.")
        
        try:
            input = self.Clip_Path + "YUV/" + self.dict['InputFile']
        except KeyError:
            raise TestException("Error: no InputFile element found in Parameter element ")
        try:
            output = get_result_path() + self.dict['OutputFile']
        except KeyError:
            raise TestException("Error: no OutputFile element found in Parameter element ")
        
        try:
            resolution = self.dict['Resolution']
        except KeyError:
            raise TestException("Error: no Resolution element found in Parameter element ")
        try:
            width = resolution.split('x')[0]
            height = resolution.split('x')[1]
        except IndexError:
            raise TestException("Error: the text in Resolution element must be in the format of NUMBERxNUMBER ")
         
        try:
            speed = self.dict['Speed']
            if speed == 'Off':
                speed = '0'
        except KeyError:
            raise TestException("Error: no Speed element found in Parameter element ") 
        
        try:
            bitRate = self.dict['BitRate']
            if bitRate == 'Off':
                bitRate = '0'
        except KeyError:
            raise TestException("Error: no BitRate element found in Parameter element ")
        
        try:
            framerate = self.dict['Framerate']
            if framerate == 'Off':
                framerate = '15'
        except KeyError:
            raise TestException("Error: no Framerate element found in Parameter element ")
        
        try:
            level = self.dict['Level'].replace('L', '')
            if encodeFormat == 7:
                if level == 'Off':
                    level = '0'
                elif level == '1':
                    level = '1'
                elif level == '1b':
                    level = '2' 
                elif level == '1.1':
                    level = '4' 
                elif level == '1.2':
                    level = '8'  
                elif level == '1.3':
                    level = '10'
                elif level == '2.0':
                    level = '20'
                elif level == '2.1':
                    level = '40'
                elif level == '2.2':
                    level = '80'
                elif level == '3.0':
                    level = '100'
                elif level == '3.1':
                    level = '200'
                elif level == '3.2':
                    level = '400'
                elif level == '4.0':
                    level = '800'
                elif level == '4.1':
                    level = '1000'
                elif level == '4.2':
                    level = '2000'
                elif level == '5.0':
                    level = '4000'
                elif level == '5.1':
                    level = '8000'
            elif encodeFormat == 3:
                if level == 'Off':
                    level = '0'
                elif level == '10':
                    level = '1'
                elif level == '20':
                    level = '2'
                elif level == '30':
                    level = '4'
                elif level == '40':
                    level = '8'
                elif level == '50':
                    level = '10'
                elif level == '60':
                    level = '20'
                elif level == '70':
                    level = '40'
            elif encodeFormat == 4:
                if level == 'Off':
                    level = '0'
                elif level == '1':
                    level = '1'
                elif level == '2':
                    level = '2'
                elif level == '3':
                    level = '4'
                elif level == '4':
                    level = '8'
                elif level == '5':
                    level = '7FFFFFFF'
        except KeyError:
            raise TestException("Error: no Level element found in Parameter element ")
        
        try:
            nalsize = self.dict['NalSize']
            if nalsize == 'Off':
                nalsize = '0'
        except KeyError:
            raise TestException("Error: no NalSize element found in Parameter element ")
        
        try:
            CIFrames = self.dict['CIFrames']
            if CIFrames == 'Off':
                CIFrames = '0'
        except KeyError:
            raise TestException("Error: no CIFrames element found in Parameter element ")
        
        try:
            profile = self.dict['Profile']
            if encodeFormat == 7:
                if profile == 'Off':
                    profile = '0'
                elif profile == 'BP':
                    profile = '1'
                elif profile == 'MP':
                    profile = '2' 
                elif profile == 'EP':
                    profile = '4' 
                elif profile == 'HP':
                    profile = '8'  
            elif encodeFormat == 3:
                if profile == 'Off':
                    profile = '0'
                elif profile == 'BP':
                    profile = '1'
            elif encodeFormat == 4:
                if profile == 'Off':
                    profile = '0'
                elif profile == 'SP':
                    profile = '1'
                elif profile == 'MP':
                    profile = '8'
        except KeyError:
            raise TestException("Error: no Profile element found in Parameter element ")
        
        try:
            rcMode = self.dict['RcMode']
            if rcMode == 'VBR':
                rcMode = '1'
            elif rcMode == 'CBR':
                rcMode = '2'
            else:
                rcMode = '0'
        except KeyError:
            raise TestException("Error: no RcMode element found in Parameter element ")
        try:
            VUIEnable = self.dict['VUIEnable']
            if VUIEnable == 'Off':
                VUIEnable = '0'
        except KeyError:
            raise TestException("Error: no VUIEnable element found in Parameter element ")
        
        try:
            testtype = self.dict['TestType']
        except KeyError:
            raise TestException("Error: no TestType element found in Parameter element ")
        
        try:
            referenceframe = self.dict['Referenceframe']
            if referenceframe == 'Off':
                referenceframe = '0'
        except KeyError:
            raise TestException("Error: no Referenceframe element found in Parameter element ")
        
        try:
            testtimes = self.dict['TestTimes']
        except KeyError:
            raise TestException("Error: no TestTimes element found in Parameter element ")
        
        if encodeFormat == 7:
            cmd = "VideoEncTest" + ' ' + input + ' ' + output + ' ' + width + ' ' + height + ' ' + speed + ' ' + bitRate + ' ' + framerate + ' ' + str(encodeFormat) + ' ' + level + ' ' + nalsize + ' ' + CIFrames + ' ' + profile + ' ' + rcMode + ' ' + VUIEnable + ' ' + testtype + ' ' + referenceframe + ' ' + testtimes 
        else:
            cmd = "VideoEncTest" + ' ' + input + ' ' + output + ' ' + width + ' ' + height + ' ' + speed + ' ' + bitRate + ' ' + framerate + ' ' + str(encodeFormat) + ' ' + rcMode + ' ' + CIFrames + ' ' + profile + ' ' + level + ' 0 0 ' + testtype + ' ' + referenceframe + ' ' + testtimes
       
        print "Command:"
        print cmd
        print ""
        self.rt_dict.setdefault('cmd', cmd)
        
        if self.stepType == 0 or self.stepType == 10:        
            #download clip if it does not exist in self.Clip_Path + 'YUV/'
            stdout, stderr = self.cli.execute("ls " + input)
            flag = stdout.find("No such file or directory")
            if flag < 0:
                pass
            else:
                print '\nDownloading %s ......' %self.dict['InputFile']
                status, output = commands.getstatusoutput("wget --no-proxy " + conf.VIDEO_CLIP_DOWNLOAD_PATH + self.dict['InputFile'])
                if status != 0:
                    print inred("Error: failed download " + self.dict['InputFile'] + ", maybe the clip storing address is invalid!\n")
                else:
                    print ingreen(self.dict['InputFile'] + " downloaded successfully.\n")
                    print ("Push " + self.dict['InputFile'] + " into device ......")
                    self.cli.upload(self.dict['InputFile'], self.Clip_Path + 'YUV/')
                    os.system("rm -rf " + self.dict['InputFile'])
                
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
            
            #obtain FPS
            str1 = stdout.find("Average frames per second") + 28
            str2 = stdout[str1: str1+50].find('\n')
            fps = stdout[str1:str1+str2].replace('\n', '').replace(' ', '').replace('\r', '')
            self.rt_dict.setdefault('FPS', fps)
            
            #obtain attrib[1].value
            stdout_text,stderr = self.cli.execute("head /data/1.* -n 20")
            flag = stdout_text.find("attrib_list[1].value") + 23
            if flag == 22 :
                print inred("No attrib_list[1].value found in va_log.")
                attrib_value = "Off"
            else:
                attrib_value = stdout_text[flag : flag+10]                
            self.rt_dict.setdefault('AttribValue', attrib_value)
                    
            #download output file
            #self.cli.download(get_result_path() + self.dict['OutputFile'], path.result_path + '/' + self.caseFolderName + '/')
            #self.cli.download(get_result_path() + self.dict['OutputFile'] + ".log", path.result_path + '/' + self.caseFolderName + '/')
        
            #delete files
            #self.cli.execute("rm " + path.Result + self.dict['OutputFile']) 
        
        if self.stepType == 0 or self.stepType == 30:
            if self.stepType == 30:
                return "noResult"
            
        return self.rt_dict
        
        
    def decode(self):
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        try:
            if not cmp(self.dict['Format'], 'H264'):
                videoFormat = 1
            elif not cmp(self.dict['Format'], 'MPEG4'):
                videoFormat = 2
            elif not cmp(self.dict['Format'], 'H263'):
                videoFormat = 3
            elif not cmp(self.dict['Format'], 'VC1'):
                videoFormat = 4
            else:
                raise TestException("Error: Invalid text in Format element in case configuration file.")
        except KeyError:
            raise TestException("Error: no Format element found in Parameter element.")
        try:
            input = self.Clip_Path + self.dict['Format'] + '/' + self.dict['InputFile']
        except KeyError:
            raise TestException("Error: no InputFile element found in Parameter element ")
        try:
            output = get_result_path() + self.dict['OutputFile']
        except KeyError:
            raise TestException("Error: no OutputFile element found in Parameter element ")
        
        try:
            resolution = self.dict['Resolution'] 
        except KeyError:
            raise TestException("Error: no Resolution element found in Parameter element ")
        try:
            maxwidth = resolution.split('x')[0]
            maxheight = resolution.split('x')[1]
        except IndexError:
            raise TestException("Error: the text in Resolution element must be in the format of NUMBERxNUMBER ")

        try:
            decodeSpeed = self.dict['DecodeSpeed'] 
        except KeyError:
            raise TestException("Error: no DecodeSpeed element found in Parameter element ")
        
        cmd = "VideoDecTest " + input + ' ' + output + ' ' + str(videoFormat) + ' ' + str(maxwidth) + ' ' + str(maxheight) + ' ' + decodeSpeed 
        print "Command:"
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
            
            #obtain FPS
            str1 = stdout.find("(seconds)") + 12
            str2 = stdout[str1: str1+30].find('\n')
            fps = stdout[str1:str1+str2].replace('\n', '').replace(' ', '').replace('\r', '')
            self.rt_dict.setdefault('FPS', fps)
            
            #obtain YV12_CRC
            YV12_CRC = stdout.split('\n')[-2].replace(' ', '').replace('\r', '')
            self.rt_dict.setdefault('YV12_CRC', YV12_CRC)
            
            #download output file
            #self.cli.download(get_result_path() + self.dict['OutputFile'], path.result_path + '/' + self.caseFolderName + '/')
            
            #delete files
            self.cli.execute("rm " + get_result_path() + self.dict['OutputFile']) 
        
        if self.stepType == 0 or self.stepType == 30:
            if self.stepType == 30:
                return "noResult"
            
        return self.rt_dict
        
        
