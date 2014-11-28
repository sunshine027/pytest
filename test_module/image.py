import sys
import os
import commands
from exceptions import IOError, AttributeError, KeyError

from conf import path
import conf
from tools.dataparser import DataParser
from exception.testexception import TestException
from tools.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite
from tools.shellExecutor import executeShell
from tools.client import execute_command_on_server
from test_module import script_path
from tools.get_execution_info import get_clip_path, get_result_path

LIBVA_FILE_PATH = '/system/LibVA-API_Test/'
LIBVA_SCRIPT_PATH = '/sdcard/'

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

    
    def jpeg_decode(self):
        try:
            inputFile = self.dict['InputFile'].strip()
        except KeyError, e:
            raise TestException("Error: no InputFile element found in Parameter element")
        try:
            OutputFile = self.dict['OutputFile'].strip()
        except KeyError, e:
            raise TestException("Error: no OutputFile element found in Parameter element")
        prefix = get_clip_path() + 'Image/'
        
        result_path = get_result_path() + 'JPEG_Decode/'
        mkdir_cmd = 'mkdir -p ' + result_path
        self.cli.execute_test(mkdir_cmd, self.step_id)
        cmd = 'djpeg -bmp ' + prefix + inputFile + ' ' + result_path + OutputFile
        self.cli.execute_test(cmd, self.step_id)
        stdout, stderr = self.cli.execute_test('cksum ' + result_path + OutputFile, self.step_id)
        bmp_crc = stdout.split('/')[0].strip()
        self.rt_dict.setdefault('Image_CRC', bmp_crc)
        self.rt_dict.setdefault('cmd', cmd)
            
        if self.stepType == 0 or self.stepType == 30:
            if self.stepType == 30:
                return "noResult"
            
        return self.rt_dict
    
    def bmp_encode(self):
        try:
            inputFile = self.dict['InputFile'].strip()
        except KeyError, e:
            raise TestException("Error: no InputFile element found in Parameter element")
        try:
            OutputFile = self.dict['OutputFile'].strip()
        except KeyError, e:
            raise TestException("Error: no OutputFile element found in Parameter element")
        prefix = get_clip_path() + 'Image/'
        
        if inputFile.strip().endswith('bmp'):
            cmd = 'cjpeg ' + prefix + inputFile + ' ' + prefix + OutputFile
            print cmd
            self.cli.execute_test(cmd, self.step_id)
            print 'cksum ' + prefix + OutputFile
            stdout, stderr = self.cli.execute_test('cksum ' + prefix + OutputFile, self.step_id)
            print stdout
            bmp_crc = stdout.split('/')[0].strip()
            print bmp_crc, ' crc'
            self.rt_dict.setdefault('Image_CRC', bmp_crc)
            self.rt_dict.setdefault('cmd', cmd)
            
        if self.stepType == 0 or self.stepType == 30:
            if self.stepType == 30:
                return "noResult"
            
        return self.rt_dict
    
    def image_decoder(self):
        try:
            inputFile = self.dict['InputFile'].strip()
        except KeyError, e:
            raise TestException("Error: no InputFile element found in Parameter element")
        try:
            OutputFile = self.dict['OutputFile'].strip()
        except KeyError, e:
            raise TestException("Error: no OutputFile element found in Parameter element")
        try:
            format = self.dict['Format'].strip()
        except KeyError, e:
            raise TestException("Error: no Format element found in Parameter element")
        prefix = get_clip_path() + format + '/'
        cmd = 'imagedecoder -input ' + prefix + inputFile + ' -output ' + prefix + OutputFile
        print cmd
        stdout, stderr = self.cli.execute_test(cmd, self.step_id)
        print stdout
        print stderr
        print 'cksum ' + prefix + OutputFile
        stdout, stderr = self.cli.execute_test('cksum ' + prefix + OutputFile, self.step_id)
        print stdout
        bmp_crc = stdout.split('/')[0].strip()
        print bmp_crc, ' crc'
        self.rt_dict.setdefault('Image_CRC', bmp_crc)
        self.rt_dict.setdefault('cmd', cmd)
            
        if self.stepType == 0 or self.stepType == 30:
            if self.stepType == 30:
                return "noResult"
        return self.rt_dict
    
    def image_encoder(self):
        try:
            inputFile = self.dict['InputFile'].strip()
        except KeyError, e:
            raise TestException("Error: no InputFile element found in Parameter element")
        try:
            OutputFile = self.dict['OutputFile'].strip()
        except KeyError, e:
            raise TestException("Error: no OutputFile element found in Parameter element")
        try:
            format = self.dict['Format'].strip()
        except KeyError, e:
            raise TestException("Error: no Format element found in Parameter element")
        try:
            output_format = self.dict['OutputFormat'].strip()
        except KeyError, e:
            raise TestException("Error: no OutputFormat element found in Parameter element")
        try:
            resolution = self.dict['Resolution'].strip()
        except KeyError, e:
            raise TestException("Error: no Resolution element found in Parameter element")
        width = resolution.split('x')[0]
        height = resolution.split('x')[1]
        prefix = get_clip_path() + format + '/'
        cmd = 'imageencoder -source ' + prefix + inputFile + ' -width ' + width + ' -height ' + height + ' -'  + output_format + ' ' + prefix + OutputFile
        stdout, stderr = self.cli.execute_test(cmd, self.step_id)
        stdout, stderr = self.cli.execute_test('cksum ' + prefix + OutputFile, self.step_id)
        bmp_crc = stdout.split('/')[0].strip()
        self.rt_dict.setdefault('Image_CRC', bmp_crc)
        self.rt_dict.setdefault('cmd', cmd)
            
        if self.stepType == 0 or self.stepType == 30:
            if self.stepType == 30:
                return "noResult"
        return self.rt_dict
    
        
        
        
        
        
        
            
            
            
            
            
            
            
            
            
            
