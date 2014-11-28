#!/usr/bin/env python
'''
    resume mechanism:
    resume/SUITE_resume.xml will record the suite profile' content that have been run, but no finished.
    resume/EXECUTION_resume.xml will record the current execution profile's content that have been run ,but not finished.
    remark will record the execution, the suite that have been run but not finished. If the current suite or execution path
    is found in remark file, we will give tips to warn if users resume to run.
'''
import sys
import os
import time
import shutil
import xml.etree.ElementTree as ET

from exception.testexception import TestException
from tools.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite
import conf
    
suiteResumePath = conf.TEST_REPO + 'resume/SUITE_resume.xml'
executionResumePath = conf.TEST_REPO + 'resume/EXECUTION_resume.xml'

def checkResume(type, file_path):
    if type == 'suite' or type == 'execution':        
        if readRemark(file_path) and os.path.isfile(conf.TEST_REPO + "resume/" + type.upper() + "_resume.xml"):
            userinput = ''
            try:
                if type == 'suite':
                    parsedName = ET.parse(suiteResumePath).getroot().find('name').text
                else:
                    parsedName = ET.parse(executionResumePath).getroot().find('name').text
            except Exception, e:
                return False                          
            while userinput != 'y' and userinput !='n':
                userinput = raw_input(inblue("You have unfinished " + type + ": %s, would you want to continue running it? y/n "%parsedName))
            if userinput == 'y':
                return True
            else:
                return False
        else:
            return False
    else:
        raise TestException("Error: wrong checkResume type!")

def getResume(type):
    if type == 'suite':
        return suiteResumePath
    elif type == 'execution':
        return executionResumePath
    else:
        raise TestException("Error: wrong getResume type!")
    
def createResume(directStr, type):
    if type == 'suite' or type == 'execution':
        if type == 'suite':
            filename = suiteResumePath
        else:
            filename = executionResumePath
        if not os.path.isfile(directStr):
            raise TestException("Error: " + directStr + " doesn't exist ") 
        shutil.copyfile(directStr, filename)
    else:
         raise TestException("Error: wrong createResume type!")   
                       
def deleteCaseInSuiteResume(casename):
    try:
        parsed_xml = ET.parse(suiteResumePath)
    except Exception,e:
        raise TestException("IOError: Cannot find: " + suiteResumePath)
    root = parsed_xml.getroot()
    all_cases = root.find('list')
    if len(all_cases) == 0:
        print inred("Error: no case in this suite file: " + suiteResumePath)
        userinput = ''
        while userinput != 'y' and userinput !='n':
            userinput = raw_input(inblue('Do you want to delete this suite resume file? y/n '))
        if userinput == 'y':
            deleteResume('suite')
            print ingreen("File deleted.")
        else:
            print inred("This suite file is invalid, we strongly recommend you delete it!")
        sys.exit(-1)
    for case in all_cases:
        if case.text == casename:
            all_cases.remove(case)
            break
    try:
        parsed_xml.write(suiteResumePath)
    except Exception,e:
        raise TestException("IOError: Cannot find directory: " + suiteResumePath)
            
def deleteResume(type, file_path=''):
    if type == 'suite':
        try:
            os.remove(suiteResumePath)
        except Exception, e:
            pass
    elif type == 'execution':
        try:
            os.remove(executionResumePath)
        except Exception, e:
            pass
    elif type == 'remark':
        if file_path == '':
            try:
                os.remove(conf.TEST_REPO + "resume/Remark")
            except Exception,e:
                pass
        else:
            remark_file = open(conf.TEST_REPO + "resume/Remark")
            str = ''
            for line in remark_file:
                if line.find(file_path) != -1:
                    pass
                else:
                    str += line
            remark_file = open(conf.TEST_REPO + "resume/Remark", 'w')
            remark_file.write(str)
    else:
        raise TestException("Error: wrong getResume type!")
 
    
def createSuiteFromExecution(test_suite_name): 
     createResume(conf.SUITE_PATH + test_suite_name + '.xml', 'suite')


def deleteSuiteInExecutionResume(suitename):
    try:
        parsed_xml = ET.parse(executionResumePath)
    except Exception,e:
        raise TestException("IOError: Cannot find: " + executionResumePath)
    root = parsed_xml.getroot()
    all_suites = root.find('list')
    for suite in all_suites:
        if suite.text == suitename:
            all_suites.remove(suite)
            break
    try:
        parsed_xml.write(executionResumePath)
    except Exception,e:
        raise TestException("IOError: Cannot find: " + executionResumePath)
    
def deleteAllResume():
    try:
        os.remove(suiteResumePath)
    except Exception, e:
        pass
    try:
        os.remove(executionResumePath)
    except Exception, e:
        pass
    try:
        os.remove(conf.TEST_REPO + "resume/Remark")
    except Exception, e:
        pass

def ifExecutionListEmpty(): 
    try:
        parsed_xml = ET.parse(executionResumePath)
    except Exception,e:
        raise TestException("IOError: Cannot find: " + executionResumePath)
    root = parsed_xml.getroot()
    all_suites = root.find('list')
    if all_suites == None:
        raise TestException(executionResumePath + " has no list element!")
    if len(all_suites) == 0:
        return True
    else:
        return False
    
def createRemark(name):
    if not os.path.exists(conf.TEST_REPO + "resume/"):
        os.system("mkdir -p " + conf.TEST_REPO + "resume/")
    remarkFile = open(conf.TEST_REPO + "resume/Remark", 'a+')
    remarkFile.write(name+'\n')
    remarkFile.close()
    
def readRemark(file_path):
    try:
        remarkFile = open(conf.TEST_REPO + "resume/Remark", 'r')
        for line in remarkFile:
            if line.strip() == file_path:
                return True
        return False
    except Exception, e:
        return False
    
def check_suite_resume(suite_name):
    if os.path.exists(suiteResumePath):
        try:
            parsed_xml = ET.parse(suiteResumePath)
        except Exception,e:
            raise TestException("IOError: Cannot find: " + suiteResumePath)
        root = parsed_xml.getroot()
        resume_name = root.find('name').text.strip()
        if suite_name.strip() == resume_name:
            return True
        else:
            return False
    else:
        return False
    
    
    
    