"""
    this module includes some common file or directory method.
"""
import os
from subprocess import Popen, PIPE
from xml.parsers.expat import ExpatError
from xml.etree import ElementTree as ET

from exception.testexception import TestException
import conf

def clear_old_directory(path):
    '''
        remove all files in some directory defined by path.
        the argument path is a directory. 
    '''
    if os.path.isdir(path):
        try:
            files = os.listdir(path)
        except OSError:
            raise TestException("Error: %s doesn't exist." %path)
        for f in files:
            cmd = 'rm -rf %s%s' % (path, f)
            p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
            if p.wait() != 0:
                raise TestException("Error: failed remove %s in %s") %(f, path)
            
def clear_unuseful_file(path):
    try:
        os.remove(path)
    except:
        pass
    
