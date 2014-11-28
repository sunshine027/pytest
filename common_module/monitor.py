#!/usr/bin/env python
from __future__ import division
import sys
import os
import datetime
import time
import shutil
import xml.etree.ElementTree as ET
import csv
from decimal import Decimal, InvalidOperation

from tools.client import get_connect_way
from common_module import ISO_DATETIME_FORMAT, DEVICE_DATA_DIR, DEVICE_COMMAND_PREFIX
from exception.testexception import TestException
from tools.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite
from tools.matrix_tool import get_interrupt_for_matrix, get_ncres_for_matrix, get_pstate_for_matrix_by_name, get_cstate_for_matrix
from tools.assertor import assertor, get_criteria_dict, CONCATENATION_STR

MATRIX_REFER_DICT = {'c_state': 'cstate', 'p_state': 'pstate', 'ncres_ved': 'ncres', 'ncres_ved': 'ncres', 'interrupt': 'intr'}


def memory_monitor_process(caseFolderName, monitor_elementtree, device_dict, monitor_exception_queue, monitor_result_queue, case_result_path):  
    try:
        prefix, accessor = get_connect_way(device_dict) 
        cli = accessor(device_dict)
        if not os.path.isdir(case_result_path): 
            os.makedirs(case_result_path)
        mi_name = monitor_elementtree.get('name')
        mi_step = monitor_elementtree.get('step') 
        sch = monitor_elementtree.find('Schedule')
        if sch is None:
            raise TestException("Error: no Schedule element found in Monitor element with name memory")  
        try:
            interval = float(sch.find('interval').text)
        except AttributeError, e:
            raise TestException("Error: no interval element found in Monitor element with name memory")
        except (TypeError, ValueError):
            raise TestException("Error: the text of interval element should be a number in Monitor element with name memory")
        try:
            count = int(sch.find('count').text)
        except AttributeError, e:
            raise TestException("Error: no count element found in Monitor element with name memory")
        except (TypeError, ValueError):
            raise TestException("Error: the text of count element should be a number in Monitor element with name memory")
        par = monitor_elementtree.find('Parameter')
        if par is None:
            raise TestException("Error: no Parameter element found in Monitor element with name memory")
        output_eles = par.findall('output')
        if not output_eles:
            raise TestException("Error: <output object='log'></output> should exist in Monitor element with name memory")
        monitor_log = ''
        #check if <output object="log"></output> exists
        ouput_with_object_ele = filter(lambda output_ele: output_ele.get('object') is not None and  output_ele.get('object').strip() == 'log', output_eles)
        if not ouput_with_object_ele:
            raise TestException("Error: <output object='log'></output> should exist in Monitor element with name memory")
        else:
            output_eles.remove(ouput_with_object_ele[0])
            output_text = ouput_with_object_ele[0].text
            if output_text is not None and output_text.strip() != '':
                monitor_log = case_result_path + '/' + output_text + '.csv'
        if monitor_log == '':
            monitor_log = '%(case_result_path)s/step_%(mi_step)s_%(mi_name)s.csv' % locals()
        csvFile = open(monitor_log, 'wb')
        writer = csv.writer(csvFile)
        title_list = ['StartTime']
        # memory monitor will run count times with interval
        for count_num in range(count): 
            result_list = []
            turn_start = datetime.datetime.now().strftime(ISO_DATETIME_FORMAT)
            result_list.append(turn_start) 
            for each_par in output_eles:
                if each_par.text is None or each_par.text.strip() == '':
                    raise TestException("Error: the text of %s element can't be empty in Monitor element with name memory" % each_par.tag)
                title_list.append(each_par.text)
                cmd = "cat /proc/meminfo | grep '^%s'" % each_par.text
                result = cli.execute(cmd)
                try:
                    meminfo = result[0].split(':')[1].lstrip().replace('\r', '').replace('\n', '')
                except IndexError:
                    raise TestException("Error: failed executing '" + cmd + "', please check your case profile.")
                result_list.append(meminfo)
            # write title for the first, for some column name is unknown first
            if count_num == 0:
                title_list.append('EndTime')
                writer.writerow(title_list)
            turn_end = datetime.datetime.now().strftime(ISO_DATETIME_FORMAT)
            result_list.append(turn_end)
            writer.writerow(result_list)
            time.sleep(interval)
        csvFile.close() 
    except TestException, e:
        monitor_exception_queue.put(e.value)
        
