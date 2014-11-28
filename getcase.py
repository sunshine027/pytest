"""
    It's used to create execution.xml, case_list.xml, and suite.xml by parsing the content from 
    url: http://10.23.31.14:8080/Service1.svc/getalltestcase?ex=ww24&ing=Video, when users use it,
    it should run it like this: python getcase.py -name www24 -ing video, after get all files,
    we'll put execution.xml to ../test_repo/execution/, case_list.xml to ../test_repo/result/www24/,
    suite.xml to ../test_repo/suite_profile/
"""

import shutil
from xml.etree import ElementTree as ET
from xml.parsers.expat import ExpatError
from subprocess import Popen, PIPE
import sys
from optparse import OptionParser
import os

from exception.testexception import TestException
from tools.color import inred

EXECUTION_XML_TARGET_PATH = '../test_repo/execution/'
SUITE_XML_TARGET_PATH = '../test_repo/suite_profile/'
SUITE_TEMPLATE_PATH = '../test_repo/example/suite_template.xml'
EXECUTION_TEMPLATE_PATH = '../test_repo/example/execution_template.xml'
CASELIST_TEMPLATE_PATH = '../test_repo/example/caselist_template.xml'


def create_suite_xml(intro_text, suite_name, case_list):
    suite_xml = '%s.xml' % suite_name
    try:
        shutil.copyfile(SUITE_TEMPLATE_PATH, suite_xml)
    except IOError:
        raise TestException("Error: the file %s doesn't exist " % SUITE_TEMPLATE_PATH)
    try:
        tree = ET.parse(suite_xml)
    except IOError:
        raise TestException("Error: the file: %s can not found" % suite_xml)
    except ExpatError:
        raise TestException("Error: the file: %s is invalid xml file" % suite_xml)
    root = tree.getroot()
    intro_ele = root.find('intro')
    if  intro_ele is not None:
        intro_ele.text = intro_text
    else:
        raise TestException("Error: no intro element found in %s" % suite_xml)
    suite_name_ele = root.find('name')
    if suite_name_ele is not None:
        suite_name_ele.text = suite_name
    else:
        raise TestException("Error: no name element found in %s" % suite_xml)
    list_ele = root.find('list')
    if list_ele is None:
        raise TestException("Error: no list element found in %s" % suite_xml)
    for case in case_list:
        case_ele = ET.SubElement(list_ele, 'Casename')
        case_ele.text = case
    tree.write(suite_xml)


def create_execution_xml(intro_text, execution_name, suite_list):
    execution_xml = '%s.xml' % execution_name
    try:
        shutil.copyfile(EXECUTION_TEMPLATE_PATH, execution_xml)
    except IOError:
        raise TestException("Error: the file %s doesn't exist " % EXECUTION_TEMPLATE_PATH)
    try:
        tree = ET.parse(execution_xml)
    except IOError:
        raise TestException("Error: the file: %s can not found" % execution_xml)
    except ExpatError:
        raise TestException("Error: the file: %s is invalid xml file" % execution_xml)
    root = tree.getroot()
    intro_ele = root.find('intro')
    if intro_ele is not None:
        intro_ele.text = intro_text
    else:
        raise TestException("Error: no intro element found in %s" % execution_xml)
    execution_name_ele = root.find('name')
    if execution_name_ele is not None:
        execution_name_ele.text = execution_name
    else:
        raise TestException("Error: no name element found in %s" % execution_xml)
    list_ele = root.find('list')
    if list_ele is None:
        raise TestException("Error: no list element found in %s" % execution_xml)
    for case in suite_list:
        case_ele = ET.SubElement(list_ele, 'Suitename')
        case_ele.text = case
    tree.write(execution_xml)


