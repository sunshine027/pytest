import os
import commands
from tools.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite
from tools.client import execute_command_on_server
from conf import path
from tools.get_execution_info import get_clip_path
SCRIPT_PATH = "./resource/stressTest_script/"

class utility:
    def __init__(self, step_id, par_dict, dev_dict1, crt, caseFolderName, all_monitor_thread_dict, stepType, platform):
        self.step_id = step_id
        self.dict = par_dict
        self.dict1 = dev_dict1
        self.crt = crt
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

        from tools.client import adbAccessor as accessor
        self.cli = accessor(self.dict1)
        self.Clip_Path = get_clip_path()
    
    def command(self):
        
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        try:
            command = self.dict['command']
        except KeyError, e:
            raise TestException("Error: no command element found in Parameter element") 
        try:
            serialNo = self.dict1['serialNumber']
        except KeyError, e:
            raise TestException("Error: no serialNumber element found in device profile")
        
        if self.stepType == 0 or self.stepType == 10:
            if self.stepType == 10:
                return "noResult"
        
        if self.stepType == 0 or self.stepType == 20:
            #generate shell file
            shFile = open("shCmd.sh", 'w')
            shFile.write("#!/system/bin/bash\n")
            shFile.write("a=`$1 ; echo SPLIT$?`\n")
            shFile.write("echo $a")
            shFile.close()
            
            #execute shell
            status, output = commands.getstatusoutput("adb -s " + serialNo + " push shCmd.sh /cache/")
            status, output = commands.getstatusoutput("adb -s " + serialNo + " shell \"chmod 4777 /cache/shCmd.sh\"")
            status, output_sh = commands.getstatusoutput("adb -s " + serialNo + " shell " + "\"/cache/shCmd.sh \\\"" + command + "\\\"\"")
            status, output = commands.getstatusoutput("adb -s " + serialNo + " shell \"rm -rf /cache/shCmd.sh\"")
            
            os.system("rm -rf shCmd.sh")
            
            #parse output_sh
            if output_sh.find("device not found") != -1:
                print inred("Adb connection error: device not found!")
                result = 127
            else:
                result = output_sh.split('SPLIT')[-1].replace(' ', '').replace('\r', '')
            
            self.rt_dict.setdefault('valueReturn', result)
                    
        if self.stepType == 0 or self.stepType == 30:
            if self.stepType == 30:
                return "noResult"
            
        return self.rt_dict
    

    def script(self):
        
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        try:
            scriptName = self.dict['script'].strip()
        except KeyError, e:
            raise TestException("Error: no script element found in Parameter element") 
        try:
            itera = self.dict['iteration']
#            if not cmp(itera.replace(' ',''), 'Off'):
#                itera = ''
        except KeyError, e:
            raise TestException("Error: no iteration element found in Parameter element") 
        try:
            serialNo = self.dict1['serialNumber']
        except KeyError, e:
            raise TestException("Error: no serialNumber element found in device profile")
        
        if self.stepType == 0 or self.stepType == 10:
            if self.stepType == 10:
                return "noResult"
        
        if self.stepType == 0 or self.stepType == 20:
            #execute
#            format = self.dict['Format']
#            try:
#                input_file_path = self.Clip_Path + self.dict['Format'] + '/' + self.dict['InputFile']
#            except KeyError:
#                raise TestException("Error: no InputFile element found in Parameter element ")
#            self.check_clip_exist_in_dut(input_file_path, serialNo)
            
            print SCRIPT_PATH + scriptName + ' ' + serialNo + ' ' + itera + ' ' + get_clip_path() + " | tee log" + str(self.step_id)
            status, output = commands.getstatusoutput(SCRIPT_PATH + scriptName + ' ' + serialNo + ' ' + itera + ' ' + get_clip_path() + " | tee log" + str(self.step_id))
                        
            #parse output
            if output.find("No such file or directory") != -1:
                print inred("Shell file not found!")
                result = 126
            elif output.find("device not found") != -1:
                print inred("Adb connection error: device not found!")
                result = 127
            else:
                result = output.split('\n')[-1].replace(' ', '').replace('\r', '')
                
            try:
                outfile = open('log' + str(self.step_id), 'r') 
            except IOError, e:
                print inred("Error: cannot generate log.")
                os.system("touch log" + str(self.step_id))
            stdout = outfile.read()
            outfile.close()
            
            self.rt_dict.setdefault('valueReturn', result)
                
        if self.stepType == 0 or self.stepType == 30:
            if self.stepType == 30:
                return "noResult"
            
        return self.rt_dict
