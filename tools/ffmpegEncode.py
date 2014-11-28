#-*- coding: UTF-8 -*-

import sys
sys.path.append("../../pytest/")
sys.path.append("../pytest/")
import os
import commands
import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
from exceptions import IOError, AttributeError

from tools.color import inred, ingreen, inpurple

def ffmpegEncode(casePath, serialNumber):
    
    try:
        from conf import path
    except Exception, e:
        print inred("No path.py generated. please run setup.py again.")
        return -1
    try:
        xml_tree = ET.parse((casePath + "/run.xml").replace('//', '/'))
    except ExpatError, e:
        print ("Cannot open file: " + (casePath + "/run.xml").replace('//', '/'))
        return -1
    
    root = xml_tree.getroot()
    try:
        if casePath[-1] == '/':
            casePath = casePath[:-1]
        caseName = casePath.split('/')[-1]
        inputFile = root.find('Step').find('Parameter').find('InputFile').text
        resolution = root.find('Step').find('Parameter').find('Resolution').text
        bitRate = str(long(root.find('Step').find('Parameter').find('BitRate').text)/1000)
        frame = inputFile[:inputFile.find("frame")].split('_')[-1]
    except Exception, e:
        print inred("Error reading element info from " + (casePath + "/run.xml").replace('//', '/'))
        return -1
    
    print ("inputFile: " + inputFile)
    print ("resolution: " + resolution)
    print ("bitRate: " + bitRate)
    print ("frame: " + frame)
    
    #generate folders
    yuvPath = path.resultClip_path + '/' + caseName + "/ffmpegEncode/YUV/"
    I420Path = path.resultClip_path + '/' + caseName + "/ffmpegEncode/I420/"
    EncodedClipPath = path.resultClip_path + '/' + caseName + "/ffmpegEncode/EncodedClip/"
    os.system("mkdir -p " + yuvPath)
    os.system("mkdir -p " + I420Path)
    os.system("mkdir -p " + EncodedClipPath)
       
    os.system("rm -rf 1.yuv")
    status, output = commands.getstatusoutput("ls " + yuvPath + inputFile)
    if output.find("No such file or directory") != -1:
        print inpurple("\nCopy yuv file from device......")
        command = "adb -s " + serialNumber + " pull " + path.clipPath + "YUV/" + inputFile + " " + yuvPath
        os.system(command)
        status, output = commands.getstatusoutput("ls " + yuvPath + inputFile)
        if output.find("No such file or directory") != -1:
            print inred("Error: cannot found yuv file in device " + serialNumber + ":" + path.clipPath + "YUV/" + inputFile)
            return -1
        
    print inpurple("\nConvert NV12 clip to I420......")
    cmd = "yuvtool convert -s " + resolution + " -i " + yuvPath + inputFile + " -ifourcc NV12 -ofourcc I420 -o " + I420Path + inputFile
    print "Command: " + cmd
    os.system(cmd)
    
    print inpurple("\nEncode I420 yuv clip......")
    cmd = "ffmpeg -s " + resolution + " -pix_fmt yuv420p -i " + yuvPath + inputFile + " -vcodec libx264 -preset fast -b " + bitRate + "k -threads 0 " + EncodedClipPath + inputFile.split('.')[0] + ".mp4"
    print "Command: " + cmd
    os.system(cmd)
    
    print inpurple("\nDecode encoded file to yuv......")
    os.system("ffmpeg -i " + EncodedClipPath + inputFile.split('.')[0] + ".mp4 1.yuv")
    
    print inpurple("\nCauculate PSNR......")
    cmd = "yuvtool psnr -s " + resolution + " -i " + I420Path + inputFile + " -o 1.yuv -n " + frame
    print "Command: " + cmd
    status, output = commands.getstatusoutput(cmd)
    print ("\nOutput: \n" + output)
    
    os.system("rm -rf 1.yuv")

if __name__ == '__main__':
    ffmpegEncode(sys.argv[1], sys.argv[2])
