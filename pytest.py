#!/usr/bin/env python
#coding=utf-8

import sys
import os
import time
import shutil
import xml.etree.ElementTree as ET
import getopt
from multiprocessing import Queue, Process, active_children, Manager
from xml.parsers.expat import ExpatError
from optparse import OptionParser
from subprocess import Popen, PIPE
from select import select
import signal
import commands

import conf
from tools.get_execution_info import get_build_name
from tools.create_configure import create_path_file
try:
    from conf import path
except ImportError, e:
    build_name = get_build_name()
    execution_profile = conf.EXECUTION_PATH + build_name + '.xml'
    create_path_file(execution_profile)
    from conf import path
    
from common_module import DEVICE_DATA_DIR, ISO_DATETIME_FORMAT, BTPprint
from common_module.check_profile import check_device_profile
from common_module.check_path import check_item_in_path
from common_module.downloadClip import downloadClip
from common_module.check_environment import check_build_name
from common_module.check_profile import check_adb_connect
from common_module.resume import readRemark, createRemark, ifExecutionListEmpty, deleteAllResume, deleteSuiteInExecutionResume, createSuiteFromExecution, executionResumePath, suiteResumePath, deleteResume, deleteCaseInSuiteResume, createResume, checkResume, getResume, check_suite_resume
from tools.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite
from tools import XMLParser, assertor
from tools.create_configure import create_path_file
from common_module.monitor import memory_monitor_process, kernel_log_monitor_process, logcat_monitor_process, matrix_monitor_process
from exception.testexception import TestException
from tools.shellExecutor import executeShell
from report.report import TestReport, error_report
from tools.client import execute_command_on_server
from tools.kill_command_on_device import kill_command_on_device, kill_kernel_log, kill_logcat
from common_module.email import checkMailList, sendMail
from common_module.recordCommand import writeCommand

    
MONITOR_THREAD_REF_DICT = {'memory': 'memory_monitor_process', 'kernel_log': 'kernel_log_monitor_process', 'logcat': 'logcat_monitor_process', 'matrix': 'matrix_monitor_process', 'matrix1': 'matrix_monitor_process'}
KILL_MONITOR_NAME = ['kernel_log', 'logcat']     
       
def executeStep(step_element, device_dict, case_log, result_queue, exception_queue, caseFolderName, runmodule, all_monitor_thread_dict, stepType, platform):
    ''' process for executing one step. '''
    
    try:
        test_case = TestCase(stepType)
        step_id = step_element.get('id')
        excname = step_element.get('function')
        if excname is None:
            raise TestException("Error: no function attribute found in the Step with id " + str(step_id))
        par = step_element.find('Parameter')
        if not par:
            raise TestException("Error: no Parameter element found in the Step with id " + str(step_id))
        etparser = XMLParser.ETParser()
        par_dict = etparser.ETtoDict(par)
        
        #generate dict for schedule
        sch = step_element.find('Schedule')
        if sch is None:
            raise TestException("Error: no Schedule element found in the Step with id " + str(step_id))
        etparser = XMLParser.ETParser()
        sch_dict = etparser.ETtoDict(sch)
        crt = step_element.find('Criteria')
        if not crt:
            raise TestException("Error: no Criteria element found in the Step with id " + str(step_id))
        try:
            ite_value = sch_dict['Iteration']
        except KeyError, e:
            raise TestException("Error: no Iteration element  found in Schedule in Step with id " + str(step_id))
        if ite_value is None or ite_value.strip() == '':
            raise TestException("Error: the value of Iteration element  in Schedule in Step with id " + str(step_id) + ' is empty, and it should be a number ')
        try:
            iterNo = int(ite_value)
        except ValueError, e:
            raise TestException("Error:  the value of Iteration element  in Schedule in Step with id " + str(step_id) + ' must be a number ')
        
        i = iterNo
        while (i > 0):
            roundnum = iterNo + 1 - i
            print inpurple("\nRound " + str(roundnum) +": ") 
            i = i - 1
            try:
                et = test_case.run(step_id, excname, par_dict, device_dict, crt, caseFolderName, runmodule, all_monitor_thread_dict, platform)
            except TestException, e:
                raise TestException(e.value + " in Step with id " + str(step_id))
            if os.path.isfile('log' + str(step_id)):
                log_fd = open(case_log, 'w')
                log_tmp = open('log' + str(step_id))
                lt = log_tmp.readlines()
                log_fd.writelines(lt)
                log_tmp.close()
                log_fd.close()
                os.remove('log' + str(step_id))
            else:
                print inblue("TIP: no log file generated during executing command, so there won't be log file for Step with id " + str(step_id))
            
            #parsing result
            criteria_dict, addtional_dict, operator_dict = assertor.get_criteria_dict(crt)
            try:
                rt = assertor.assertor(criteria_dict, et, operator_dict, addtional_dict, device_dict, caseFolderName)
            except TestException, e:
                raise TestException(e.value + " in Step with id " + str(step_id))
            if not cmp(rt, 'fail'):
                break

        #the format of the result of one step is [step_id, case_result, command_result]
        result_queue.put(['step_' + str(step_id), rt, et])
    except TestException, e:
        exception_queue.put(e.value)
        