def create_caselist_xml(intro_text, execution_name, case_dict):
    #case_dict = {suite_name: [(case_name, id), (case_name, id)], another_suite_name: [(case_name: id)]}
    caselist_xml = 'caselist.xml'
    try:
        shutil.copyfile(CASELIST_TEMPLATE_PATH, caselist_xml)
    except IOError:
        raise TestException("Error: the file %s doesn't exist " % CASELIST_TEMPLATE_PATH)
    try:
        tree = ET.parse(caselist_xml)
    except IOError:
        raise TestException("Error: the file: %s can not found" % caselist_xml)
    except ExpatError:
        raise TestException("Error: the file: %s is invalid xml file" % caselist_xml)
    root = tree.getroot()
    intro_ele = root.find('intro')
    if intro_ele is not None:
        intro_ele.text = intro_text
    else:
        raise TestException("Error: no intro element found in %s" % caselist_xml)
    name_ele = root.find('name')
    if name_ele is not None:
        name_ele.text = execution_name
    else:
        raise TestException("Error: no name element found in %s" % caselist_xml)
    list_ele = root.find('list')
    if list_ele is None:
        raise TestException("Error: no list element found in %s" % caselist_xml)
    for suite_name, case_tuple_list in case_dict.iteritems():
        for case_tuple in case_tuple_list:
            case_ele = ET.SubElement(list_ele, 'Casename')
            case_ele.set('Suite', suite_name)
            case_ele.set('Id', case_tuple[1])
            case_ele.text = case_tuple[0]
    tree.write(caselist_xml)


def move_files(files_dict):
    # files_dict = {source_file: target_path}
    for key, value in files_dict.iteritems():
        if not os.path.isdir(value):
            os.makedirs(value)
        cmd = 'mv -f %s %s' % (key, value)
        p = Popen(cmd, shell=True, stderr=PIPE, stdout=PIPE)
        if p.wait() != 0:
            raise TestException("Error: failed to execute command: %s" % cmd)


def parse_args(url):
    usage = "usage: python %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option('-n', '--name', dest='name', help="build's name", default=False)
    parser.add_option('-i', '--ing', dest='ing', help="project's name", default=False)
    options, args = parser.parse_args()
    if (not options.name) or (not options.ing):
        print inred('Error: you should input -n and -i parameter, the usage is as bellow:')
        parser.print_help()
        sys.exit(2)
    else:
        name = options.name
        ing = options.ing
        return (url + '?ex=' + name.strip() + '&ing=' + ing.strip(), name, ing)


def get_result_from_source_file(file_path, url):
    try:
        tree = ET.parse(file_path)
    except IOError:
        raise TestException("Error: the file: %s can not found" % file_path)
    except ExpatError:
        raise TestException("Error: the file: the content got from the url: %s is invalid xml" % url)
    result_dict = {}
    root = tree.getroot()
    all_tables = []
    for ele in root:
        all_tables += ele.findall('NewDataSet/Table')
    if not all_tables:
        raise TestException('Error: no case at all, maybe you input wrong build name or project name.')
    for table in all_tables:
        execution_type = table.find('ExecutionType')
        if str(execution_type.text).strip().lower() == 'manual':
            continue
        else:
            try:
                suite_name = table.find('TestSuite').text.strip()
                case_name = table.find('TestCase').text.strip()
                eid = table.find('ExecutionID').text.strip()
            except AttributeError:
                continue
            result_dict.setdefault(suite_name, []).append((case_name, eid))
    return result_dict


def main():
    try:
        url = 'http://10.23.31.14:8080/Service1.svc/getalltestcase'
        (full_url, build_name, ing) = parse_args(url)
        cmd = 'curl --noproxy 10.23.31.14 -o alltestcase.xml "%s"' % full_url
        p = Popen(cmd, bufsize=-1, shell=True, stderr=PIPE, stdout=PIPE)
        if p.wait() != 0:
            raise TestException("Error: failed to execute command: %s" % cmd)
        # parse souce file
        result_dict = get_result_from_source_file('./alltestcase.xml', full_url)
        intro = 'Medfield+Android+%s+%s' % (ing, build_name)
        suite_list = result_dict.keys()
        # create exeuction.xml
        create_execution_xml(intro, build_name, suite_list)
        # create many suite.xml
        for suite_name, case_tuple_list in result_dict.iteritems():
            case_list = []
            for case_tuple in case_tuple_list:
                case_list.append(case_tuple[0])
            create_suite_xml('', suite_name, case_list)
        # create case_list.xml
        create_caselist_xml(intro, build_name, result_dict)
        # move files to the right path
        source_file_dict = {}
        source_file_dict['%s.xml' % build_name] = EXECUTION_XML_TARGET_PATH
        for suite_name in suite_list:
            source_file_dict['%s.xml' % suite_name] = SUITE_XML_TARGET_PATH
        source_file_dict['caselist.xml'] = '../test_repo/result/%s/' % build_name
        move_files(source_file_dict)
    except TestException, e:
        print inred(e.value)
if __name__ == '__main__':
    main()
