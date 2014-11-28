import sys
import os
from conf import path
from common_module.dataparser import DataParser
from exceptions import IOError, AttributeError, KeyError
from common_module.testexception import TestException
from common_module.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite

class vcTS:
    def __init__(self, step_id, par_dict, dev_dict, crt, cam, casename):
        self.step_id = step_id
        self.dict = par_dict
        self.dict1 = dev_dict
        self.crt = crt
        self.casename = casename
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
            from common_module.client import sshAccessor as accessor

        if not cmp(self.dict1['Connect'], 'adb'):
            self.prefix = '/system/bin/'
            from common_module.client import adbAccessor as accessor
        self.cli = accessor(self.dict1)
        try:
            #self.Clip_Path = path.vd_clip
            self.Clip_Path = "/cache/Clips/video-tests/Clips/"
        except AttributeError, e:
           raise TestException("Error: no vd_clip in path.py, maybe there is something wrong during run setup.py ")
       
       
    def audioDecode(self):
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        try:
            if not cmp(self.dict['Codec'], 'mp3'):
                pass
            elif not cmp(self.dict['Codec'], 'acc'):
                pass
            else:
                raise TestException("Error: Invalid text in Codec element in case configuration file.")
        except KeyError:
            raise TestException("Error: no Codec element found in Parameter element.")
        try:
            input = self.Clip_Path + self.dict['Codec'] + '/' + self.dict['InputFile']
        except KeyError:
            raise TestException("Error: no InputFile element found in Parameter element ")
        try:
            output = self.Clip_Path + self.dict['Codec'] + '/' + self.dict['OutputFile']
        except KeyError:
            raise TestException("Error: no OutputFile element found in Parameter element ")
        try:
            format = self.dict['Format'] 
        except KeyError:
            raise TestException("Error: no Format element found in Parameter element ")
        
        cmd = "omx_mp3_dec_test " + input + ' ' + output + ' ' + format
        print "Command:"
        print cmd
        print ""
        self.rt_dict.setdefault('cmd', cmd)
        
        #execute in remote device
        print "Execute Output: "
        stdout,stderr = self.cli.execute(cmd)
        if stdout == '':
            raise TestException("Error: No content in log. You may use a wrong test tool or wrong platform ")
        outfile = open('log' + str(self.step_id), 'w+')
        outfile.writelines(stderr)
        outfile.writelines(stdout)
        outfile.close()
        
        #download output file
        self.cli.download(self.Clip_Path + self.dict['Codec'] + '/' + self.dict['OutputFile'], path.result_path + '/' + self.casename + '/')
        
        #count md5 value
        res = os.system("./resource/md5sum " + path.result_path + '/' + self.casename + '/' + self.dict['OutputFile'] + " >> md5info")
        if res == 256:
            print inred("No wav file generated.")      
        try:
            md5file = open('md5info')
        except IOError, e:
            md5 = ''
        else:
            md5 = md5file.readlines()[0].split(' ')[0]
        md5file.close()
        
        #delete files
        os.system("rm md5info")
        self.cli.execute("rm " + self.Clip_Path + self.dict['Codec'] + '/' + self.dict['OutputFile']) 
                        
        self.rt_dict.setdefault('MD5', md5)        
        return self.rt_dict
        
    def audioEncode(self):
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        try:
            if not cmp(self.dict['Codec'], 'wav'):
                pass
            else:
                raise TestException("Error: Invalid text in Codec element in case configuration file.")
        except KeyError:
            raise TestException("Error: no Codec element found in Parameter element.")
        try:
            input = self.Clip_Path + self.dict['Codec'] + '/' + self.dict['InputFile']
        except KeyError:
            raise TestException("Error: no InputFile element found in Parameter element ")
        try:
            output = self.Clip_Path + self.dict['Codec'] + '/' + self.dict['OutputFile']
        except KeyError:
            raise TestException("Error: no OutputFile element found in Parameter element ")
        try:
            format = self.dict['Format'] 
        except KeyError:
            raise TestException("Error: no Format element found in Parameter element ")
        if 'Bitrate' in self.dict:
            command = "omx_amr_enc_test"
            try:
                bitrate = self.dict['Bitrate'] 
            except KeyError:
                raise TestException("Error: no Format element found in Parameter element ")
        else:
            command = "omx_aac_enc_test"
            bitrate = ''
        
        cmd = command + ' ' + input + ' ' + output + ' ' + format + ' ' + bitrate
        print "Command:"
        print cmd
        print ""
        self.rt_dict.setdefault('cmd', cmd)
        
        #execute in remote device
        print "Execute Output: "
        stdout,stderr = self.cli.execute(cmd)
        if stdout == '':
            raise TestException("Error: No content in log. You may use a wrong test tool or wrong platform ")
        outfile = open('log' + str(self.step_id), 'w+')
        outfile.writelines(stderr)
        outfile.writelines(stdout)
        outfile.close()
        
        #download output file
        self.cli.download(self.Clip_Path + self.dict['Codec'] + '/' + self.dict['OutputFile'], path.result_path + '/' + self.casename + '/')
    
        #delete files
        self.cli.execute("rm " + self.Clip_Path + self.dict['Codec'] + '/' + self.dict['OutputFile']) 
                             
        return self.rt_dict
    
    def videoEncode(self):
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        try:
            if not cmp(self.dict['Codec'], 'YUV'):
                pass
            else:
                raise TestException("Error: Invalid text in Codec element in case configuration file.")
        except KeyError:
            raise TestException("Error: no Codec element found in Parameter element.")
        try:
            input = self.Clip_Path + self.dict['Codec'] + '/' + self.dict['InputFile']
        except KeyError:
            raise TestException("Error: no InputFile element found in Parameter element ")
        try:
            output = self.Clip_Path + self.dict['Codec'] + '/' + self.dict['OutputFile']
        except KeyError:
            raise TestException("Error: no OutputFile element found in Parameter element ")
        try:
            width = self.dict['Resolution_width']
        except KeyError:
            raise TestException("Error: no Resolution_width element found in Parameter element ")
        try:
            height = self.dict['Resolution_height']
        except KeyError:
            raise TestException("Error: no Resolution_height element found in Parameter element ")   
        try:
            YUVcolorformat = self.dict['YUVcolorformat']
        except KeyError:
            raise TestException("Error: no YUVcolorformat element found in Parameter element ") 
        try:
            bitRate = self.dict['BitRate']
        except KeyError:
            raise TestException("Error: no BitRate element found in Parameter element ")
        try:
            framerate = self.dict['Framerate']
        except KeyError:
            raise TestException("Error: no Framerate element found in Parameter element ")
        try:
            format = self.dict['Format']
        except KeyError:
            raise TestException("Error: no Format element found in Parameter element ")
        try:
            level = self.dict['Level']
        except KeyError:
            raise TestException("Error: no Level element found in Parameter element ")
        try:
            nalsize = self.dict['Nalsize']
        except KeyError:
            raise TestException("Error: no Nalsize element found in Parameter element ")
        try:
            allocorusebuffer = self.dict['Allocorusebuffer']
        except KeyError:
            raise TestException("Error: no Allocorusebuffer element found in Parameter element ")
        try:
            deblock = self.dict['Deblock']
        except KeyError:
            raise TestException("Error: no Deblock element found in Parameter element ")
        try:
            ratectrl = self.dict['Ratectrl']
        except KeyError:
            raise TestException("Error: no Ratectrl element found in Parameter element ")
        try:
            qpl = self.dict['Qpl']
        except KeyError:
            raise TestException("Error: no Qpl element found in Parameter element ")
        try:
            testtype = self.dict['Testtype']
        except KeyError:
            raise TestException("Error: no Testtype element found in Parameter element ")
        try:
            referenceframe = self.dict['Referenceframe']
        except KeyError:
            raise TestException("Error: no Referenceframe element found in Parameter element ")
        try:
            testtimes = self.dict['Testtimes']
        except KeyError:
            raise TestException("Error: no Testtimes element found in Parameter element ")
        
        cmd = "VideoEncTest" + ' ' + input + ' ' + output + ' ' + width + ' ' + height + ' ' + YUVcolorformat + ' ' + bitRate + ' ' + framerate + ' ' + format + ' ' + level + ' ' + nalsize + ' ' + allocorusebuffer + ' ' + deblock + ' ' + ratectrl + ' ' + qpl + ' ' + testtype + ' ' + referenceframe + ' ' + testtimes 
        print "Command:"
        print cmd
        print ""
        self.rt_dict.setdefault('cmd', cmd)
        
        #execute in remote device
        print "Execute Output: "
        stdout,stderr = self.cli.execute(cmd)
        if stdout == '':
            raise TestException("Error: No content in log. You may use a wrong test tool or wrong platform ")
        outfile = open('log' + str(self.step_id), 'w+')
        outfile.writelines(stderr)
        outfile.writelines(stdout)
        outfile.close()
        
        #download output file
        self.cli.download(self.Clip_Path + self.dict['Codec'] + '/' + self.dict['OutputFile'], path.result_path + '/' + self.casename + '/')
    
        #delete files
        self.cli.execute("rm " + self.Clip_Path + self.dict['Codec'] + '/' + self.dict['OutputFile']) 
                             
        return self.rt_dict
        
        
    def videoDecode(self):
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        try:
            if not cmp(self.dict['Codec'], 'H264'):
                pass
            elif not cmp(self.dict['Codec'], 'm4v'):
                pass
            elif not cmp(self.dict['Codec'], 'H263'):
                pass
            else:
                raise TestException("Error: Invalid text in Codec element in case configuration file.")
        except KeyError:
            raise TestException("Error: no Codec element found in Parameter element.")
        try:
            input = self.Clip_Path + self.dict['Codec'] + '/' + self.dict['InputFile']
        except KeyError:
            raise TestException("Error: no InputFile element found in Parameter element ")
        try:
            output = self.Clip_Path + self.dict['Codec'] + '/' + self.dict['OutputFile']
        except KeyError:
            raise TestException("Error: no OutputFile element found in Parameter element ")
        try:
            format = self.dict['Format'] 
        except KeyError:
            raise TestException("Error: no Format element found in Parameter element ")
        try:
            maxwidth = self.dict['Maxwidth'] 
        except KeyError:
            raise TestException("Error: no Maxwidth element found in Parameter element ")
        try:
            maxheight = self.dict['Maxheight'] 
        except KeyError:
            raise TestException("Error: no Maxheight element found in Parameter element ")
        try:
            decodeSpeed = self.dict['DecodeSpeed'] 
        except KeyError:
            raise TestException("Error: no DecodeSpeed element found in Parameter element ")
        
        cmd = "omx_vdec_test " + input + ' ' + output + ' ' + format + ' ' + maxwidth + ' ' + maxheight + ' ' + decodeSpeed 
        print "Command:"
        print cmd
        print ""
        self.rt_dict.setdefault('cmd', cmd)
        
        #execute in remote device
        print "Execute Output: "
        stdout,stderr = self.cli.execute(cmd)
        if stdout == '':
            raise TestException("Error: No content in log. You may use a wrong test tool or wrong platform ")
        outfile = open('log' + str(self.step_id), 'w+')
        outfile.writelines(stderr)
        outfile.writelines(stdout)
        outfile.close()
        
        #download output file
        self.cli.download(self.Clip_Path + self.dict['Codec'] + '/' + self.dict['OutputFile'], path.result_path + '/' + self.casename + '/')
        
        #delete files
        self.cli.execute("rm " + self.Clip_Path + self.dict['Codec'] + '/' + self.dict['OutputFile']) 
                               
        return self.rt_dict
        
        
        
        