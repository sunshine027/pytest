import os
import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError

import conf

def get_build_name():
    try:
        files = os.listdir(conf.EXECUTION_PATH)
    except OSError:
        raise TestException("Error: %s doesn't exist." %conf.EXECUTION_PATH)
    build_name = ''
    i = 0
    for f in files:
        if f.endswith('.xml'):
            build_name = f[:-4]
            i = i + 1
    if i != 1:
        raise TestException("Error: there should be one execution xml file in %s" %conf.EXECUTION_PATH)
    if build_name.strip():
        return build_name.strip()
    else:
        raise TestException("Error: no execution xml file found in %s" %conf.EXECUTION_PATH)
    
def get_work_directory():
    execution_file = get_build_name() + '.xml'
    if execution_file:
        try:
            root = ET.parse(conf.EXECUTION_PATH + execution_file).getroot()
        except IOError, e:
            raise TestException("Error: the file: " + conf.EXECUTION_PATH + execution_file + " can not found")
        except ExpatError, e:
            raise TestException("Error: the file: " + conf.EXECUTION_PATH + execution_file + " is invalid!")
        try:
            workdirectory_ele = root.find('Setup').find('DUTWorkDirectory')
        except AttributeError, e:
            raise TestException("Error: no Setup element found in " + conf.EXECUTION_PATH + execution_file)
        try:
            work_directory = workdirectory_ele.text
        except AttributeError, e:
            raise TestException("Error: no DUTWorkDirectory element found in " + conf.EXECUTION_PATH + execution_file)
        if work_directory is None or work_directory.strip() == '':
            raise TestException("Error: text of DUTWorkDirectory element can't be empty in " + conf.EXECUTION_PATH + execution_file)
        return work_directory.strip()

def get_result_path():
    return get_work_directory() + '/Result/' + get_build_name() + '/'

def get_clip_path():
    execution_file = get_build_name() + '.xml'
    if execution_file:
        try:
            root = ET.parse(conf.EXECUTION_PATH + execution_file).getroot()
        except IOError, e:
            raise TestException("Error: the file: " + conf.EXECUTION_PATH + execution_file + " can not found")
        except ExpatError, e:
            raise TestException("Error: the file: " + conf.EXECUTION_PATH + execution_file + " is invalid!")
        try:
            clipdirectory_ele = root.find('Setup').find('ClipsDirectory')
        except AttributeError, e:
            raise TestException("Error: no Setup element found in " + conf.EXECUTION_PATH + execution_file)
        try:
            clip_directory = clipdirectory_ele.text
        except AttributeError, e:
            raise TestException("Error: no ClipsDirectory element found in " + conf.EXECUTION_PATH + execution_file)
        if clip_directory is None or clip_directory.strip() == '':
            raise TestException("Error: text of ClipsDirectory element can't be empty in " + conf.EXECUTION_PATH + execution_file)
        return clip_directory.strip()
        