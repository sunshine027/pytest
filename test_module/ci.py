import sys
import os
import commands
from conf import path

from tools.dataparser import DataParser
from exceptions import IOError, AttributeError, KeyError
from exception.testexception import TestException
from tools.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite

class utility:
    def __init__(self, step_id, par_dict, dev_dict1, crt, caseFolderName, all_monitor_thread_dict, stepType, platform):
        self.step_id = step_id
        self.dict = par_dict
        self.dict1 = dev_dict1
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

        from tools.client import adbAccessor as accessor
        self.cli = accessor(self.dict1)
        
    def execute(self):
        
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
            
        try:
            if self.dict.get('Dir') is None:
                raise TestException("Error: no text in element 'Dir' in case profile.")
            dir = self.dict['Dir']
        except KeyError, e:
            raise TestException("Error: no Dir element found in Parameter element")
        
        try:
            if self.dict.get('CmdName') is None:
                raise TestException("Error: no text in element 'CmdName' in case profile.")
            cmdname = self.dict['CmdName']
        except KeyError, e:
            raise TestException("Error: no CmdName element found in Parameter element")
        
        if self.stepType == 0 or self.stepType == 10:
            #delete last result
            print "\nCase preparation: \n"
            self.cli.execute("rm -rf /cache/*")
            self.cli.execute("rm -rf /sdcard/result/*")
        
        #delete case_id in self.caseFolderName
        case_id = self.caseFolderName.split("_")[0]
        caseFolderName_withoutCaseId = self.caseFolderName[len(case_id) + 1:]
        
        if self.stepType == 0 or self.stepType == 10:
            #download case and chmod
            print inblue("Pushing case files into device ......")
            self.cli.upload("../cats/TestCase/" + dir + "/" + caseFolderName_withoutCaseId, "/cache")
            self.cli.execute("cd /cache ; chmod 777 " + caseFolderName_withoutCaseId)
            if self.stepType == 10:
                return "noResult"
        
        if self.stepType == 0 or self.stepType == 20:
            cmd = "cd /cache/ ; ./" + caseFolderName_withoutCaseId
            print "Command:"
            print cmd
            print ""
            self.rt_dict.setdefault('cmd', cmd)
    
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
        
        if self.stepType == 0 or self.stepType == 30:
            #create case result storing dir
            caseResultStorePath = "../cats/Execution/" + path.build_name + '/' + dir + '/' + caseFolderName_withoutCaseId
            status, output = commands.getstatusoutput("mkdir -p " + caseResultStorePath)
            if status != 0:
                print inred("Error: cannot create result storing dir.")
            
            #pull all case result
            print inblue("Pulling case result files ......")
#            self.cli.execute("rm -rf /sdcard/result/" + caseFolderName_withoutCaseId)
            self.cli.download("/sdcard/result", caseResultStorePath)
            self.cli.download("/cache", caseResultStorePath)
            if self.stepType == 30:
                return "noResult"
        
        if self.stepType == 0 or self.stepType == 20:
            #obtain cam_Result
            status, output = commands.getstatusoutput("tac log" + str(self.step_id))
            ost1 = output.find("Result:") + 8
            ost2 = output.find("Result:") + 12
            if ost1 == 7:
                cam_Result = "null"
            else:
                cam_Result = output[ost1:ost2]
    
            self.rt_dict.setdefault('Result', cam_Result)
            
            return self.rt_dict
            
            
            
            
            
            
            
            
            
            
            