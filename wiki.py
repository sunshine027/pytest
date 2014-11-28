#!/usr/bin/env python

import os
import sys
import getopt
import commands
from xml.parsers.expat import ExpatError
import xml.etree.ElementTree as ET
from optparse import OptionParser

from exception.testexception import TestException
from tools import XMLParser
from common_module import BTPprint
from tools.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite
from tools.shellExecutor import executeShell
from tools.client import sshAccessor as accessor
import conf
import paramiko      
    

def wiki_xml(cfg):

    #get items in execution.xml
    try:
        root_build = ET.parse(cfg).getroot()
    except IOError, e:
        raise TestException("Error: the file: " + str(cfg) + " can not found")
    except ExpatError, e:
        raise TestException("Error: the file: " + str(cfg) + " is invalid!")
       
    buildname = root_build.find('name').text

    head_1 = """
<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.4/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.4/ http://www.mediawiki.org/xml/export-0.4.xsd" version="0.4" xml:lang="en">
  <siteinfo>
    <sitename>ValidationWiki</sitename>
    <base>http://172.16.120.166/wiki/index.php/Beijing_Verification_Wiki</base>
    <generator>MediaWiki 1.16.2</generator>
    <case>first-letter</case>
    <namespaces>
      <namespace key="-2" case="first-letter">Media</namespace>
      <namespace key="-1" case="first-letter">Special</namespace>
      <namespace key="0" case="first-letter" />
      <namespace key="1" case="first-letter">Talk</namespace>
      <namespace key="2" case="first-letter">User</namespace>
      <namespace key="3" case="first-letter">User talk</namespace>
      <namespace key="4" case="first-letter">ValidationWiki</namespace>
      <namespace key="5" case="first-letter">ValidationWiki talk</namespace>
      <namespace key="6" case="first-letter">File</namespace>
      <namespace key="7" case="first-letter">File talk</namespace>
      <namespace key="8" case="first-letter">MediaWiki</namespace>
      <namespace key="9" case="first-letter">MediaWiki talk</namespace>
      <namespace key="10" case="first-letter">Template</namespace>
      <namespace key="11" case="first-letter">Template talk</namespace>
      <namespace key="12" case="first-letter">Help</namespace>
      <namespace key="13" case="first-letter">Help talk</namespace>
      <namespace key="14" case="first-letter">Category</namespace>
      <namespace key="15" case="first-letter">Category talk</namespace>
    </namespaces>
  </siteinfo>
  <page>
"""
    title = " <title>" + buildname + "</title>"
    head_2 = """ 
<revision>
      <text xml:space="preserve">

== '''BAT Result''' ==
{|
    |}

== '''FAIL''' ==
{|  class=&quot;wikitable&quot;
|-
! Suite
! CaseName
! Result
"""
    outfile = open('wiki', 'w+')
    outfile.writelines(head_1)
    outfile.writelines(title)
    outfile.writelines(head_2)
    all_suites = root_build.find('list')
    
    for testsuite in all_suites:
        if testsuite.text is None or testsuite.text.strip() == '':
            continue
        suite_file = conf.SUITE_PATH + testsuite.text.strip() + '.xml'
        root_suite = ET.parse(suite_file).getroot()
        all_cases = root_suite.find('list')
        for case in all_cases:
            if case.text is None or case.text.strip() == '':
                continue
            case_file = conf.RESULT_PATH + buildname + "/" + case.text.strip() + "/" + case.text.strip() + ".xml"
            if os.path.isfile(case_file):
                root_case = ET.parse(case_file).getroot()
                result = root_case.find('result').text
                if result is None:
                    continue  
                if result == "fail":
                    item = "|-align='left'\n" + "|" + testsuite.text.strip() + "\n" + "|" + case.text.strip() + "\n" + "|[http://172.16.120.166/media_resource/TestResult/log/" + buildname +"/"+ case.text.strip()+" " + result + "] \n" 
                    outfile.writelines(item)
    failend = """
    |}
"""
    outfile.writelines(failend)

    head_3 = """
== '''PASS''' ==
{|  class=&quot;wikitable&quot;
|-
! Suite
! CaseName
! Result
"""
    outfile.writelines(head_3)
    for testsuite in all_suites:
        if testsuite.text is None or testsuite.text.strip() == '':
            continue
        suite_file = conf.SUITE_PATH + testsuite.text.strip() + '.xml'
        root_suite = ET.parse(suite_file).getroot()
        all_cases = root_suite.find('list')
        for case in all_cases:
            if case.text is None or case.text.strip() == '':
                continue
            case_file = conf.RESULT_PATH + buildname + "/" + case.text.strip() + "/" + case.text.strip() + ".xml"
            if os.path.isfile(case_file):
                root_case = ET.parse(case_file).getroot()
                result = root_case.find('result').text
                if result is None:
                    continue   
                if result == "pass" or result == "TBD":
                    item = "|-align='left'\n" + "|" + testsuite.text.strip() + "\n" + "|" + case.text.strip() + "\n" + "|[http://172.16.120.166/media_resource/TestResult/log/" + buildname +"/"+ case.text.strip()+" " + result + "] \n" 
                    outfile.writelines(item)
    tail = """
    |}</text>
    </revision>
  </page>
</mediawiki>
"""
    outfile.writelines(tail)
    outfile.close()

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('172.16.120.166',username='shihui',password='shihui')
#    dict_server = {'IP':'172.16.120.166','Username':'shihui','Password':'shihui'        }
#    cli = accessor(dict_server)
    sftp = ssh.open_sftp()
    sftp.put('wiki','/home/shihui/wiki')
#    cli.upload('wiki','/home/shihui/')
    cmd1 = "php /var/www/html/wiki/maintenance/importDump.php /home/shihui/wiki"
    cmd2 = "rm -f /home/shihui/wiki"
    stdin, stdout, stderr = ssh.exec_command(cmd1)
    print stdout.readlines()    
    stdin, stdout, stderr = ssh.exec_command(cmd2)
    print stdout.readlines()
    ssh.close()
    os.system('rm -f wiki')    
    log_source = "../test_repo/result/log/" + buildname
    clip_source = "../test_repo/result/clip/" + buildname
    cmd3 = 'scp -r ' + log_source + ' shihui@172.16.120.166:/var/www/html/media_resource/TestResult/log/'
#    cmd4 = 'scp -r ' + clip_source + ' shihui@172.16.120.166:/var/www/html/media_resource/TestResult/clip/'
    os.system(cmd3)
#    os.system(cmd4)
#    cli.execute(cmd1)    
#    cli.execute(cmd2)    
    print "http://172.16.120.166/wiki/index.php/" + buildname

def main(argv):
    try:
        for arg in argv:
            if arg == "-e":
                ecfg = argv[argv.index(arg) + 1]

    except IndexError, e:
        print inred("Error: you must input the parameter value of --build or --ingredient")
        exit(-1)
    print ecfg
    wiki_xml(ecfg)

if __name__ == "__main__":
    main(sys.argv)

