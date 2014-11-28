import os
import sys
import commands

def parseMediaInfo(mediaFile):
    
    resultDict = {}
    
    status, output = commands.getstatusoutput("mediainfo " + mediaFile)
    try:
        generaInfo = output.split('\n\n')[0]
    except Exception, e:
        generaInfo = ''
    try:
        videoInfo = output.split('\n\n')[1]
    except Exception, e:
        videoInfo = ''
    try:
        audioInfo = output.split('\n\n')[2]
    except Exception, e:
        audioInfo = ''  
        
    #obtain VideoFormat
    try:
        videoFormat = videoInfo[videoInfo.find("Format"):].split('\n')[0].split(':')[1].replace(' ', '')  
    except Exception, e:
        videoFormat = ''
    resultDict.setdefault('VideoFormat', videoFormat)
    
    #obtain VideoProfile
    try:
        videoProfile = videoInfo[videoInfo.find("Format profile"):].split('\n')[0].split(':')[1].replace(' ', '').split('@')[0]  
    except Exception, e:
        videoProfile = ''
    resultDict.setdefault('VideoProfile', videoProfile)
    
    #obtain VideoLevel
    try:
        videoLevel = videoInfo[videoInfo.find("Format profile"):].split('\n')[0].split(':')[1].replace(' ', '').split('@')[1]  
    except Exception, e:
        videoLevel = ''
    resultDict.setdefault('VideoLevel', videoLevel)
    
    #obtain Resolution
    try:
        width = videoInfo[videoInfo.find("Width"):].split('\n')[0].split(':')[1].replace(' ', '').replace('pixels', '') 
        height = videoInfo[videoInfo.find("Height"):].split('\n')[0].split(':')[1].replace(' ', '').replace('pixels', '') 
        resolution = width + 'x' + height
    except Exception, e:
        resolution = ''
    resultDict.setdefault('Resolution', resolution)

    #obtain VideoBitrate
    try:
        eraseDisturbance = videoInfo.replace('Bit rate mode', '')
        videoBitrate = eraseDisturbance[eraseDisturbance.find("Bit rate"):].split('\n')[0].split(':')[1].replace(' ', '').replace('Kbps', '').replace('Mbps', '') 
        if eraseDisturbance[eraseDisturbance.find("Bit rate"):].split('\n')[0].split(':')[1].find('Mbps') != -1:
            videoBitrate = int(float(videoBitrate) * 1000)
    except Exception, e:
        videoBitrate = ''
    resultDict.setdefault('VideoBitrate', str(videoBitrate))

    #obtain FPS
    try:
        eraseDisturbance = videoInfo.replace('Frame rate mode', '')
        fps = eraseDisturbance[eraseDisturbance.find("Frame rate"):].split('\n')[0].split(':')[1].replace(' ', '').replace('fps', '') 
    except Exception, e:
        fps = ''
    resultDict.setdefault('FPS', fps)
    
    #obtain AudioFormat
    try:
        audioFormat = audioInfo[audioInfo.find("Format"):].split('\n')[0].split(':')[1].replace(' ', '')  
    except Exception, e:
        audioFormat = ''
    resultDict.setdefault('AudioFormat', audioFormat)
    
    #obtain AudioBitrate
    try:
        eraseDisturbance = audioInfo.replace('Bit rate mode', '')
        audioBitrate = eraseDisturbance[eraseDisturbance.find("Bit rate"):].split('\n')[0].split(':')[1].replace(' ', '').replace('Kbps', '').replace('Mbps', '')
        if eraseDisturbance[eraseDisturbance.find("Bit rate"):].split('\n')[0].split(':')[1].find('Mbps') != -1:
            audioBitrate = int(float(audioBitrate) * 1000)
    except Exception, e:
        audioBitrate = ''
    resultDict.setdefault('AudioBitrate', str(audioBitrate))
    
    #obtain VideoDuration
    try:
        videoDuration = videoInfo[videoInfo.find("Duration"):].split('\n')[0].split(':')[1].replace(' ', '')  
    except Exception, e:
        videoDuration = ''
        
    duration_str = videoDuration
    #obtain hour
    if duration_str.find('h') != -1:
        if duration_str.split('h')[0] == '':
            hour = 0
            duration_str = duration_str.split('h')[1]
        else:
            hour = int(duration_str.split('h')[0]) * 3600
            duration_str = duration_str.split('h')[1]
    else:
        hour = 0
    #obtain minite
    if duration_str.find('mn') != -1:
        if duration_str.split('mn')[0] == '':
            minite = 0
            duration_str = duration_str.split('mn')[1]
        else:
            minite = int(duration_str.split('mn')[0]) * 60
            duration_str = duration_str.split('mn')[1]
    else:
        minite = 0
    #obtain second
    if duration_str.find('s') != -1 and duration_str.split('s')[0][-1] != 'm':
        if duration_str.split('s')[0] == '':
            second = 0
            duration_str = duration_str.split('s')[1]
        else:
            second = int(duration_str.split('s')[0]) 
            duration_str = duration_str[duration_str.find('s')+1:]
    else:
        second = 0
    #obtain millisecond
    if duration_str.find('ms') != -1:
        if duration_str.split('ms')[0] == '':
            millisecond = 0
        else:
            millisecond = float(duration_str.split('ms')[0]) / float(1000)
    else:
        millisecond = 0
    
    resultDuration = float(hour + minite + second + millisecond)
        
    resultDict.setdefault('VideoDuration', str(resultDuration))

    return resultDict


def main(argv):
    
    resultDict = []
    errorFlag = True
    
    if len(argv) < 2:
        print "Error: must input absolute clip path!"
    elif len(argv) > 2:
        print "Error: you should only input one clip path!"
    else:
        mediaFile = argv[1]
        resultDict = parseMediaInfo(mediaFile)
        
        #checkErrorFlag
        for eachDictMem in resultDict:
            if resultDict[eachDictMem] != '':
                errorFlag = False
                break
        if errorFlag == False:
            #print resultDict
            for eachDictMem in resultDict:
                print eachDictMem + ':' + ' '*(25-len(eachDictMem)-len(resultDict[eachDictMem])) + resultDict[eachDictMem]
        else:
            print "Wrong clip path!"
            
            
if __name__ == "__main__":
    main(sys.argv)