
from exception.testexception import TestException

def get_element(source, target, error_info):
    ele = source.find(target)
    if ele is None:
        raise TestException(error_info)
    return ele

def get_elements(source, target, error_info):
    ele_list = source.find(target)
    if not ele_list:
        raise TestException(error_info)
    return ele_list

def get_text_by_ele(ele, error_info):
    try:
        ele_text = ele.text
    except AttributeError, e:
        raise TestException(error_info)
    if ele_text is None or ele_text.strip() == '':
        raise TestException(error_info)
    return ele_text

def get_attribute_by_ele(ele, attri_name, error_info):
    attri_value = ele.get(attri_name)
    if attri_value is None:
        raise TestException(error_info)
    return attri_value