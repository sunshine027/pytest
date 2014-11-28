import os
import commands
from subprocess import Popen, PIPE

import conf
from tools.color import inred, ingreen
from exception.testexception import TestException

def upload_result_to_tms(ingredient, build_name):
    
    if ingredient == '':
        ingredient = "Video"
    print "Ingredient: " + ingredient  
        
    if build_name == '':
        try:
            from conf import path
        except Exception, e:
            raise TestException("No path.py generated. please run setup.py again.")
        build_name = path.build_name
    print "Build name: " + build_name
    
    #obtain ip of tms.bj.intel.com
    status, output = commands.getstatusoutput("nslookup tms.bj.intel.com")
    ip = output.split('\n')[-2].replace(' ', '').replace("Address:", '')

    #generate tar.gz file
    status, output = commands.getstatusoutput("cd %s ; tar cvzf %s.tar.gz %s/"%(conf.RESULT_PATH, build_name, build_name))
    if status != 0:
        raise TestException("Error: zip result file failed.")
    
    ingredientId = "174"
    if ingredient == "Camera_Img":
        ingredientId = "176"
    cmd = "cd %s ; curl --noproxy %s -F upload=@%s.tar.gz http://%s/tms/execution/tool/upload.php?id=%s"%(conf.RESULT_PATH, ip, build_name, ip, ingredientId)
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    if p.wait() !=0:
        raise TestException("Error: upload result to http://tms.bj.intel.com/tms/execution/tool/upload.php failed.") 
    else:
        cmd = "curl --noproxy %s 'http://%s/tms/execution/tool/video_input.php?plat=Medfield&os=Android&ing=%s&ex=%s'" %(ip, ip, ingredient, build_name)
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        if p.wait() !=0:
            raise TestException("Error: upload result to http://tms.bj.intel.com/tms/execution/tool/upload.php failed.") 
                   
    status, output = commands.getstatusoutput("rm -rf %s%s.tar.gz"%(conf.RESULT_PATH, build_name))  
    print ingreen("###########################--UPLOAD FINISHED--###########################")  

    
