"""
    download execution case from TMS.
    1. clear old execution directory defined by config.EXECUTION_PATH
    2. download test_repo.tar.gz, only including device profile and some templates
    3. download config.tar.gz, including case profile, suite profile, and execution profile.
    4. check if config.tar.gz is right and run tar xzf config.tar.gz, and put all suite profiles 
       to suite directory, and put execution profiles to execution directory
    5. delete temporary config directory 
"""

from subprocess import Popen, PIPE
import os
import sys
import commands
from xml.etree import ElementTree as ET

from tools.color import inred, ingreen
from chDev import main
import conf

def download(ingredient, buildname):
    if ingredient == '':
        ingredient = raw_input("Enter Ingredient name:");
        ingredient = ingredient.replace(" ","%20");
        
    if buildname == '':
        buildname = raw_input("Enter Test Execution name:");
        buildname = buildname.replace(" ","%20");
        
    #create buildname in ./conf/
    buildname_file = open('conf/buildname','w')
    buildname_file.write(buildname)
    buildname_file.close()
    
    #delete origin test_repo
    os.system("cd .. ; rm -rf test_repo")
    
    #download test_repo.tar.gz
    url = "http://tms.bj.intel.com/tms/execution/tool/download.php"
    command = "curl --noproxy tms.bj.intel.com -o ../test_repo.tar.gz '%s'" %(url)
    status, output = commands.getstatusoutput(command)
    if not status == 0:
        print inred("###########################--Download test_repo.tar.gz Error--###########################")
    else:
        status, output = commands.getstatusoutput("cd .. ; tar zxvf test_repo.tar.gz")
        if not status == 0:
            print inred("Error: fail to download test_repo from TMS.")
        else:
            os.system("cd .. ; rm -rf test_repo.tar.gz")
            
            #download config.tar.gz
            url = "http://tms.bj.intel.com/tms/execution/tool/video_profile.php?plat=Medfield&os=Android&ing=%s&ex=%s"%(ingredient, buildname)
            command = "curl --noproxy tms.bj.intel.com -o %sconfig.tar.gz '%s'" %(conf.TEST_REPO, url)
            status, output = commands.getstatusoutput(command)
            if not status == 0:
                print inred("###########################--Download Case Profile Error--###########################")
            else:
                status, output = commands.getstatusoutput("cd " + conf.TEST_REPO + " ; tar zxvf config.tar.gz")
                if not status == 0:
                    print inred("Error: fail to download execution from TMS, maybe the ingredient name or execution name is invalid. Or your host need to install curl.")
                else:
                    os.system("cd " + conf.TEST_REPO + " ; rm -rf config.tar.gz")
                    os.system("mv " + conf.TEST_REPO + "config/" + buildname + ".xml " + conf.TEST_REPO)
                    os.system("mv " + conf.TEST_REPO + "config/case_profile " + conf.TEST_REPO)
                    os.system("cd " + conf.TEST_REPO + " ; mv config suite_profile")
                    print ingreen("###########################Download Successful--###########################") 
                    # set device number
                    try:
                        main()
                    except Exception, e:
                        print e
           