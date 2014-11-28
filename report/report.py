import shutil
import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
import os

from exception.testexception import TestException
import conf
try:
    from conf import path
except ImportError, e:
    print inred("ERROR: no path.py found, please run setup.py again.")
    sys.exit(2)

class TestReport:
    
    ''' A class for generate test report'''
    
    def __init__(self):
        pass
    
    def caseReport(self, dict1, step_info_dict, monitor_info_list, log, first_flag):
        #step_info_dict's format is {'step_id': {step_output_dict}}
        #monitor_info_list's format is [(tag_name, [tag_text, tag_attr_dict, tag_child_list]), and tag_child_list 's format is also like [(tag_name, [tag_text, tag_attr_dict, tag_child_dict]],
        # it'a a recursion
        if first_flag:
            try:
                if not os.path.isfile(conf.CASE_LOG):
                    raise TestException("Error: the file defined by conf.CASE_LOG doesn't exist ")
            except AttributeError, e:
                raise TestException("Error: no CASE_LOG found in conf.py ")   
            shutil.copyfile(conf.CASE_LOG, log)
        try:
            tree = ET.parse(log)
        except IOError, e:
            raise TestException("Error: the file: " + str(conf.CASE_LOG) + " can not found")
        except ExpatError, e:
            raise TestException("Error: the file: " + str(conf.CASE_LOG) + " is invalid, please check if all tags are matched or missed some signs.")
        root = tree.getroot()
        result_ele = root.find('result')
        if result_ele is None:
            raise TestException("Error: no result element found in the file: " + str(conf.CASE_LOG))
        name_ele = root.find('name')
        if name_ele is None:
            raise TestException("Error: no name element found in the file: " + str(conf.CASE_LOG))
        case_id_ele = root.find('case_id')
        if case_id_ele is None:
            raise TestException("Error: no case_id element found in the file: " + str(conf.CASE_LOG))
        execution_id_ele = root.find('execution_id')
        if execution_id_ele is None:
            raise TestException("Error: no execution_id element found in the file: " + str(conf.CASE_LOG))
        begin_time_ele = root.find('begin_time')
        if begin_time_ele is None:
            raise TestException("Error: no begin_time element found in the file: " + str(conf.CASE_LOG))
        end_time_ele = root.find('end_time')
        if end_time_ele is None:
            raise TestException("Error: no end_time element found in the file: " + str(conf.CASE_LOG))
        execute_information_ele = root.find('execute_information')
        if execute_information_ele is None:
            raise TestException("Error: no execute_information element found in the file: " + str(conf.CASE_LOG))
        
        if dict1.get('result'):
            result_ele.text = dict1.get('result', '')
        if dict1.get('name'):
            name_ele.text = dict1.get('name', '')
        if dict1.get('case_id'):
            case_id_ele.text = dict1.get('case_id', '')
        if dict1.get('execution_id'):
            execution_id_ele.text = dict1.get('execution_id', '')
        if dict1.get('start_time'):
            begin_time_ele.text = dict1.get('start_time', '')
        if dict1.get('end_time'):
            end_time_ele.text = dict1.get('end_time', '')
        if step_info_dict:
            for key, value in step_info_dict.iteritems():
                step_ele = ET.SubElement(execute_information_ele, 'step')
                step_ele.set('id', key)
                for k,v in value.iteritems():
                    step_child = ET.SubElement(step_ele, k)
                    step_child.text = str(v)
        if monitor_info_list:
            self.create_child_ele(monitor_info_list, execute_information_ele)
        tree.write(log)
    
    def create_child_ele(self, child_list, parent_ele):
        for first_item in child_list:
                new_ele = ET.SubElement(parent_ele, first_item[0])
                tag_text = first_item[1][0]
                attr_dict = first_item[1][1]
                new_child_list= first_item[1][2]
                new_ele.text=tag_text
                for attr_name, attr_value in attr_dict.iteritems():
                    new_ele.set(attr_name, attr_value)
        if new_child_list:
            self.create_child_ele(new_child_list, new_ele)   
            
    def suiteReport(self, dict1, list1, list2, TBD_list, result_xml, first_flag):
        if first_flag:
            try:
                shutil.copyfile(conf.SUITE_LOG, result_xml)
            except AttributeError, e:
                raise TestException("Error: no SUITE_LOG in conf.py")
            except IOError, e:
                raise TestException("Error: the file defined by conf.SUITE_LOG doesn't exist ")
        try:
            tree = ET.parse(result_xml)
        except IOError, e:
            raise TestException("Error: the file: " + str(conf.SUITE_LOG) + " can not found")
        except ExpatError, e:
            raise TestException("Error: the file: " + str(conf.SUITE_LOG) + " is invalid, please check if all tags are matched or missed some signs.")
        root = tree.getroot()
        name_ele = root.find('name')
        if name_ele is None:
            raise TestException("Error: no name element found in the file: " + str(conf.SUITE_LOG))
        begin_time_ele = root.find('begin_time')
        if begin_time_ele is None:
            raise TestException("Error: no begin_time element found in the file: " + str(conf.SUITE_LOG))
        end_time_ele = root.find('end_time')
        if end_time_ele is None:
            raise TestException("Error: no end_time element found in the file: " + str(conf.SUITE_LOG))
        pass_count_ele = root.find('pass_count')
        if pass_count_ele is None:
            raise TestException("Error: no pass_count element found in the file: " + str(conf.SUITE_LOG))
        fail_count_ele = root.find('fail_count')
        if fail_count_ele is None:
            raise TestException("Error: no fail_count element found in the file: " + str(conf.SUITE_LOG))
        TBD_count_ele = root.find('TBD_count')
        if TBD_count_ele is None:
            raise TestException("Error: no TBD_count element found in the file: " + str(conf.SUITE_LOG))
        pass_list_ele = root.find('pass_list')
        if pass_list_ele is None:
            raise TestException("Error: no pass_list element found in the file: " + str(conf.SUITE_LOG))
        fail_list_ele = root.find('fail_list')
        if fail_list_ele is None:
            raise TestException("Error: no fail_list element found in the file: " + str(conf.SUITE_LOG))
        TBD_list_ele = root.find('TBD')
        if TBD_list_ele is None:
            raise TestException("Error: no TBD element found in the file: " + str(conf.SUITE_LOG))
        
        if dict1.get('name', ''):
            name_ele.text = dict1.get('name', '')
        if dict1.get('start_time', ''):
            begin_time_ele.text = dict1.get('start_time', '')
        if dict1.get('end_time', ''):
            end_time_ele.text = dict1.get('end_time', '')
        if dict1.get('pass_count', ''):
            pass_count_ele.text = str(dict1.get('pass_count', ''))
        if dict1.get('fail_count', ''):
            fail_count_ele.text = str(dict1.get('fail_count', ''))
        if dict1.get('TBD_count', ''):
            TBD_count_ele.text = str(dict1.get('TBD_count', ''))
        if list1:
            pl = pass_list_ele
            for cn in list1:
                ke = ET.SubElement(pl, 'case_name')
                ke.text = cn
        if list2:
            fl = fail_list_ele
            for cn in list2:
                ke = ET.SubElement(fl, 'case_name')
                ke.text = cn
        if TBD_list:
            for cn in TBD_list:
                ke = ET.SubElement(TBD_list_ele, 'case_name')
                ke.text = cn
        tree.write(result_xml)
        
    def executionReport(self, dict1, list1, list2, TBD_list, result_xml, first_flag):
        if first_flag:
            try:
                shutil.copyfile(conf.EXECUTION_LOG, result_xml)
            except AttributeError, e:
                raise TestException("Error: no EXECUTION_LOG found in conf.py ")
            except IOError, e:
                raise TestException("Error: the file defined by conf.EXECUTION_LOG doesn't exist ")
        try:
            tree = ET.parse(result_xml)
        except IOError, e:
            raise TestException("Error: the file: " + str(conf.EXECUTION_LOG) + " can not found")
        except ExpatError, e:
            raise TestException("Error: the file: " + str(conf.EXECUTION_LOG) + " is invalid, please check if all tags are matched or missed some signs.")
        root = tree.getroot()
        name_ele = root.find('name')
        if name_ele is None:
            raise TestException("Error: no name element found in the file: " + str(conf.EXECUTION_LOG))
        begin_time_ele = root.find('begin_time')
        if begin_time_ele is None:
            raise TestException("Error: no begin_time element found in the file: " + str(conf.EXECUTION_LOG))
        end_time_ele = root.find('end_time')
        if end_time_ele is None:
            raise TestException("Error: no end_time element found in the file: " + str(conf.EXECUTION_LOG))
        pass_count_ele = root.find('pass_count')
        if pass_count_ele is None:
            raise TestException("Error: no pass_count element found in the file: " + str(conf.EXECUTION_LOG))
        fail_count_ele = root.find('fail_count')
        TBD_count_ele = root.find('TBD_count')
        if TBD_count_ele is None:
            raise TestException("Error: no TBD_count element found in the file: " + str(conf.EXECUTION_LOG))
        if fail_count_ele is None:
            raise TestException("Error: no fail_count element found in the file: " + str(conf.EXECUTION_LOG))
        pass_list_ele = root.find('pass_list')
        if pass_list_ele is None:
            raise TestException("Error: no pass_list element found in the file: " + str(conf.EXECUTION_LOG))
        fail_list_ele = root.find('fail_list')
        if fail_list_ele is None:
            raise TestException("Error: no fail_list element found in the file: " + str(conf.EXECUTION_LOG))
        TBD_list_ele = root.find('TBD')
        if TBD_list_ele is None:
            raise TestException("Error: no TBD element found in the file: " + str(conf.EXECUTION_LOG))
        
        if dict1.get('name', ''):
            name_ele.text = dict1.get('name', '')
        if dict1.get('start_time', ''):
            begin_time_ele.text = dict1.get('start_time', '')
        if dict1.get('end_time', ''):
            end_time_ele.text = dict1.get('end_time', '')
        if dict1.get('pass_count', ''):
            pass_count_ele.text = str(dict1.get('pass_count', ''))
        if dict1.get('fail_count', ''):
            fail_count_ele.text = str(dict1.get('fail_count', ''))
        if dict1.get('TBD_count', ''):
            TBD_count_ele.text = str(dict1.get('TBD_count', ''))
        if list1:
            pl = pass_list_ele
            for cn in list1:
                ke = ET.SubElement(pl, 'case_name')
                ke.text = cn
        if list2:
            fl = fail_list_ele
            for cn in list2:
                ke = ET.SubElement(fl, 'case_name')
                ke.text = cn
        if TBD_list:
            for cn in TBD_list:
                ke = ET.SubElement(TBD_list_ele, 'case_name')
                ke.text = cn
        tree.write(result_xml)
        
        
def error_report(error_file_path, error_message):
    error_file = open(error_file_path, 'a+')
    error_file.write(error_message + "\n")
    error_file.close()