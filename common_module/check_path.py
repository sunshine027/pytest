
import sys

from exception.testexception import TestException
from tools.color import inred
try:
    from conf import path
except ImportError, e:
    print inred("ERROR: no path.py found, please run setup.py again.")
    sys.exit(0)
    
def check_item_in_path():
    try:
       path.build_name + " " + path.MediaRecorderResult + " " \
       + path.result_path + " " + path.resultClip_path + " " + path.test_repo
    except AttributeError, e:
         raise TestException("Error: there is something wrong with the item created in path.py. Please run setup.py again.")