class TestExecution:
    
    '''A class whose instances can execute test execution.'''
    
    def __init__(self):
        self.reporter = TestReport()
        self.btpprint = BTPprint.PytestPrint()

    def runTest(self, excution_resume, original_execution_path, resume_execution_xml, dev_dict, module_value, runtype, platform, maillist):
        try:
            try:
                root = ET.parse(resume_execution_xml).getroot()
            except IOError, e:
                raise TestException("Error: file " + str(original_execution_path) + " not found")
            except ExpatError, e:
                raise TestException("Error: the file: " + str(original_execution_path) + " is in invalid xml format.")
            try:
                intro = root.find('intro').text
            except AttributeError, e:
                raise TestException("Error: no intro element found in execution file: " + str(original_execution_path))
            if intro is not None and intro.strip() != '':
                print "\nintro: " + intro
            try:
                execution_name = root.find('name').text.strip()
            except AttributeError, e:
                raise TestException("Error: no name element found in execution file: " + str(original_execution_path))
            if execution_name is None or execution_name.strip() == '':
                raise TestException("Error: the text of name element can't be empty in execution file: " + str(original_execution_path))
            all_suites = root.find('list')
            if all_suites is None:
                raise TestException("Error: no list element found in execution file: " + str(original_execution_path))
            if len(all_suites) == 0:
                raise TestException("Error: no suite in execution file: " + str(original_execution_path) + ", no need to run.")
            dict1 = {}
            start_time = time.strftime(ISO_DATETIME_FORMAT, time.gmtime(time.time()))
            dict1.setdefault('start_time', start_time)
            dict1.setdefault('name', execution_name)
            
            self.btpprint.executionBeginPrint(execution_name, start_time)
            
            execution_dir = path.result_path + '/' + execution_name
            if not os.path.isdir(execution_dir):
                os.makedirs(execution_dir)
            result_xml = execution_dir + '/' + execution_name +'.xml'
            self.reporter.executionReport(dict1, [], [], [], result_xml, not excution_resume)
            pass_count_total = 0
            fail_count_total = 0
            TBD_count_total = 0
            pass_list_total = []
            fail_list_total = []
            TBD_list_total = []
            index = 0
            for testsuite in all_suites:
                index += 1
                print inblue("Suite " + str(index) + " in execution list:")
                test_suite_ins = TestSuite()
                if testsuite.text is None or testsuite.text.strip() == '':
                    continue
                    #raise TestException("Error: the text of Suitename element can't be empty in file " + str(original_execution_path))
                try:
                    suite_file = conf.SUITE_PATH + testsuite.text.strip() + '.xml'
                    if not check_suite_resume(testsuite.text.strip()):
                        createSuiteFromExecution(testsuite.text.strip())
                        createRemark(suite_file)
                    resume_suite_file = getResume('suite')
                    (pass_count, fail_count, TBD_count, pass_list, fail_list, TBD_list) = test_suite_ins.runTest(False, suite_file, resume_suite_file, dev_dict, 1, module_value, runtype, platform, [])
                except TestException, e:
                    suite_result_path = path.result_path + '/' + testsuite.text.strip()
                    if not os.path.exists(suite_result_path):
                        os.makedirs(suite_result_path)
                    error_report(suite_result_path + '/error.log', e.value + ' when running suite: ' + str(suite_file))
                    continue
                pass_count_total = pass_count_total + pass_count
                fail_count_total = fail_count_total + fail_count
                TBD_count_total = TBD_count_total + TBD_count
                pass_list_total.extend(pass_list)
                fail_list_total.extend(fail_list)
                TBD_list_total.extend(TBD_list)
                dict1 = {}  # clear pre_info, in case some info like start_time, name were written twice    
                dict1.setdefault('pass_count', pass_count_total)
                dict1.setdefault('fail_count', fail_count_total)
                dict1.setdefault('TBD_count', TBD_count_total)
                self.reporter.executionReport(dict1, pass_list, fail_list, TBD_list, result_xml, False)
            end_time = time.strftime(ISO_DATETIME_FORMAT, time.gmtime(time.time()))
            self.btpprint.execuitonEndPrint(execution_name, end_time, pass_count_total, fail_count_total, TBD_count_total, result_xml)
            dict1 = {}  # clear pre_info, in case some info like start_time, name were written twice 
            dict1.setdefault('end_time', end_time)
            self.reporter.executionReport(dict1, [], [], [], result_xml, False)
            deleteAllResume()
        except TestException, e:
            raise TestException(e.value)
        finally:
            sendMail(maillist)

            
