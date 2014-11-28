import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError

def create_path_file(execution_profile):
    # generate path.py
    try:
        root = ET.parse(execution_profile).getroot()
    except IOError, e:
        raise TestException("Error: the file: " + str(self.args['execution']) + " can not found")
    except ExpatError, e:
        raise TestException("Error: the file: " + str(self.args['execution']) + " is invalid!") 
    try:
        buildname = root.find('name').text
    except AttributeError, e:
        raise TestException("Error: no name element found in " + str(self.args['execution']))
    if buildname is None or buildname.strip() == '':
        raise TestException("Error: the text of name element can't be empty in " + str(self.args['execution']))
    
    setup_ele = root.find('Setup')
    if setup_ele is None:
        raise TestException("Error: no Setup element found in " + str(self.args['execution']))
                   
    pytest_file = open('conf/path.py', 'w')
    pytest_file.write("#init\n")
    pytest_file.write("build_name = \'" + buildname + "'\n\n")
    pytest_file.write("# For DUT\n")
#    pytest_file.write("WorkDirectory = '" + workdir + "'\n")
#    pytest_file.write("Result = WorkDirectory + 'Result/' + build_name + '/'\n")
    pytest_file.write("MediaRecorderResult = '/dev/' + build_name + '/'\n")
#    pytest_file.write("clipPath = '" + clipDir + "'\n")
    pytest_file.write("test_repo = '../test_repo/'\n")
    pytest_file.write("result_path = test_repo + 'result/log/' + build_name \n")
    pytest_file.write("resultClip_path = test_repo + 'result/clip/' + build_name \n")
    pytest_file.write("mailContentFile_path = test_repo + 'mailContent.xlsx' \n")
#    pytest_file.write("email_profile_path = 'conf/mail_list.xml' \n")
    pytest_file.close()