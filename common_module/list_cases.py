'''
    list all cases in this execution, and there must only one execution xml file under config.EXECUTION_PATH,
    and it is the execution profile about to be executed.
'''
import os
from xml.etree import ElementTree as ET

import conf
from exception.testexception import TestException

def list_cases(print_flag, build_name):
    case_name_list = []

    try:
        tree = ET.parse(conf.EXECUTION_PATH + build_name + '.xml')
    except IOError:
        raise TestException("Error: %s%s.xml doesn't exist." %(conf.EXECUTION_PATH, build_name))
    root = tree.getroot()
    suite_name_list = root.find('list')
    for suite_name in suite_name_list:
        files = os.listdir(conf.SUITE_PATH)
        for child_f in files:
            if child_f == suite_name.text + '.xml':
                tree= ET.parse(conf.SUITE_PATH + child_f)
                root = tree.getroot()
                case_list = root.find('list')
                for case_ele in case_list:
                    if print_flag:
                        print "Suite Name: " + suite_name.text + "\t\tCase Name: " + case_ele.text 
                    else:
                        case_name_list.append(case_ele.text)
                        
    return case_name_list