class TestSuite:
    
    '''A class whose instances can execute test suite.'''
    
    def __init__(self):
        self.reporter = TestReport()
        self.btpprint = BTPprint.PytestPrint()
        
    def run_case_process(self, tcr, run_result_queue, casecfg, dev_dict, module_value, runtype, original_suite_path, platform):
        try:
            rt = tcr.runTest(casecfg, dev_dict, module_value, runtype, platform, [])
        except TestException, e:
            raise TestException(e.value + " when running suite profile: " + str(original_suite_path))
        run_result_queue.put(rt)
        
    def kill_all_subprocess_and_remove_result(self, case_profile, case_process, dev_dict, step_process_list, monitor_process_list, result_path_dict):
        kill_command_on_device(case_profile, dev_dict)
        for step_process_pid in step_process_list:
            try:
                os.kill(step_process_pid, signal.SIGTERM)
            except OSError, e:
                pass
        for monitor_process_id in monitor_process_list:
            try:
                os.kill(monitor_process_id, signal.SIGTERM)
            except OSError, e:
                pass
        case_process.terminate()
        for key, value in result_path_dict.items():
            cmd = 'rm -rf ' + value
            execute_command_on_server(cmd)
            
    def runTest(self, resume_flag, original_suite_path, resume_suite_path, dev_dict, startNo, module_value, runtype, platform, maillist):
        try:
            pass_count = 0
            fail_count = 0
            TBD_count = 0
            pass_list = []
            fail_list = []
            TBD_list = []
            suitename = ''
            try:
                root = ET.parse(resume_suite_path).getroot()
            except IOError, e:
                raise TestException("Error: the file: " + str(original_suite_path) + " not found")
            except ExpatError, e:
                raise TestException("Error: the file: " + str(original_suite_path) + " is in invalid xml format.")
            
            try:
                intro = root.find('intro').text
            except AttributeError, e:
                raise TestException("Error: no intro element found in file: " + str(original_suite_path))
            if intro is not None and intro.strip() != '':
                print "\n" + 'intro: ' + intro
            try:
                suitename = root.find('name').text.strip()
            except AttributeError, e:
                raise TestException("Error: no name element found in file: " + str(original_suite_path))
            if suitename is None or suitename == '':
                raise TestException("Error: the text of name element can't be empty in file: " + str(original_suite_path))
            all_cases = root.find('list')       
            if all_cases is None:
                raise TestException("Error: no list element found in file: " + str(original_suite_path))
            if len(all_cases) == 0:
                raise TestException("Error: no case in this suite profile: " + str(original_suite_path))
            list_len = len(all_cases)
            if startNo < 1 or startNo > list_len:
                raise TestException("Error: -n parameter should be larger than 0 and less than case amount in suite" + suitename)
            #delete the first "startNo" cases in SUITE_resume.xml
            if startNo > 1:
                if os.path.isfile(conf.TEST_REPO + "resume/SUITE_resume.xml"):
                    for i in range(startNo-1):
                        deleteCaseInSuiteResume(all_cases[i].text)
            dict1 = {}
            start_time = time.strftime(ISO_DATETIME_FORMAT, time.gmtime(time.time()))
            dict1.setdefault('start_time', start_time)
            dict1.setdefault('name', suitename)
            self.btpprint.suiteBeginPrint(suitename, list_len, start_time)
            if startNo == 1:
                print inpurple("Run suite from the first case: ")
            elif startNo == 2:
                print inpurple("Run suite from the second case: ")
            elif startNo == 3:
                print inpurple("Run suite from the third case: ")
            else:
                print inpurple("Run suite from the " + str(startNo + 1) + "th case: ")
            rtp = path.result_path + '/' + suitename
            if not os.path.isdir(rtp):
                os.makedirs(rtp)
            rtlog = rtp + '/' + suitename + '.xml'
            try:
                self.reporter.suiteReport(dict1, pass_list, fail_list, TBD_list, rtlog, not resume_flag)
            except TestException, e:
                raise TestException(e.value + ' when running suite profile: ' + str(original_suite_path))
            
            # if executed by suite or execution, then allow users to input n/f to execute next one or previous one
            i = startNo - 1
            while i < len(all_cases):
                tc = all_cases[i]
                print inblue("Case " + str(list(all_cases).index(tc) + 1) + ":")
                dict1 = {}  # clear dict1, in case pre_info was written twice
                manager = Manager()
                step_process_list = manager.list()
                monitor_process_list = manager.list()
                result_path_dict = manager.dict()
                tcr = TestCase(0, step_process_list, monitor_process_list, result_path_dict)
                if tc.text is None or tc.text.strip() == '':
                    continue
                try:                
                    casecfg = conf.CASE_PATH + tc.text.strip()
                except AttributeError, e:
                    raise TestException("Error: no CASE_PATH in conf.py")
                run_result_queue = Queue()
                case_process = Process(target=self.run_case_process, args=(tcr, run_result_queue, casecfg, dev_dict, module_value, runtype, original_suite_path, platform))
                case_process.start()
                while True:
                    sys.stdout.write('')
                    sys.stdout.flush()
                    if select([sys.stdin.fileno()], [], [], 5)[0]:
                        user_input = raw_input()
                        if user_input.strip().lower() == 'n':
                            i = i + 1
                            self.kill_all_subprocess_and_remove_result(casecfg, case_process, dev_dict, step_process_list, monitor_process_list, result_path_dict)
                            if os.path.isfile(conf.TEST_REPO + "resume/SUITE_resume.xml"):
                                deleteCaseInSuiteResume(tc.text.strip())
                            break
                        elif user_input.strip().lower() == 'f':
                            i = i - 1
                            self.kill_all_subprocess_and_remove_result(casecfg, case_process, dev_dict, step_process_list, monitor_process_list, result_path_dict)
                            if os.path.isfile(conf.TEST_REPO + "resume/SUITE_resume.xml"):
                                deleteCaseInSuiteResume(tc.text.strip())
                            break
                    if not run_result_queue.empty():
                        rt = run_result_queue.get()
                        if not cmp(rt, 'pass'):
                            pass_list.append(tc.text)
                            pass_count = pass_count + 1
                            dict1.setdefault('pass_count', pass_count)
                            self.reporter.suiteReport(dict1, [tc.text], [], [], rtlog, False)
                        elif not cmp(rt, 'TBD'):
                            TBD_list.append(tc.text)
                            TBD_count = TBD_count + 1
                            dict1.setdefault('TBD_count', TBD_count)
                            self.reporter.suiteReport(dict1, [], [], [tc.text], rtlog, False)
                        else:
                            fail_list.append(tc.text)
                            fail_count = fail_count + 1
                            dict1.setdefault('fail_count', fail_count)
                            self.reporter.suiteReport(dict1, [], [tc.text], [], rtlog, False)
                        print '\n'
                        i = i + 1
                        case_process.terminate()
#                        listen_process.terminate()
                        break
                    else:
                        time.sleep(1)
            end_time = time.strftime(ISO_DATETIME_FORMAT, time.gmtime(time.time()))
            self.btpprint.suiteEndPrint(suitename, end_time, pass_count, fail_count, TBD_count, rtlog)
            dict1 = {}  # clear dict1, in case pre_info was written twice
            dict1.setdefault('end_time', end_time)
            try:
                self.reporter.suiteReport(dict1, [], [], [], rtlog, False)
            except TestException, e:
                raise TestException(e.value + ' when running suite profile: ' + str(cfg))
            if os.path.isfile(conf.TEST_REPO + "resume/EXECUTION_resume.xml"):
                deleteSuiteInExecutionResume(suitename)
            deleteResume('suite')
            if runtype == 2:
                # run by execution, we should not delete remark file, delete the suite line only
                deleteResume('remark', original_suite_path)
            else:
                deleteResume('remark')
        except TestException, e:
            if runtype == 2:
                print inred(e.value)
                if suitename:
                    suite_result_path = path.result_path + '/' + suitename
                    if not os.path.isdir(suite_result_path):
                        os.makedirs(suite_result_path) 
                    error_report(suite_result_path + '/error.log', e.value)
                else:
                    error_report(path.result_path + '/error.log', e.value)
                deleteResume('suite')
                deleteResume('remark', original_suite_path)
                if os.path.isfile(conf.TEST_REPO + "resume/EXECUTION_resume.xml"):
                    deleteSuiteInExecutionResume(suitename)
                all_cases = root.find('list')       
                if all_cases is not None:
                    for case_item in all_cases:
                        if case_item.text is not None and case_item.text.strip() != '':
                            fail_list.append(case_item.text.strip())
                            fail_count += 1
            else:
                deleteResume('suite')
                deleteResume('remark')
                raise TestException(e.value)
            
        sendMail(maillist)
        return (pass_count, fail_count, TBD_count, pass_list, fail_list, TBD_list)



