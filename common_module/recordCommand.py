import os
from xml.etree import ElementTree as ET
from tools.color import inred

recordCommandFilePath = "conf/recordCommand"

def writeCommand(cmd):
    recordFile = open(recordCommandFilePath,'w')
    for each_param in cmd:
        recordFile.write(each_param + " ")
    recordFile.close()
    
def readCommand_type():
    try:
        recordFile = open(recordCommandFilePath,'r')
    except Exception, e:
        print inred("Can not read command file: " + recordCommandFilePath)
        return -1
    cmd = recordFile.read()
    recordFile.close()
    paramList = cmd.split(' ')
    for eachParam in paramList:
        if eachParam == "-c":
            return "c"
        elif eachParam == "-s":
            return "s"
        elif eachParam == "-e":
            return "e"
    return -1

def readCommand_profile(type):
    if type == "c" or type == "s" or type == "e":        
        try:
            recordFile = open(recordCommandFilePath,'r')
        except Exception, e:
            print inred("Can not read command file: " + recordCommandFilePath)
            return -1
        cmd = recordFile.read()
        recordFile.close()
        paramList = cmd.split(' ')
        try:
            return paramList[paramList.index("-" + type)+1]
        except Exception, e:
            return -1
    else:
        return -1
     