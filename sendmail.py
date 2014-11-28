import os
import sys
import commands
from optparse import OptionParser
from xml.etree import ElementTree as ET
from tools.color import inred
from common_module.email import checkMailList
import conf
try:
    from conf import path
except ImportError, e:
    print inred("ERROR: no path.py found, please run setup.py again.")
    sys.exit(2)    
try:
    email_profile = conf.email_profile_path
except Exception, e:
    print inred("Error: Cannot find path.email_profile_path. Please run setup.py first.")
    sys.exit(2)

def sendMail(srcNameList,wikisrc,buildlink):
    if maillist == []:
        pass
    else:
        status, output = commands.getstatusoutput("ls " + path.result_path)
        if output.find("No such file or directory") != -1:
            print inred("Cannot send mail because we could not find any result file.")
            return 
        caseList = output.split('\n')
        if caseList == []:
            print inred("Cannot send mail because we could not find any result file.")
            return 
        
        #start writing report
        mailContentFile = open("tempMailContent", 'w')
        buildInfo = "   Build:   " + path.build_name + "\n"
        HWInfo = "   H/W:   PR3.1\n"
        separateLine = "***************************************************************************\n"
        mailContentFile.write(separateLine)
        mailContentFile.write("General Info:\n")
        mailContentFile.write(buildInfo)
        mailContentFile.write(HWInfo)
        mailContentFile.write("\n")
        mailContentFile.write(separateLine)
        
        mailContentFile.write("\n\n")        
	mailContentFile.write(separateLine)  
        mailContentFile.write("   build image:   " + buildlink + "\n")
        mailContentFile.write("\n")        
        mailContentFile.write(separateLine) 
 
        
        total_count = 0
        pass_count = 0
        fail_count = 0  
        TBD_count = 0 
        passCaseList = []
        failCaseList = []
        TBDCaseList = []
         
        for eachCase in caseList:
            try:  
                tree = ET.parse(path.result_path + "/" + eachCase + "/" + eachCase + ".xml") 
                root = tree.getroot() 
            except Exception, e:  
                print "Error: cannot parse file: " + path.result_path + "/" + eachCase + "/" + eachCase + ".xml"  
                continue
            if root.find("pass_count") is not None:     #only record case result
                continue
            else:
                total_count += 1
                caseResult = "pass"
                try:
                    stepList = root.find("execute_information").findall("step")
                    for each_step in stepList:
                        result = each_step.find("result").text
                        if result is None:
                            caseResult = "Cannot obtain result"
                            break
                        elif result.lower() == "pass":
                            pass
                        elif result.lower() == "fail":
                            caseResult = "fail"
                            fail_count += 1
                            failCaseList.append(eachCase)
                            break
                        elif result.lower() == "TBD":
                            caseResult = "TBD"
                            TBD_count += 1
                            TBDCaseList.append(eachCase)
                            break
                        else:
                            caseResult = result
                            break
                    if caseResult == "pass":
                        pass_count += 1
                        passCaseList.append(eachCase)
                except Exception, e:
                    print "Exception occurs when finding step element in file: " + path.result_path + "/" + eachCase + "/" + eachCase + ".xml"
                
        mailContentFile.write("\n\n")        
        mailContentFile.write(separateLine)        
        mailContentFile.write("Test Info:\n")
        mailContentFile.write("   total_count:   " + str(total_count) + "\n")
        mailContentFile.write("   pass_count:   " + str(pass_count) + "\n") 
        mailContentFile.write("   fail_count:    " + str(fail_count) + "\n")
        mailContentFile.write("\n")        
        mailContentFile.write(separateLine)  
        #if failCaseList == []:
            #mailContentFile.write("   None\n")
        #else:
            #for eachPassCase in failCaseList:
                #mailContentFile.write("   " + eachPassCase + "\n")        
        #mailContentFile.write("\n\nTBDCaseList\n")
        #mailContentFile.write(separateLine)  
        #if TBDCaseList == []:
            #mailContentFile.write("   None\n")
        #else:
            #for eachPassCase in TBDCaseList:
                #mailContentFile.write("   " + eachPassCase + "\n")        
        mailContentFile.write("\n\n")        
        mailContentFile.write(separateLine)  
        mailContentFile.write("   AllCaseList:   " + wikisrc + "\n")
        mailContentFile.write("\n")        
        mailContentFile.write(separateLine)  
        #if passCaseList == []:
            #mailContentFile.write("   None\n")
        #else:
            #print "eachpasscase"
            #for eachPassCase in passCaseList:
                #mailContentFile.write("   " + eachPassCase + "\n")
        mailContentFile.close() 
                
        #send mail
        dstNameString = ""
        for eachName in srcNameList:
            dstNameString = dstNameString + ',' + eachName
        dstNameString = dstNameString[1:]
        if os.path.exists("tempMailContent"):
            cmd = "mail -s RapidRunner_TestReport_" + path.build_name + " " + dstNameString + " < tempMailContent"
            os.system(cmd)
            os.system("rm -rf tempMailContent")
        else:
            print inred("No mail content file found, will not send mail!")
            

if __name__ == "__main__":
    
    usage = "usage: python %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option('--mail', dest='mail', help="send mail manually according to current execution result.", default=None)
    options, args = parser.parse_args(sys.argv)
   
    if options.mail is not None:
        maillist = checkMailList(options.mail)
    else:
        print inred("Could not send mail because of the lack of --mail parameter.")
        exit(-1)
    sendMail(maillist,args [1],args[2])


