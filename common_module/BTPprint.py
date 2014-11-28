#!/usr/bin/env python
import sys
from tools.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite

class SetupPrint:
    
    def __init__(self):
        pass
    
    def main_menu(self):
        print "1. Setup environment for Video test."
        print "2. Push busybox into device."
        print "0. Exit."
        
    def menu_CI(self):
        print "\n1. Setup pre-environment for CI test."
        print "2. Push ci_val_cdk into device."
        print "3. Execute 1 - 2 automatically."
        print "4. View CI profile configuration guide."
        print "0. Return.\n"
        
    def menu_Video(self):
        print "\n1. Push busybox into device."
        print "2. Setup pre-environment for Video test."
        print "3. Download and insmod Video Testsuite files and other test tools into device."
        print "4. Push and insmod Codec test and Framework tools into device."
        print "5. Create result directory in device."
        print "6. Setup environment for JPEG Encode."
        print "7. Install android sdk"
        print "8. Execute 1 - 7 automatically."
        print "9. Check Paramiko and install Paramiko."
        print "10. View video profile configuration guide."
        print "0. Return.\n"
        
    def showUserGuidePrint(self):
        print ingreen("\n*****************************")
        print "You may need to create or edit your profile files, please refer to below detail profile info:\n"
        print "1 " + inred("execution profile") + " -- located in test_repo/execution/"
        print "    1.1 name: refer to TMS Excution name and replace all spaces ' ' with underlines '_'.    e.g. tms_excution_name: Build 20110312-001, and the name in execution.xml should be Build_20110312-001"
        print "    1.2 OS: operating system under test. android or meego"
        print "    1.3 DUTTestsuite: ftp or http address for downloading Testsuite.    e.g. ftp://172.16.120.166/TestSuite/Android/mfld/0318/"
        print "    1.4 DUTWorkDirectory: an absolute path used for storing you test output files.    e.g. /cache/"
        print "    1.5 ClipsDirectory: an absolute path leading to your stored clips.    e.g. /cache/Clips/"
        print "    1.6 SystemBoot: from where your system boot.    e.g. SD or eMMC \n"
        print "2 " + inred("device profile") + " -- located in test_repo/device/"
        print "    2.1 Platform: platform under test. MFLD or MRST"
        print "    2.2 OS: operating system under test. android or meego"
        print "    2.3 Connect: device connection method. adb or ssh"
        print "    2.4 serialNumber: use unix command \"adb devices\" to obtain you device serialNumber.    e.g. 0123456789ABCDEF or 172.16.125.197:5555\n"
        print "3. You need" + inred(" root") + " authority to completely implement all functions in setup.py.\n"
        print "4. Your Python version should be" + inred(" 2.6") + ".\n"
        print "5. If you encountered something wrong with Paramiko, try executing step 4 first.\n"
        print "6. You need busybox installed. If not, please install it with step 5 in the main menu."
        print ingreen("*****************************\n")
        userNext = raw_input ("Please Enter to continue: ")
        
    def showCIGuidePrint(self):
        print ingreen("\n*****************************")
        print "You may need to create or edit your profile files, please refer to below detail profile info:\n"
        print "1 " + inred("execution profile") + " -- located in test_repo/execution/"
        print "    1.1 name: refer to TMS Excution name and replace all spaces ' ' with underlines '_'.    e.g. tms_excution_name: Build 20110312-001, and the name in execution.xml should be Build_20110312-001\n"
        print "2 " + inred("device profile") + " -- located in test_repo/device/"
        print "    2.1 Platform: platform under test. MFLD or MRST"
        print "    2.2 OS: operating system under test. android or meego"
        print "    2.3 Connect: device connection method. adb or ssh"
        print "    2.4 serialNumber: use unix command \"adb devices\" to obtain you device serialNumber.    e.g. 0123456789ABCDEF or 172.16.125.197:5555\n"
        print "3. You need" + inred(" root") + " authority to completely implement all functions in setup.py.\n"
        print "4. Your Python version should be" + inred(" 2.6") + ".\n"
        print "5. If you encountered something wrong with Paramiko, try executing step 4 first."
        print ingreen("*****************************\n")
        userNext = raw_input ("Please Enter to continue: ")
        
class PytestPrint: 
    
    def __init__(self):
        pass
    
    def executionBeginPrint(self, execution_name, start_time): 
        print "\n_____________________________"
        print "Execution Name: %s"%execution_name
        print "Start Time: %s"%start_time
    
    def execuitonEndPrint(self, execution_name, end_time, pass_count_total, fail_count_total, TBD_count_total, result_xml):
        print "\nExecution Name: %s"%execution_name
        print "End Time: %s" %end_time
        print "Pass Count: " + ingreen(pass_count_total)
        print "Fail Count: " + inred(fail_count_total)
        print "TBD Count: " + ingreen(TBD_count_total)
        print "Log Path: %s" %result_xml
        print "_____________________________\n"
    
    def suiteBeginPrint(self, suitename, list_len, start_time):
        print "\n###############################"
        print "Suite Name: %s"%suitename
        print "Case Num: %s"%list_len
        print "Begin Time: %s" %start_time
        
    def suiteEndPrint(self, suitename, end_time, pass_count, fail_count, TBD_count, rtlog):
        print "Suite Name: %s"%suitename
        print "End Time: %s" %end_time
        print 'Pass Count: ' + ingreen(pass_count)
        print 'Fail Count: ' + inred(fail_count)
        print 'TBD Count: ' + ingreen(TBD_count)
        print "Log Path: %s" %rtlog
        print "###############################\n"
        
    def caseBeginPrint(self, casename, start_time):
        print "\n******************************"
        print "Case Name: %s" %casename
        print "Begin Time: %s\n"%start_time
        
    def caseEndPrint(self, casename, end_time, case_result, xmllog):
        print "\nCase Name: %s" %casename
        print "End Time: %s" %end_time
        if not cmp(case_result, 'pass'):
            print 'Result: ' + ingreen(case_result)
        else:
            print 'Result: ' + inred(case_result)
        print "Log Path: %s" %xmllog
        print "******************************"
        