def kernel_log_monitor_process(caseFolderName, monitor_elementtree, device_dict, monitor_exception_queue, monitor_result_queue, case_result_path):  
    try:
        prefix, accessor = get_connect_way(device_dict)
        cli = accessor(device_dict)
        par_ele = monitor_elementtree.find('Parameter')
        step_id = monitor_elementtree.get('step') 
        if par_ele is None:
            raise TestException("Error: no Parameter element found in Monitor element with name kernel_log")
        try:
            level = par_ele.find('level').text
        except AttributeError, e:
            raise TestException("Error: no level element found in Monitor element with name kernel_log")
        if level is None or level.strip() == '':
            raise TestException("Error: text of level element can't be empty in Monitor element with name kernel_log")
        try:
            level = int(level)
        except ValueError, e:
            raise TestException("Error: the text of level element should be a number in Monitor element with name kernel_log")
        cli.execute(' echo %s > /proc/sys/kernel/printk' % level)
        kernel_log = ''
        output_eles = par_ele.findall('output')
        if not output_eles:
            raise TestException("Error: <output object='log'></output> should exist in Monitor element with name kernel_log")
        #check if <output object="log"></output> exists
        ouput_with_object_ele = filter(lambda output_ele: output_ele.get('object') is not None and  output_ele.get('object').strip() == 'log', output_eles)
        if not ouput_with_object_ele:
            raise TestException("Error: <output object='log'></output> should exist in Monitor element with name kernel_log")
        else:
            output_eles.remove(ouput_with_object_ele[0])
            output_text = ouput_with_object_ele[0].text
            if output_text is not None and output_text.strip() != '':
                kernel_log = output_text
        if kernel_log == '':
            kernel_log = 'step_%s_kernel_log' % step_id
        result_file = DEVICE_DATA_DIR + str(kernel_log)
        cli.execute('cat /proc/kmsg > ' + result_file)
    except TestException, e:
        monitor_exception_queue.put(e.value)
            
def logcat_monitor_process(caseFolderName, monitor_elementtree, device_dict, monitor_exception_queue, monitor_result_queue, case_result_path):  
    print 'Start Logcat Monitor: '       
    try:
        prefix, accessor = get_connect_way(device_dict)
        cli = accessor(device_dict)
        par_ele = monitor_elementtree.find('Parameter')
        step_id = monitor_elementtree.get('step').strip()
        if par_ele is None:
            raise TestException("Error: no Parameter element found in Monitor element with name logcat")
        output_eles = par_ele.findall('output')
        if len(output_eles) == 0:
            raise TestException("Error: <output object='log'></output> should exist in Monitor element with name logcat")
        logcat_log = ''
        #check if <output object="log"></output> exists
        ouput_with_object_ele = filter(lambda output_ele: output_ele.get('object') is not None and  output_ele.get('object').strip() == 'log', output_eles)
        if not ouput_with_object_ele:
            raise TestException("Error: <output object='log'></output> should exist in Monitor element with name logcat")
        else:
            output_eles.remove(ouput_with_object_ele[0])
            output_text = ouput_with_object_ele[0].text
            if output_text is not None and output_text.strip() != '':
                logcat_log = output_text
        if logcat_log == '':
            logcat_log = 'step_%s_logcat' % step_id
        result_file = DEVICE_DATA_DIR + str(logcat_log)
        cli.execute("logcat -c")
        cli.execute('logcat -f ' + result_file) 
    except TestException, e:
        monitor_exception_queue.put(e.value)