class TestCase:
    
    '''A class whose instances can execute test cases. '''

    def __init__(self, stepType, manager_step_process_list=None, manager_monitor_process_list=None, manager_result_path_dict=None):
        self.reporter = TestReport()
        self.btpprint = BTPprint.PytestPrint()
        self.stepType = stepType
        self.all_monitor_thread_dict = {}
        self.step_process_list = []
        self.manager_step_process_list = manager_step_process_list
        self.manager_monitor_process_list = manager_monitor_process_list
        self.manager_result_path_dict = manager_result_path_dict
        
    def run(self, step_id, func, data, dev_dict, crt, caseFolderName, runmodule, all_monitor_thread_dict, platform):
        module_info = func.split('.')
        if len(module_info) != 3:
            raise TestException("Error on case profile  ")
        if runmodule:
            module = runmodule
        else:
            module = module_info[0]
        cls = module_info[1]
        method = module_info[2]
        cmd = 'tc = ' + cls + '(step_id, data, dev_dict, crt, caseFolderName, all_monitor_thread_dict, self.stepType, platform).' + method + '()'
        try:
            exec('from test_module.' + module + ' import ' + cls)
        except ImportError:
            raise TestException("Error on the function attribute value ")
        exec(cmd)
        return tc
    
    def parseMonitorElement(self, root, ahead_monitor_dict, delay_monitor_dict, usual_monitor_dict, step_id, cfgfile, monitor_with_result_list):
        all_monitors = root.findall('Monitor')
        for monitor in all_monitors:
            monitor_parallel_id = monitor.get('step')
            if monitor_parallel_id is None:
                raise TestException("Error: step id invalid in Monitor: " + str(cfgfile))
            if monitor_parallel_id.strip() == step_id:
                monitor_name = monitor.get('name')
                if monitor_name is None or monitor_name.strip() == '':
                    raise TestException('Error: name invalid in Monitor: ' + str(cfgfile))
                schedule_ele = monitor.find('Schedule')
                if schedule_ele is None:
                    raise TestException("Error: Schedule invalid in  Monitor " + monitor_name + " in case file: " + str(cfgfile))
                criteria_ele = monitor.find('Criteria')
                if criteria_ele is not None:
                    monitor_with_result_list.append(monitor)
                begin_ele = schedule_ele.find('begin')
                if begin_ele is None:
                    raise TestException("Error: begin element invalid in Monitor " + monitor_name + " in case file: " + str(cfgfile))
                time = begin_ele.text
                if time is None or time.strip() == '':
                    raise TestException("Error: begin element invalid in Monitor element with name " + monitor_name + " in case file: " + str(cfgfile))
                try:
                    float_time = float(time)
                except ValueError, e:
                    raise TestException("Error: text of begin element should be a number in Monitor element with name " + monitor_name + " in case file: " + str(cfgfile))
                if float_time <= 0:
                    temp_dict = usual_monitor_dict
                else:
                    operator_value = begin_ele.get('operator')
                    if operator_value is None or operator_value.strip() not in ['delay', 'ahead']:
                        raise TestException("Error: operator attribute should exist and its value should be delay/ahead if begin text greater than 0 in Monitor element with name " + monitor_name + " in case file: " + str(cfgfile))
                    if  operator_value.strip() == 'ahead':
                        temp_dict = ahead_monitor_dict
                    elif operator_value.strip() == 'delay':
                        temp_dict = delay_monitor_dict
                try:
                    #if monitor name duplicate, it will overridden
                    temp_dict.update({monitor_name: [MONITOR_THREAD_REF_DICT[monitor_name], monitor, float_time]})
                except KeyError, e:
                    raise TestException("Error: monitor name: " + monitor_name + " is wrong, it should be one of " + ', '.join(MONITOR_THREAD_REF_DICT.keys()) + "in case file: " + str(cfgfile))
    
    def start_monitor_thread(self, all_monitor_thread_dict, monitor_dict, cfgfile, aheadflag, caseFolderName, device_dict, monitor_exception_queue, monitor_result_queue, case_result_path):
        # if start as usual
        if aheadflag == '':
            for key, value in monitor_dict.items():
                monitor_name = key
                monitor_thread_name = value[0]
                monitor_ele = value[1]
                cmd = 'monitor_thread=Process(target=' + monitor_thread_name + ', args=(caseFolderName, monitor_ele, device_dict, monitor_exception_queue, monitor_result_queue, case_result_path))'
                exec(cmd)
                monitor_thread.start()
                all_monitor_thread_dict.update({monitor_thread: monitor_ele})
                if self.manager_monitor_process_list is not None:
                    self.manager_monitor_process_list.append(monitor_thread.pid)
                start_time = time.strftime(ISO_DATETIME_FORMAT, time.gmtime(time.time()))
                print inred('monitor ' + monitor_name + ' start at: '), inred(start_time)
        else:
            #sort by sleep time with reverse
            sorted_monitor_dict = sorted(monitor_dict.items(), key=lambda d: d[1][2], reverse=aheadflag) 
            for i in range(len(sorted_monitor_dict)):
                monitor_name = sorted_monitor_dict[i][0]
                monitor_thread_name = sorted_monitor_dict[i][1][0]
                monitor_ele = sorted_monitor_dict[i][1][1]
                cmd = 'monitor_thread=Process(target=' + str(monitor_thread_name) + ', args=(caseFolderName, monitor_ele, device_dict, monitor_exception_queue, monitor_result_queue, case_result_path))'
                exec(cmd)
                all_monitor_thread_dict.update({monitor_thread: monitor_ele})
                if self.manager_monitor_process_list is not None:
                    self.manager_monitor_process_list.append(monitor_thread.pid)
                first_sleep_time = sorted_monitor_dict[i][1][2]
                if aheadflag:
                    # if ahead, sleep time should sort reverse, and for the last monitor, it sleep directly, for others, its sleep time is first time minus the second 
                    # start first, and then sleep
                    start_time = time.strftime(ISO_DATETIME_FORMAT, time.gmtime(time.time()))
                    print inred('monitor ' + monitor_name + ' start at: '), inred(start_time)
                    monitor_thread.start()
                    if i == len(sorted_monitor_dict) -1:
                        time.sleep(first_sleep_time)
                    else:
                        second_sleep_time = sorted_monitor_dict[i+1][1][2]
                        time.sleep(first_sleep_time - second_sleep_time)
                else:
                    # if delay, sleep time should sort first, and for the first monitor, it sleep directly, for others, its sleep time is second time minus the first 
                    # sleep first, and then start
                    if i == 0:
                        time.sleep(first_sleep_time)
                    else:
                        second_sleep_time = sorted_monitor_dict[i-1][1][2]
                        time.sleep(first_sleep_time - second_sleep_time)
                    monitor_thread.start()
                    start_time = time.strftime(ISO_DATETIME_FORMAT, time.gmtime(time.time()))
                    print inred('monitor ' + monitor_name + ' start at: '), inred(start_time)
                    
    def kill_step_process(self):
        for process in self.step_process_list:
            process.terminate()
            
    def kill_monitor_thread(self, all_alive_thread_dict, result_path, device_dict, all_kill_flag, step_id): 
        if not device_dict.get('Connect', ''):
            raise TestException("Error: no Connect element found in device's profile")
        if not device_dict.get('Connect', '') in ['ssh', 'adb']:
            raise TestException("Error: the text of Connect element should be ssh or adb in device's profile ")            
        if not cmp(device_dict['Connect'], 'ssh'):
            from tools.client import sshAccessor as accessor
        if not cmp(device_dict['Connect'], 'adb'):
            from tools.client import adbAccessor as accessor
        self.cli = accessor(device_dict)
        kill_logcat(device_dict)
        kill_kernel_log(device_dict)
        for  monitor in all_alive_thread_dict.keys():
            monitor_ele = all_alive_thread_dict[monitor]
            if all_kill_flag:
                # all_kill_flag means exit unusually, maybe exception occurs
                monitor.terminate()
            else:
                # process in KILL_MONITOR_NAME is no_dead process, so we need to kill them if step exit
                if monitor_ele.get('name').strip() in KILL_MONITOR_NAME:
                    monitor.terminate()
                    #if exit naturally, after kill monitor process, we should put the result file to the case result directory, and then delete local files
                    parameter_ele = monitor_ele.find('Parameter')
                    file_name = ''
                    if parameter_ele is not None:
                        output_eles = parameter_ele.findall('output')
                        if len(output_eles) == 0:
                            raise TestException("Error: <output object='log'></output> should exist in Monitor element with name logcat")
                        output_log_exist_flag = False
                        #check if <output object="log"></output> exists
                        for output in output_eles:
                            if output.get('object') is not None and output.get('object').strip() == 'log':
                                output_log_exist_flag = True
                                output_text= output.text
                                if output_text is not None and output_text.strip() != '':
                                    file_name = output_text
                                break
                        if file_name == '':
                            if monitor_ele.get('name').strip() == 'kernel_log':
                                file_name = 'step_' + step_id + '_kernel_log'
                            elif monitor_ele.get('name').strip() == 'logcat':
                                file_name = 'step_' + step_id + '_logcat'
                        cmd = 'test -f ' + DEVICE_DATA_DIR + str(file_name)  + " && echo 'file exists' || echo 'file not found'"
                        stdout, stderr = self.cli.execute(cmd)
                        if stdout.strip() == 'file exists':
                            self.cli.execute_on_host(' pull ' + DEVICE_DATA_DIR + str(file_name) + ' ' + str(result_path))
                            self.cli.execute(' rm -rf ' + DEVICE_DATA_DIR + str(file_name))
    
    def get_step_result(self, exception_queue, result_queue, step_process_list, monitor_with_result_list, all_monitor_thread_dict, xmllog, case_result_path, device_dict, cfgfile):
        """
            when the program can exit:
            1.if one step fail, all other parallel steps and monitors will be forced exit
            2.if one monitor with result fail, the program should wait until any step's result come out
        """
        step_result_count = 0
        monitor_result_count = 0
        step_result = ''
        monitor_result = ''
        final_step_result = ''
        while True:
            if not exception_queue.empty():
                error_info = exception_queue.get(block=False)
                raise TestException(error_info + ' when running case profile: ' + str(cfgfile))
            if not result_queue.empty():
                result_info = result_queue.get()
                
                if not type(result_info[0]).__name__ == 'tuple':
                    id_info = result_info[0]
                    first_figure = id_info.split('_')
                    if first_figure[0] == 'step':
                        step_id = first_figure[1]
                        step_result = result_info[1]
                        command_result_dict = result_info[2]
                        if command_result_dict == "noResult":
                            command_result_dict = {}
                        command_result_dict.update({'result': step_result})
                        step_result_dict = {step_id: command_result_dict}
                        try:
                            if self.stepType == 0 or self.stepType == 20:
                                self.reporter.caseReport({}, step_result_dict, {}, xmllog, False)
                        except TestException, e:
                            raise TestException(e.value + ' when running case profile: ' + str(cfgfile))
                        if step_result == 'fail':
                            kill_command_on_device(cfgfile, device_dict)
                            self.kill_step_process()
                            self.kill_monitor_thread(all_monitor_thread_dict, case_result_path + '/', device_dict, True, step_id)
                            break
                        else:
                            step_result_count += 1
                else:
                    for result_item in result_info:
                        attr_dict = result_item[1][1]
                        step_id=int(attr_dict['step'])
                        ele_info = result_item[1][2]
                        for child_item in ele_info:
                            if child_item[0] == 'result':
                                monitor_result = child_item[1][0]
                    try:
                        if self.stepType == 0 or self.stepType == 20:
                            self.reporter.caseReport({}, {}, result_info, xmllog, False)
                    except TestException, e:
                        raise TestException(e.value + ' when running case profile: ' + str(cfgfile))
                    monitor_result_count += 1
