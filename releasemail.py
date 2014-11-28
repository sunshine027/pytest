import os
import sys
import commands
from optparse import OptionParser
from xml.etree import ElementTree as ET
from tools.color import inred
from common_module.email import checkMailList
import conf  
import path

email_profile = conf.email_profile_path


def sendMail(srcNameList,wikisrc):
    if maillist == []:
        pass
    else:
        #start writing report
        mailContentFile = open("tempMailContent", 'w')
        separateLine = "\n******************************************************************\n"
        mailContentFile.write(separateLine)
        
        mailContentFile.write("Build:\n")
        mailContentFile.write("link:   " + wikisrc + "\n")
        mailContentFile.write(separateLine)        

    
        mailContentFile.write("\n\n")        

        mailContentFile.write(separateLine)        
        mailContentFile.write("Integrated new Patch list\n")
        mailContentFile.write("link:   " + wikisrc + "/diff/HEAD please see Patches\n")
        mailContentFile.write(separateLine) 

        mailContentFile.write("\n\n")      

        mailContentFile.write(separateLine) 
        mailContentFile.write("Bug info and Bug list related new patches\n")
        mailContentFile.write("link:   " + wikisrc + "/diff/HEAD/  please see Bugs\n")
        mailContentFile.write(separateLine)

        mailContentFile.close() 
                
        #send mail
        dstNameString = ""
        for eachName in srcNameList:
            dstNameString = dstNameString + ',' + eachName
        dstNameString = dstNameString[1:]

        if os.path.exists("tempMailContent"):
            #cmd = "mail -s RapidRunner_TestReport_" + path.build_name + " " + dstNameString + " < tempMailContent"
            cmd = "mail -s 'Video pre-integration " + path.build_name + " build release' " + dstNameString + " < tempMailContent"
            #cmd = "mail -s Video_pre-integration_build_release " + buildname + " " + dstNameString + " < tempMailContent"
            os.system(cmd)
            os.system("rm -rf tempMailContent")
        else:
            print inred("No mail content file found, will not send mail!")
            

if __name__ == "__main__":
    
    usage = "usage: python %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option('--mail', dest='mail', help="send mail manually according to current execution result.", default=None)
    options, args = parser.parse_args(sys.argv)

    if options.mail is not None:
        print options.mail
        maillist = checkMailList(options.mail)
    else:
        print inred("Could not send mail because of the lack of --mail parameter.")
        exit(-1)
    
    sendMail(maillist,args [1])
