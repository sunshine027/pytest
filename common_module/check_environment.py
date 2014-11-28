
import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError

from exception.testexception import TestException
from conf import path


def check_build_name(test_execution_profile):
    try:
        tree = ET.parse(test_execution_profile)
    except IOError, e:
        raise TestException("Error: the file: " + str(test_execution_profile) + " can not be found")
    except ExpatError, e:
        raise TestException("Error: the file: " + str(test_execution_profile) + " is invalid, please check if all tags are matched or missed some signs.")
    else:
        root = tree.getroot()
        try:
            suite_name = root.find('name').text
        except AttributeError, e:
            raise TestException("Error: no name element found in the file: " + str(test_execution_profile))
        if suite_name is None or suite_name.strip() == '':
            raise TestException("Error: the text of name element can't be empty in the file: " + str(test_execution_profile))
        if path.build_name.find('/') != -1:
            path.build_name = path.build_name[:-1]
        if suite_name.strip() != path.build_name:
            raise TestException("Error: the text of name element in execution profile:" + str(test_execution_profile) +" is different with path.build_name, please run setup.py first.")