def matrix_monitor_process(caseFolderName, monitor_elementtree, device_dict, monitor_exception_queue, monitor_result_queue, case_result_path):
    print 'Start Matrix Monitor: '       
    try:
        step_id = monitor_elementtree.get('step').strip()
        monitor_name = monitor_elementtree.get('name').strip()
        schedule_ele = monitor_elementtree.find('Schedule')
        if schedule_ele is None:
            raise TestException("Error: no Schedule element found in Monitor element with name matrix")
        duration_ele = schedule_ele.find('duration')
        if duration_ele is None:
            raise TestException("Error: no duration element found in Monitor element with name matrix")
        duration_text = duration_ele.text
        if duration_text is None or duration_text.strip() == '':
            raise TestException("Error: text of duration element can't be empty in Monitor element with name matrix")
        try:
            float_duration_text = float(duration_text)
        except ValueError, e:
            raise TestException("Error: text of duration element should be number value in Monitor element with name matrix")
        par_ele = monitor_elementtree.find('Parameter')
        if par_ele is None:
            raise TestException("Error: no Parameter element found in Monitor element with name matrix")
        prefix, accessor = get_connect_way(device_dict)
        cli = accessor(device_dict)
        output_eles = par_ele.findall('output')
        if not output_eles:
            raise TestException("Error: <output object='log'></output> should exist in Monitor element with name logcat")
        matrix_log = ''
        matrix_file = ''
        #check if <output object="log"></output> exists
        ouput_with_object_ele = filter(lambda output_ele: output_ele.get('object') is not None and  output_ele.get('object').strip() == 'log', output_eles)
        if not ouput_with_object_ele:
            raise TestException("Error: <output object='log'></output> should exist in Monitor element with name logcat")
        else:
            output_eles.remove(ouput_with_object_ele[0])
            output_text = ouput_with_object_ele[0].text
            if output_text is not None and output_text.strip() != '':
                matrix_file = output_text.strip()
        if matrix_file == '':
            matrix_file = 'step_' + str(step_id) + '_matrix'
        matrix_log = DEVICE_DATA_DIR + matrix_file
#        cmd = "test -f " + prefix + "matrix.ko && echo 'File exists' || echo 'File not found'"
        cli.execute_on_host(' remount')
        cli.execute('chmod a+x ' + prefix + 'matrix')
#        cli.execute('chmod a+x ' + prefix + 'ver_matrix')
#        cli.execute(prefix + 'ver_matrix ' + prefix + 'matrix.ko')
#        cli.execute('insmod ' + prefix + 'matrix.ko')
#        stdout, stderr = cli.execute(cmd)
#        if stdout.strip() == 'File not found':
#            cli.execute('chmod a+x ' + prefix + 'matrix')
#            cli.execute('chmod a+x ' + prefix + 'ver_matrix')
#            cli.execute('ver_matrix ' + prefix + 'matrix.ko')
#            stdout, stderr = cli.execute("cd " + prefix + ' ; ./matrix -genanddrv')
#             stdout, stderr = cli.execute(cmd)
#            if stdout.strip() == 'File not found':
#                raise TestException("Error: " + prefix + "matrix -genanddrv doesn't run successfully" )
#        cli.execute('insmod ' + prefix + 'matrix.ko')
#        cli.execute('chmod a+x ' + prefix + 'matrix')
        run_ncres_flag = False
        # delete output whose text is empty or None
        output_eles = filter(lambda output_ele: output_ele.text is not None and output_ele.text.strip(), output_eles)
        # if not matrix option was executed, but criteria option exist, it's wrong
        check_output_list = [output.text.strip() for output in output_eles]
        # temp_set is used to delete all duplicate matrix args, like both ncres_vec and ncres_ved corresponding ncres
        temp_set = set()
        map(lambda arg: temp_set.add(MATRIX_REFER_DICT.get(arg.text.strip())), output_eles)
        matrix_arg_list = list(temp_set)
        args = ''
        for matrix_arg in matrix_arg_list:
            # in case some tag are not included in MATRIX_REFER_DICT, like ved_mbw            
            if matrix_arg:
                args = args + ' -f ' + matrix_arg
        cmd = '%smatrix %s -t %s -o %s ' % (prefix, args, float_duration_text, matrix_log)
        cli.execute(cmd)
        result_path = case_result_path + '/'
        if not os.path.isdir(result_path): 
            os.makedirs(result_path)
        test_cmd = "test -f %s.csv && echo 'File exists' || echo 'File not found'" % matrix_log
        stdout, stderr = cli.execute(test_cmd)
        if stdout.strip() == 'File not found':
            raise TestException("Error: there is something wrong when executing command: " + cmd)
        else:
            cli.execute_on_host(' pull %s.csv %s'  % (matrix_log, result_path))
        cli.execute(' rm -rf %s.csv' % matrix_log)
        criteria_ele = monitor_elementtree.find('Criteria')
        if criteria_ele is None:
            raise TestException("Error: no Criteria element found in Monitor element with name matrix")
        matrix_output_data = {} # it's used to record the matrix result, and its item is like c_state: 0.0013%
        monitor_child_info_list = [] # it's used to record the matrix child element info
        
        matrix_output_data, monitor_child_info_list = get_matrix_data(criteria_ele, matrix_output_data, result_path + matrix_file + '.csv', check_output_list, duration_text, monitor_child_info_list)
        matrix_attr_data_dict={'step': step_id, 'name': monitor_name}
        get_push_result_for_monitor(criteria_ele, matrix_output_data, monitor_child_info_list, device_dict, caseFolderName, matrix_attr_data_dict, monitor_result_queue)
    except TestException, e:
        monitor_exception_queue.put(e.value)
        