#            print "step_result_count: ", step_result_count
#            print "len(step_process_list): ", len(step_process_list)
#            print "monitor_result_count: ", monitor_result_count
#            print "len(monitor_with_result_list): ", len(monitor_with_result_list)
            if(step_result_count == len(step_process_list) and monitor_result_count == len(monitor_with_result_list)):
                #if all success, we should kill name in KILL_MONITOR_NAME monitor, because they will run all the time
                self.kill_monitor_thread(all_monitor_thread_dict, case_result_path + '/', device_dict, False, step_id)
                break
            time.sleep(1)
        if monitor_with_result_list:
            if step_result == 'pass' and monitor_result == 'pass':
                final_step_result = 'pass'
            else:
                final_step_result = 'fail'
        else:
            final_step_result = step_result
        return final_step_result
                
    def runTest(self, cfg, dev_dict, runmodule, runtype, platform, maillist):
        """
            the final case result:
            monitor(with result)      step        run_next_step        case
            fail                     pass        no                    fail
            fail                     fail        no                    fail
            pass                     fail        no                    fail
            pass                    pass        yes                   pass(all steps and monitors are pass)
            
        """
        try:
            #dict1 will record case result info
            dict1 = {}
            casename = ''
            case_result = ''
            cfgfile = cfg + '/run.xml'
            cfgfile = str(cfgfile).replace('//', '/')
            
            #parse case profile
            try:
                root = ET.parse(cfgfile).getroot()
            except IOError, e:
                raise TestException("Error: the file: " + str(cfgfile) + " can not be found.")
            except ExpatError, e:
                raise TestException("Error: the file: " + str(cfgfile) + " is in invalid xml format.")
            caseFolderName = cfgfile.split('/')[-2]
            try:
                intro = root.find('intro').text
            except AttributeError, e:
                raise TestException("Error: no intro element found in " + str(cfgfile))
            if intro is not None and intro.strip() != '':
                print "\n" + 'intro: ' + intro
            try:
                casename = root.find('name').text
            except AttributeError, e:
                raise TestException("Error: no name element found in " + str(cfgfile))
            if casename is None or casename.strip() == '':
                raise TestException("Error: the text of name element can't be empty in case profile: " + str(cfgfile))
            dict1.setdefault('name', casename)
            try:
                executiontype = root.find('executiontype').text
            except AttributeError, e:
                raise TestException("Error: no executiontype element found in " + str(cfgfile))
            if executiontype is None or executiontype.strip() == '':
                raise TestException("Error: the text of executiontype element can't be empty in case profile: " + str(cfgfile))
            
            #obtain case id
            try:
                case_id = root.find('case_id').text
            except AttributeError, e:
                case_id = "Off"
            if case_id is None or case_id.strip() == '':
                case_id = "Off"
            dict1.setdefault('case_id', case_id)
            
            #obtain execution id
            try:
                execution_id = root.find('execution_id').text
            except AttributeError, e:
                execution_id = "Off"
            if execution_id is None or execution_id.strip() == '':
                execution_id = "Off"
            dict1.setdefault('execution_id', execution_id)
            
            start_time = time.strftime(ISO_DATETIME_FORMAT, time.gmtime(time.time()))
            self.btpprint.caseBeginPrint(caseFolderName, start_time)
            #download clips
            returnValue = downloadClip(cfgfile, dev_dict)
            if returnValue == "finished":
                print ingreen("Clips download finished")
            elif returnValue == "No clip need to download":
                pass
            else:
                print inred(returnValue)
                
            case_result_path = path.result_path + '/' + caseFolderName
            if self.manager_result_path_dict is not None:
                self.manager_result_path_dict['result_path'] = case_result_path
            if not os.path.isdir(case_result_path): 
                os.makedirs(case_result_path) 
            xmllog = case_result_path + '/' + caseFolderName + '.xml'
            dict1.setdefault('start_time', start_time)
            try:
                if self.stepType == 0 or self.stepType == 20:
                    self.reporter.caseReport(dict1, {}, {}, xmllog, True)
            except TestException, e:
                raise TestException(e.value + ' when running case profile: ' + str(cfgfile))
            all_steps = root.findall('Step')
            if all_steps is None or not all_steps:
                raise TestException("Error: no Step element found in " + str(cfgfile))
            # ran_parallel_id_list will record all step's parallel value which have been run, so if it had been run with other steps, it won't run again.
            ran_parallel_id_list = []
            # step_id_list will record all step's id, to make sure no duplicate step id
            step_id_list= []
            for step in all_steps:
                enabled_flag = step.get('enabled', 'no_enabled')  # if no enabled attribute, the step will still run
                if enabled_flag != 'no_enabled' and enabled_flag not in ['on', 'off']:
                    raise TestException("Error:  the enabled attribute of Step if exists, its value should be on or off with file: " + str(cfgfile))
                parallel_id = step.get('parallel', 'no_parallel')
                if parallel_id != 'no_parallel':
                    try:
                        int(parallel_id)
                    except (ValueError,TypeError), e:
                        raise TestException("Error:  the parallel attribute of Step if exists, its value should be a number in file: " + str(cfgfile))
                if enabled_flag == 'off' or ((enabled_flag == 'on' or enabled_flag == 'no_enabled') and parallel_id in ran_parallel_id_list):
                    #if enabled is off, or enabled is on but it has been run with the other steps it means that this step doesn't need to run 
                    continue
                step_id = step.get('id', '').strip()
                if step_id == '':
                    raise TestException("Error: no id attribute found in Step with file: " + str(cfgfile))
                try:
                    int(step_id)
                except (TypeError, ValueError), e:
                    raise TestException("Error: the value of id attribute must be a number in Step with file: " + str(cfgfile))
    
                print "------Step%s------" %step_id
                if step_id in step_id_list:
                    raise TestException("Error: the value of id attribute of Step is the same with other Step, they should be unique in the file: " + str(cfgfile))
                step_id_list.append(step_id)
                parallel_step_list = []  
                #parallel=0 or no parallel attribute indicates this step will run alone
                if parallel_id == 'no_parallel' or int(parallel_id) == 0:
                    parallel_step_list.append(step)
                else:
                    if int(parallel_id) != 0:
                        ran_parallel_id_list.append(parallel_id)
                        for new_step in all_steps:
                            if new_step.get('enabled') == 'on' or new_step.get('enabled', 'no_enabled') == 'no_enabled':
                                if new_step.get('parallel') == parallel_id:
                                    #the first step is added here, and so don't need to eliminate itself
                                    parallel_step_list.append(new_step)
                                    
                # delay_monitor_dict used to recored delay monitor, it's format is monitor_name: [monitor_thread_name, monitor_ele, sleep_time]
                delay_monitor_dict = {}
                # ahead_monitor_dict used to recored ahead monitor, it's format is monitor_name: [monitor_thread_name, monitor_ele, sleep_time]
                ahead_monitor_dict = {}
                # usual_monitor_dict used to recored usual monitor, it's format is monitor_name: [monitor_thread_name, monitor_ele, sleep_time]
                usual_monitor_dict = {}
                # monitor_with_result_list used to record monitor thread with result, because the case result will be influenced by the matrix monitor result
                monitor_with_result_list = []
                self.parseMonitorElement(root, ahead_monitor_dict, delay_monitor_dict, usual_monitor_dict, step_id, cfgfile, monitor_with_result_list)
                #monitor and step use one result_queue
                result_queue = Queue()
                #monitor and step use one exception_queue, because main process can't get the child process's exception directly, so we use queue
                exception_queue = Queue()
                try:
                    if ahead_monitor_dict:
                        self.start_monitor_thread(self.all_monitor_thread_dict, ahead_monitor_dict, cfgfile, True, caseFolderName, dev_dict, exception_queue,  result_queue, case_result_path)                
                    if usual_monitor_dict:
                        self.start_monitor_thread(self.all_monitor_thread_dict, usual_monitor_dict, cfgfile, '', caseFolderName, dev_dict, exception_queue, result_queue, case_result_path)
                    for i in range(len(parallel_step_list)):
                        tclog = case_result_path + '/' + str(parallel_step_list[i].get('id')) + '.log'
                        step_process = Process(target=executeStep, args=(parallel_step_list[i], dev_dict, tclog, result_queue, exception_queue, caseFolderName, runmodule, self.all_monitor_thread_dict, self.stepType, platform))
                        step_process.start()
                        self.step_process_list.append(step_process)
                        if self.manager_step_process_list is not None:
                            self.manager_step_process_list.append(step_process.pid)
                        
                        start_time = time.strftime(ISO_DATETIME_FORMAT, time.gmtime(time.time()))
                        print inred('step with id '+ parallel_step_list[i].get('id') + ' start at: '), inred(start_time)
                    if delay_monitor_dict:
                        self.start_monitor_thread(self.all_monitor_thread_dict, delay_monitor_dict, cfgfile, False, caseFolderName, dev_dict, exception_queue, result_queue ,case_result_path)
                    step_result = self.get_step_result(exception_queue, result_queue, self.step_process_list, monitor_with_result_list, self.all_monitor_thread_dict, xmllog, case_result_path, dev_dict, cfgfile)
                except TestException, e:
                    self.kill_step_process()
                    self.kill_monitor_thread(self.all_monitor_thread_dict, case_result_path + '/', dev_dict, True, step_id)
                    raise TestException(e.value)
                #if some step fails, then exit the whole case circle
                if step_result == 'fail':
                    break
            case_result = step_result
            end_time = time.strftime(ISO_DATETIME_FORMAT, time.gmtime(time.time()))
            dict1 = {}
            dict1.setdefault('end_time', end_time)
            if executiontype.strip().lower() == 'semi_auto' or executiontype.strip().lower() == 'semi-auto':
                if case_result == 'pass':
                    case_result = 'TBD'
            self.btpprint.caseEndPrint(caseFolderName, end_time, case_result, xmllog)
            dict1.setdefault('result', case_result)
            if os.path.isfile(conf.TEST_REPO + "resume/SUITE_resume.xml"):
                deleteCaseInSuiteResume(caseFolderName)
            try:
                if self.stepType == 0 or self.stepType == 20:
                    self.reporter.caseReport(dict1, {}, {}, xmllog, False)
            except TestException, e:
                raise TestException(e.value + ' in file: ' + str(cfgfile))
        except TestException, e:
            case_result = 'fail'
            if runtype == 1 or runtype == 2:
                print inred(e.value)
                if casename:
                    case_result_path = path.result_path + '/' + casename
                    if not os.path.isdir(case_result_path):
                        os.makedirs(case_result_path) 
                    error_report(case_result_path + '/error.log', e.value)
                else:
                    error_report(path.result_path + '/error.log', e.value)
                if os.path.isfile(conf.TEST_REPO + "resume/SUITE_resume.xml"):
                    deleteCaseInSuiteResume(casename)
            else:
                print inred(e.value)
                sys.exit(0)
        
        sendMail(maillist)
        return case_result
    
