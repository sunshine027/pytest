import os
import sys
from xml.etree import ElementTree as ET
from tools.color import inred
from common_module.recordCommand import readCommand_type, readCommand_profile
import conf

try:
    from conf import path
except ImportError, e:
    print inred("ERROR: no path.py found, please run setup.py again.")
    sys.exit(2)
email_profile = conf.email_profile_path

def checkMailList(srcNameList):
    
    dstMailList = []
    try:  
        tree = ET.parse(email_profile) 
        root = tree.getroot() 
    except Exception, e:  
        print "Error: cannot parse file: " + email_profile  
        return dstMailList
    try:
        eles_MailList = root.findall("MailList")  
    except Exception, e:
        print "Error: cannot find Maillist element in " + email_profile  
        return dstMailList
    
    nameList = srcNameList.split(',')    
    for eachName in nameList:
        if eachName.find("@") != -1:
            dstMailList.append(eachName)
        else:
            eachNameFoundFlag = -1         
            for each_MailList in eles_MailList:               
                if eachName.lower() == each_MailList.get("name"):
                    dstMailList.append(each_MailList.text)
                    eachNameFoundFlag = 0
                    break
            if eachNameFoundFlag == -1:
                print inred("Error: Could not send mail to " + eachName + " because " + eachName + " does not exist in mail list.")
            
    return dstMailList

def sendMail(srcNameList):
    if srcNameList != []:
        generateReport(readCommand_type())
        dstNameString = ""
        for eachName in srcNameList:
            dstNameString = dstNameString + ',' + eachName
        dstNameString = dstNameString[1:]
        print path.build_name
        if os.path.exists(path.mailContentFile_path):
            cmd = "mail -s RapidRunner_TestReport_" + path.build_name + " " + dstNameString + " < " + path.mailContentFile_path
            os.system(cmd)
            os.system("rm -rf " + path.mailContentFile_path)
        else:
            print inred("No mail content file found, will not send mail!")
    else:
        pass
        
