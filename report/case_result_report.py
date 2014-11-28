import os
from xml.etree import ElementTree as ET

from common_module.list_cases import list_cases
import conf
from tools.color import inred, ingreen, inblue
from exception.testexception import TestException

def test_report():
    case_list = list_cases(False)
    try:
        files = os.listdir(conf.RESULT_PATH)
    except OSError:
        raise TestException("Error: %s doesn't exist." %conf.RESULT_PATH) 
    i = 0
    for build_name in files:
        report_file = open(conf.RESULT_PATH + build_name + '/test_report', 'w')
        report_file.write("TestCaseName".ljust(50) +"Result"  + '\n\n')
        test_files = os.listdir(conf.RESULT_PATH + build_name)
        for case_name in case_list:
            for result_name in test_files:
                if result_name == case_name:
                    case_result_files = os.listdir(conf.RESULT_PATH + build_name + '/' + result_name)
                    for logname in case_result_files:
                        if logname == case_name + '.xml':
                            i = i + 1
                            tree = ET.parse(conf.RESULT_PATH + build_name + '/' + result_name + '/' + case_name + '.xml')
                            root = tree.getroot()
                            result = root.find('result').text
                            if result is None:
                                result = ''
                            report_file.write(case_name.ljust(50) + result + '\n')
        report_file.close()
    if i != len(case_list):
        print inblue("Warning: the number of cases with result isn't the same with the number of cases in the execution, maybe some cases don't have result")