def get_matrix_data(criteria_ele, data_dict, log_file, check_output_list, duration_text, monitor_child_info_list):
    criteria_ele_list = list(criteria_ele)
    for ele in criteria_ele_list:
        if cmp(ele.text.lower(), 'off'):
            if not (ele.tag in check_output_list):
                raise TestException("Error: no " + ele.tag + " in Parameter element in Monitor element with name matrix")
            name = ele.get('name')
            if name is None or name.strip() == '':
                raise TestException("Error: " + ele.tag + " element should have name attribute if its text is not Off in Monitor element with name matrix")
            if ele.text is None or ele.text.strip() == '':
                raise TestException("Error: " + ele.tag + " element text should be Off or number value in Monitor element with name matrix")
            if ele.tag.strip() == 'interrupt' and len(name.split('_')) != 2:
                raise TestException("Error: the value of name attribute of " + ele.tag + " must be in this format: irq_value in Monitor element with name matrix")
            tag_value = get_value_in_csv_file(ele.tag, name, log_file, duration_text)
            monitor_child_info_list.append((ele.tag, [tag_value, {'name': name}, []]))
            data_dict[ele.tag.strip() + CONCATENATION_STR + name.strip() ]=tag_value
    return (data_dict, monitor_child_info_list)

                                      
def get_value_in_csv_file(tag, name, log_file, duration_text):
    tag_value = ''
    if tag == 'c_state':
        tag_value = get_cstate_for_matrix(name, log_file)
    elif tag == 'p_state':
        tag_value = get_pstate_for_matrix_by_name(name, log_file)
    elif tag == 'ncres_vec':
        new_tag = 'Video Encode'
        tag_value = get_ncres_for_matrix(new_tag, log_file, ncres_name=name)
    elif tag == 'ncres_ved':
        new_tag = 'Video Decode'
        tag_value = get_ncres_for_matrix(new_tag, log_file, ncres_name=name)
    elif tag == 'interrupt':
        irq_value = name.split('_')[1].strip()
        tag_value = get_interrupt_for_matrix(irq_value, log_file, duration_text=duration_text)
    if tag_value != -1:
        return tag_value
    else:
        return 'empty_value'
    
def get_push_result_for_monitor(criteria_ele, monitor_data, monitor_child_info_list, device_dict, caseFolderName, monitor_attr_data_dict, monitor_result_queue):
    """
        parameter instruction:
        criteria_ele: the comparing standard, it's the Criteria Element in Monitor Element in case profile
        monitor_data: the actual data got by monitor in Criteria Element, like {'c_state': 0.1%}, the key is the tag's name, and the value if we got for this tag.
        monitor_child_info_list: all the child element included by Monitor Element, a tuple presents an element, its format is [('tag_name', [tag_text, attr_dict, child_element_list])], 
        and child_element_list is a recursion, its format is also [('tag_name', [tag_text, attr_dict, child_element_dict])], like [('c_state', [0.1, {'name': C[0]}, [])]
        monitor_attr_data_dict: the attribute data of Monitor, like {'step_id':1, 'name': 'matrix'}
    """
    result=[]
    criteria_dict, addtional_dict, operator_dict = get_criteria_dict(criteria_ele)
    monitor_result = assertor(criteria_dict, monitor_data, operator_dict, addtional_dict, device_dict, caseFolderName)
    monitor_child_info_list.append(('result', [monitor_result, {}, []]))
    result.append(('Monitor', ['', monitor_attr_data_dict, monitor_child_info_list]))
    monitor_result_queue.put(result)