def generateReport(type):
    if type != -1:
        mailContentFile = open(path.mailContentFile_path, 'w')     
        buildInfo = "   Build:   " + path.build_name + "\n"
        HWInfo = "   H/W:   PR3.1\n"
        separateLine = "-----------------------------------------------------------------------------------------\n"
        mailContentFile.write("General Info\n")
        mailContentFile.write(separateLine)
        mailContentFile.write(buildInfo)
        mailContentFile.write(HWInfo)
        
        if type == "c":
            mailContentFile.write("\n\nExecution Info\n")
            mailContentFile.write(separateLine)
            resultCaseName = readCommand_profile(type).split('/')[-2]
            resultProfilePath = path.result_path + '/' + resultCaseName + '/' + resultCaseName + ".xml"
            try:  
                tree = ET.parse(resultProfilePath) 
                root = tree.getroot() 
            except Exception, e:  
                print "Error: cannot parse file: " + resultProfilePath
                mailContentFile.close()
                return -1
            try:
                eles_step = root.find("execute_information").findall("step")
            except Exception, e:
                print "Error: cannot find element step in " + resultProfilePath
                mailContentFile.close()
                return -1
            caseResult = "pass"
            for each_ele_step in eles_step:
                try:
                    result = each_ele_step.find("result").text
                    if result is None:
                        caseResult = "Cannot obtain result"
                    elif result.lower() == "pass":
                        pass
                    elif result.lower() == "fail":
                        caseResult = "fail"
                        break
                    else:
                        caseResult = result
                        break
                except Exception, e:
                    caseResult = "Cannot obtain result"
            mailContentFile.write("   " + resultCaseName + ":   " + caseResult + "\n")
        elif type == "s":
            resultSuiteName = readCommand_profile(type).split('/')[-1].split('.')[0]
            resultProfilePath = path.result_path + '/' + resultSuiteName + '/' + resultSuiteName + ".xml"
            try:  
                tree = ET.parse(resultProfilePath) 
                root = tree.getroot() 
            except Exception, e:  
                print "Error: cannot parse file: " + resultProfilePath
                mailContentFile.close()
                return -1
            pass_count = root.find("pass_count").text
            if pass_count is None:
                pass_count = "0"
            fail_count = root.find("fail_count").text
            if fail_count is None:
                fail_count = "0"
            TBD_count = root.find("TBD_count").text
            if TBD_count is None:
                TBD_count = "0"
            mailContentFile.write("\n\nCount Info\n")
            mailContentFile.write(separateLine)
            mailContentFile.write("   PassCount:   " + pass_count + "\n")
            mailContentFile.write("   FailCount:   " + fail_count + "\n")
            mailContentFile.write("   TBDCount:   " + TBD_count + "\n")
            
            mailContentFile.write("\n\nFailCaseList\n")
            mailContentFile.write(separateLine)
            eles_failCases = root.find("fail_list").findall("case_name")
            if eles_failCases == []:
                mailContentFile.write("   None\n")
            else:
                for each_ele in eles_failCases:
                    mailContentFile.write("   " + each_ele.text + "\n")
            mailContentFile.write("\n\nTBDCaseList\n")
            mailContentFile.write(separateLine) 
            eles_TBDCases = root.find("TBD").findall("case_name")
            if eles_TBDCases == []:
                mailContentFile.write("   None\n")
            else:
                for each_ele in eles_TBDCases:
                    mailContentFile.write("   " + each_ele.text + "\n")
            mailContentFile.write("\n\nPassCaseList\n")
            mailContentFile.write(separateLine)
            eles_passCases = root.find("pass_list").findall("case_name")
            if eles_passCases == []:
                mailContentFile.write("   None\n")
            else:
                for each_ele in eles_passCases:
                    mailContentFile.write("   " + each_ele.text + "\n")
        elif type == "e":
            resultExecutionName = readCommand_profile(type).split('/')[-1].split('.')[0]
            resultProfilePath = path.result_path + '/' + resultExecutionName + '/' + resultExecutionName + ".xml"
            try:  
                tree = ET.parse(resultProfilePath) 
                root = tree.getroot() 
            except Exception, e:  
                print "Error: cannot parse file: " + resultProfilePath
                mailContentFile.close()
                return -1
            pass_count = root.find("pass_count").text
            if pass_count is None:
                pass_count = "0"
            fail_count = root.find("fail_count").text
            if fail_count is None:
                fail_count = "0"
            TBD_count = root.find("TBD_count").text
            if TBD_count is None:
                TBD_count = "0"
            mailContentFile.write("\n\nCount Info\n")
            mailContentFile.write(separateLine)
            mailContentFile.write("   PassCount:   " + pass_count + "\n")
            mailContentFile.write("   FailCount:   " + fail_count + "\n")
            mailContentFile.write("   TBDCount:   " + TBD_count + "\n")
            
            mailContentFile.write("\n\nFailCaseList\n")
            mailContentFile.write(separateLine)
            eles_failCases = root.find("fail_list").findall("case_name")
            if eles_failCases == []:
                mailContentFile.write("   None\n")
            else:
                for each_ele in eles_failCases:
                    mailContentFile.write("   " + each_ele.text + "\n")
            mailContentFile.write("\n\nTBDCaseList\n")
            mailContentFile.write(separateLine) 
            eles_TBDCases = root.find("TBD").findall("case_name")
            if eles_TBDCases == []:
                mailContentFile.write("   None\n")
            else:
                for each_ele in eles_TBDCases:
                    mailContentFile.write("   " + each_ele.text + "\n")
            mailContentFile.write("\n\nPassCaseList\n")
            mailContentFile.write(separateLine)
            eles_passCases = root.find("pass_list").findall("case_name")
            if eles_passCases == []:
                mailContentFile.write("   None\n")
            else:
                for each_ele in eles_passCases:
                    mailContentFile.write("   " + each_ele.text + "\n")
        else:
            pass                    
        mailContentFile.close()
    else:
        pass
                
