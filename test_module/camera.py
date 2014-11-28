import sys
import os
from conf import path
from common_module.dataparser import DataParser
from exceptions import IOError, AttributeError, KeyError
from common_module.testexception import TestException
from common_module.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite

class caTS:
    def __init__(self, step_id, par_dict, dev_dict1, crt, cam, casename):
        self.step_id = step_id
        self.dict = par_dict
        self.dict1 = dev_dict1
        self.crt = crt
        self.cam = cam
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

        from common_module.client import adbAccessor as accessor
        self.cli = accessor(self.dict1)
        
    def execute(self):
        #get cam
        if self.cam == False:
            print inred("Maybe you forgot to input --cam ")
            raise TestException("Error: invalid camera component type!")
        caseRoute_1 = self.cam
        
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        
        #get type
        try:
            if self.dict.get('type') is None:
                raise TestException("Error: no text in element 'cam' in case profile.")
            if not cmp(self.dict['type'], 'Integration'):
                caseRoute_2 = 'Integration'
            elif not cmp(self.dict['type'], 'Std_ioctl'):
                caseRoute_2 = 'Std_ioctl'
            else:
                raise TestException("Error: invalid text in element 'cam' in case profile. The content of 'type' element must be one of 'Integration' and 'Std_ioctl'. ")
        except KeyError:
            raise TestException("Error: no type element found in Parameter element! ")
        
        #get cmdname
        try:
            if self.dict.get('cmdname') is None:
                raise TestException("Error: no text in element 'cmdname' in case profile.")
            cmdname = self.dict['cmdname']
        except KeyError, e:
            raise TestException("Error: no cmdname element found in Parameter element")
        
        #self.cli.upload(path.case_path + "V4L2_" + caseRoute_1 + "Cam/" + caseRoute_2 + "/" + cmdname, "/cache/")        
        if caseRoute_2 == 'Integration':
            stdout,stderr = self.cli.execute("cd /cache/V4L2_" + caseRoute_1 + "/" + caseRoute_2 + "/" + cmdname + "/" + "; chmod 777 " + cmdname)
            stdout,stderr = self.cli.execute("cd /cache/V4L2_" + caseRoute_1 + "/" + caseRoute_2 + "/" + cmdname + "/" + "; ./" + cmdname)
        elif caseRoute_2 == 'Std_ioctl':
            stdout,stderr = self.cli.execute("cd /cache/V4L2_" + caseRoute_1 + "/" + caseRoute_2 + "/" + "; chmod 777 " + cmdname)
            stdout,stderr = self.cli.execute("cd /cache/V4L2_" + caseRoute_1 + "/" + caseRoute_2 + "/" + "; ./" + cmdname)
        else:
            raise TestException("Error: Invalid case type.")
        
        outfile = open('log' + str(self.step_id), 'w+')
        outfile.writelines(stderr)
        outfile.writelines(stdout)
        outfile.close()
        
        #pull image file
        if caseRoute_2 == 'Integration':
            self.cli.download("/cache/V4L2_" + caseRoute_1 + "/" + caseRoute_2 + "/" + cmdname + "/" + cmdname + ".img", path.result_path + "/" + self.cam + "/" + cmdname + "/")
        
        #delete all case file in device
        if caseRoute_2 == 'Integration':
            stdout,stderr = self.cli.execute("cd /cache/V4L2_" + caseRoute_1 + "/" + caseRoute_2 + "/" + cmdname + "/ ; rm -rf " + cmdname + ".img")
        
        #obtain cam_Result
        fd = open('log' + str(self.step_id))
        textlist = fd.readlines()
        for text in textlist:
            if text == '\r\n':
                textlist.remove(text)
        try:
            text = textlist[len(textlist)-2]
        except IndexError, e:
            print inblue("Tips: maybe you executed this case in a wrong platform.")
            os.system('rm -f ./log' + str(self.step_id))
            raise TestException("JPEG log error: wrong JPEG log!")
        ost1 = text.find("Result:") + 8
        ost2 = text.find("Result:") + 12
        cam_Result = text[ost1:ost2]
        fd.close()
        
        self.rt_dict.setdefault('Result', cam_Result)
        return self.rt_dict
       
       
       
       
        