class TestProgram:
    
    '''A command-line program that runs a set of tests.'''
    
    def __init__(self, argv=None):
        """
            if exception happens, but if it doesn't influence executing the next case, the program should not exit.
            the program should exit:
            1. the device is bad
            2. the adb connect is bad
            3. the path.py created by setup.py is bad
        """
        try:
            argv = argv or sys.argv[1:]
            self.parseArgs(argv)
            
            # check device profile
            self.check_device_path()
            
            # check path.py
            check_item_in_path()
            
            # check environment
            check_adb_connect(self.options.device)
            if self.options.execution is not None:
                check_build_name(self.options.execution)
            #check_paramiko()
            #check_jpeg()
            self.runTest()
        except TestException, e:
            print inred(e.value)
            sys.exit(0)
            
        

    def check_device_path(self):
        '''
        check if testers figure -d parameter, if not, we'll use path.default_dev instead, or do nothing.
        '''
        # self.options is just in dictionary format, but if u want to get its key-value, u can't use self.options.get() or self.options[key], please use self.options.key
        if self.options.device is None:
            self.options.device = conf.DEFAULT_DEVICE_PATH
            print inblue("Default device profile used.")
        check_device_profile(self.options.device)
        self.dev_dict = XMLParser.XMLParser(self.options.device).ClientParser()
        
    def parseArgs(self, argv):
        writeCommand(argv)
        usage = "usage: python %prog [options]"
        parser = OptionParser(usage=usage)
        parser.add_option('-c', '--case', dest='case', help="case's configure file", default=None)
        parser.add_option('-s', '--suite', dest='suite', help="suite's configure file", default=None)
        parser.add_option('-e', '--execution', dest='execution', help="execution's configure file", default=None)
        parser.add_option('-d', '--device', dest='device', help="device's configure file", default=None)
        parser.add_option('-n', '--startNo', dest='startNo', help="start running number in suite", default=None)
        parser.add_option('-m', '--module', dest='module', help="switch module", default=None)
        parser.add_option('-p', '--platform', dest='platform', help="switch platform", default=None)
        parser.add_option('-t', '--step', dest='step', help="execute which step of the case. 0:default, 10:prepare, 20:execute, 30:pull result", default=None)       
        parser.add_option('--mail', dest='mail', help="send mail after execution.", default=None)
        self.options, args = parser.parse_args(argv)
        # check -c, -s, -e, should input one of them, and at most one kind.
        if self.options.case is None and self.options.suite is None and self.options.execution is None:
            print parser.print_help()
            raise TestException("Error: make sure you input one of -c, -e, -s as parameter ")
        elif (self.options.case is not None and (self.options.suite is not None or self.options.execution is not None)) or \
            (self.options.suite is not None and (self.options.case is not None or self.options.execution is not None)) or \
            (self.options.execution is not None and (self.options.suite is not None or self.options.case is not None)):
                raise TestException("Error: You can only select one of -c, -s and -e.")

        #check whether has parameter -n and whether value of -n is correct
        if self.options.startNo is not None:
            if self.options.case is not None or self.options.execution is not None:
                raise TestException("Error: you can not input -n when executing case or execution, only for suite!")
            try:
                self.suiteStartNo = int(self.options.startNo)
            except (ValueError, TypeError), e:
                raise TestException("Error: the value of parameter -n must be a number!")
        else:
            self.suiteStartNo = 1
            
        # check -t and its validity
        self.stepType = 0
        if self.options.step is not None:
            if self.options.case is not None and self.options.suite is None and self.options.execution is None:
                if self.options.step == '0':
                    pass
                elif self.options.step == '10':
                    self.stepType = 10
                elif self.options.step == '20':
                    self.stepType = 20
                elif self.options.step == '30':
                    self.stepType = 30
                else:
                    print parser.print_help()
                    raise TestException("Error: Incorrect value of parameter -t.") 
            else:
                raise TestException("Error: -t parameter is only for case, we'll ignore it.")
            
        #check --mail
        
        if self.options.mail is not None:
            self.maillist = checkMailList(self.options.mail)
        else:
            self.maillist = []

    
    def runTest(self):
        # execute body 
        if self.options.case is not None and self.options.suite is None and self.options.execution is None:
            TestCase(self.stepType).runTest(self.options.case, self.dev_dict, self.options.module, 0, self.options.platform, self.maillist)
        elif  self.options.case is None and self.options.suite is not None and self.options.execution is None:
            # whatever the user use resume, we'll still create resume.xml, and use this for executing.
            resume_flag = True
            if not checkResume('suite', self.options.suite):
                #not resume
                resume_flag = False 
                createRemark(self.options.suite)
                createResume(self.options.suite, 'suite')
            TestSuite().runTest(resume_flag, self.options.suite, getResume('suite'), self.dev_dict, self.suiteStartNo, self.options.module, 1, self.options.platform, self.maillist)
        
        elif self.options.case is None and self.options.suite is None and self.options.execution is not None:
            # whatever the user use resume, we'll still create resume.xml, and use this for executing.
            excution_resume = True
            if not checkResume('execution', self.options.execution):
                # not resume
                excution_resume = False
                createRemark(self.options.execution)
                createResume(self.options.execution, 'execution')
#                createSuiteFromExecution()
            TestExecution().runTest(excution_resume, self.options.execution, getResume('execution'), self.dev_dict, self.options.module, 2, self.options.platform, self.maillist)
                        
if __name__ == "__main__":
    TestProgram()



