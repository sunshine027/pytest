import os
import commands

import conf
from tools.color import inred, ingreen, inpurple
from exception.testexception import TestException

def upload_clip_to_mediaserver(buildname):
    
    try:
        from conf import path
    except Exception, e:
        raise TestException("No path.py generated. please run setup.py again.")
    
    print inpurple("Uploading result clips to media server......")
    
    '''
    status, output = commands.getstatusoutput("resource/uploadClipPrepare.sh")
    if status != 0:
        print inred("Error: upload clips failed.")
        return ''
    '''
    
    resultClipDir = conf.RESULTCLIP_PATH_WITHOUTBUILDNAME
    
    if buildname == '':
        status, output = commands.getstatusoutput("ls -l " + resultClipDir + " | grep ^d")
        dirList = output.split('\n')
        resultDirList = []
        for eachDir in dirList:
            resultDirList.append(eachDir.split(' ')[-1])            
        for executionName in resultDirList:
            status, output = commands.getstatusoutput("resource/uploadClip.sh " + resultClipDir + executionName)
            if status != 0:
                print inred("Error: upload clips failed.")
                return ''
        print ingreen("################### Upload finished ###################")
    else:
        status, output = commands.getstatusoutput("resource/uploadClip.sh " + resultClipDir + buildname)
        if status != 0:
            print inred("Error: upload clips failed.")
            return ''
        print ingreen("################### Upload finished ###################")
        