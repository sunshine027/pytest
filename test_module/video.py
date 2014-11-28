import sys
import os
from conf import path
from common_module.dataparser import DataParser
from exceptions import IOError, AttributeError, KeyError
from common_module.testexception import TestException
from common_module.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite
from common_module.shellExecutor import executeShell

class vaTS:
    def __init__(self, step_id, par_dict, dev_dict1, crt, cam, casename):
        self.step_id = step_id
        self.dict = par_dict
        self.dict1 = dev_dict1
        self.crt = crt
        self.casename = casename
        print "Parameter List: "
        for key in self.dict:
            print key , ": " , self.dict[key]
        #print self.dict
        print ""
        self.rt_dict = {}
        
        crt_list = list(crt)
        print "Pass Criterion: "
        crt_exist = 0
        for crt_no in crt_list:
            if cmp(crt_no.text,'Off'):
                print crt_no.tag, crt_no.text
                crt_exist = 1
        if crt_exist == 0:
            print "None"
        print ''
        if not self.dict1.get('Connect', ''):
            raise TestException("Error: no Connect element found in device's profile, while running")
        if not self.dict1.get('Connect', '') in ['ssh', 'adb']:
            raise TestException("Error: the text of Connect element should be ssh or adb in device's profile ")            
        if not cmp(self.dict1['Connect'], 'ssh'):
            self.prefix = ''  
            from common_module.client import sshAccessor as accessor
#            self.Clip_Path='/mnt/video-tests/Clips/'

        if not cmp(self.dict1['Connect'], 'adb'):
            self.prefix = '/system/bin/'
            from common_module.client import adbAccessor as accessor
#            self.Clip_Path='/sdcard/'
        self.cli = accessor(self.dict1)
        try:
            self.Clip_Path = path.vd_clip
        except AttributeError, e:
           raise TestException("Error: no vd_clip in path.py, maybe there is something wrong during run setup.py ")

    def decode(self):
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        try:
            if not cmp(self.dict['Codec'], 'H263'):
                vld = 'mpeg4vld'
            else:
                vld = self.dict['Codec'].lower() + 'vld'
        except KeyError:
            raise TestException("Error: no Codec element found in Parameter element ")
        try:
            Clip = self.Clip_Path + self.dict['Codec'] + '/' + self.dict['ClipFile']
        except KeyError:
            raise TestException("Error: no ClipFile element found in Parameter element ")
        if self.dict.get('OutputYUV') is None or not cmp(self.dict['OutputYUV'], 'Off'):
            outp = ''
        else:
            try:
                outp = ' -o '+ path.Result + self.dict['OutputYUV']
            except AttributeError, e:
                raise TestException("Error: no Result in path.py, maybe there is something wrong during run setup.py ")
        if self.dict.get('CRC') is None or not cmp(self.dict['CRC'], 'Off'):
            crcp = ''
        else:
            crcp = ' -c'

        if self.dict.get('Window') is None or not cmp(self.dict['Window'], 'Off'):
            wdp = ''
        else:
            wdp = ' -n'

        if self.dict.get('FPS') is None or not cmp(self.dict['FPS'], 'Off'):
            fpsp = ''
        else:
            fpsp = ' -r '+ self.dict['FPS']

        if self.dict.get('Rotation') is None or not cmp(self.dict['Rotation'], 'Off'):
            rp = ''
        else:
            rp = ' -z ' + self.dict['Rotation']

        if self.dict.get('Headerlog') is None or not cmp(self.dict['Headerlog'], 'Off'):
            hp = ''
        else:
            try:
                hp = ' -headerlog ' +  path.Result + self.dict['Headerlog']
            except AttributeError, e:
                raise TestException("Error: no Result in path.py, maybe there is something wrong during run setup.py ")

        if self.dict.get('FullScreen') is None or not cmp(self.dict['FullScreen'], 'Off'):
            fsp = ''
        else:
            fsp = ' -k'

        if self.dict.get('Display') is None or not cmp(self.dict['Display'],'overlay'):
            dp = ''
        else:
            dp = 'PSB_VIDEO_CTEXTURE=1 '

        cmd1 = dp + self.prefix + vld + ' -x -i ' + Clip + outp + crcp + wdp + fpsp + rp + hp + fsp
        print "Command:"
        print cmd1
        print ""
        self.rt_dict.setdefault('cmd', cmd1)

#execute in remote device
        print "Execute Output: "
        stdout,stderr = self.cli.execute(cmd1)
        if stdout == '':
            raise TestException("Error: No content in log. You may use a wrong test tool or wrong platform ")

#result parsing
#        outfile = open('log','w+')
        outfile = open('log' + str(self.step_id), 'w+')
        outfile.writelines(stderr)
        outfile.writelines(stdout)
        outfile.close()
        
#        outfile='log'
        outfile='log' + str(self.step_id)
        dp = DataParser()
        try:
            crc_value = self.dict['CRC']
        except KeyError, e:
            raise TestException("Error: no CRC element found ")
        try:
            outputYUV_value = self.dict['OutputYUV']
        except KeyError, e:
            raise TestException("Error: no OutputYUV element found ")

        if cmp(crc_value, 'Off'):
            NV, YV = dp.vld_crc(outfile)
#            print NV,YV
            self.rt_dict.setdefault('NV12_CRC', NV)
            self.rt_dict.setdefault('YV12_CRC', YV)

        if cmp(outputYUV_value, 'Off'): 
            cmd2 = 'md5sum '+ path.Result + outputYUV_value
            #print cmd2
            stdout,stderr = self.cli.execute(cmd2)
            md5 = dp.md5sum(stdout)
            self.rt_dict.setdefault('MD5', md5)
            try:
                os.remove(self.dict['OutputYUV'])
            except Exception, e:
                print e.message
#        for line in stdout.readlines():
#            print line
#        md5 = dp.md5sum(stdout)
        fps = dp.fps(outfile)
#        print fps
        self.rt_dict.setdefault('FPS', fps)
        self.cli.teardown()
        return self.rt_dict

    def encode(self):
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        try:
            Clip = self.Clip_Path + 'YUV/' + self.dict['InputFile']
        except KeyError, e:
            raise TestException("Error: no InputFile element found in Parameter element")
        try:
            if cmp(self.dict1['Platform'], 'MFLD'):
                set = ''
            else:
                set = 'MFLD=1 '
        except KeyError, e:
            raise TestException("Error: no Platform element found in device's profile ")

        if self.dict.get('Codec') is None or self.dict.get('Resolution') is None or self.dict.get('IntraPeriod') is None:
            self.tc_dict.setdefault('rt','F')
            return self.tc_dict

        if self.dict.get('RecYUV') is None or not cmp(self.dict['RecYUV'],'Off'):
            recp = ''
        else:
            try:
                recp = ' -recyuv ' +  path.Result + self.dict['RecYUV']
            except AttributeError, e:
                raise TestException("Error: no Result in path.py, maybe there is something wrong during run setup.py ")  

        if self.dict['IntraPeriod'] is None or not cmp(self.dict['IntraPeriod'],'Off'):
            itpp = ''
        else:
            itpp = ' -intracnt ' + self.dict['IntraPeriod']

        if self.dict['IDRPeriod'] is None or not cmp(self.dict['IDRPeriod'],'Off'):
            idrp = ''
        else:
            idrp = ' -idrcnt ' + self.dict['IDRPeriod']

        if self.dict['QP'] is None or not cmp(self.dict['QP'],'Off'):
            qpp = ''
        else:
            qpp = ' -qpluma ' + self.dict['QP']

        if self.dict['FPS'] is None or not cmp(self.dict['FPS'],'Off'):
            fpsp = ''
        else:
            fpsp = ' -framerate ' + self.dict['FPS']

        if self.dict['RC'] is None or not cmp(self.dict['RC'],'Off'):
            rcp = ''
        else:
            rcp = ' -rcEnable -rcMode ' + self.dict['RC']

        if self.dict['BitRate'] is None or not cmp(self.dict['BitRate'],'Off'):
            brp = ''
        else:
            brp = ' -bitrate ' + self.dict['BitRate']

        if self.dict['Slices'] is None or not cmp(self.dict['Slices'],'Off'):
            slip = ''
        else:
            slip = ' -slices ' + self.dict['Slices']

        if self.dict['PSNR'] is None or not cmp(self.dict['PSNR'],'Off'):
            psnrp = ''
        else:
            psnrp = ' -enablePSNR'

        if self.dict['FrameSizeLog'] is None or not cmp(self.dict['FrameSizeLog'],'Off'):
            fslp = ''
        else:
            try:
                fslp = ' -frame_size_log ' + path.Result + self.dict['FrameSizeLog']
            except AttributeError, e:
                raise TestException("Error: no Result in path.py, maybe there is something wrong during run setup.py ")
        if self.dict['OutputFile'] is None or not cmp(self.dict['OutputFile'], 'Off'):
            op = ' -o /dev/null'
        else:
            try:
                op = ' -o ' + path.Result + self.dict['OutputFile']
            except AttributeError, e:
                raise TestException("Error: no Result in path.py, maybe there is something wrong during run setup.py ")

        if self.dict['DeblockIDC'] is None or not cmp(self.dict['DeblockIDC'], 'Off'): 
            didc = ''
        else:
            didc = ' -deblockIDC ' + self.dict['DeblockIDC']
 
        if self.dict['Profile'] is None or not cmp(self.dict['Profile'],'Off'):
            pro= ''
        else:
            pro= ' -profile ' + self.dict['Profile']
 
        if self.dict['Level'] is None or not cmp(self.dict['Level'],'Off'):
            lev= ''
        else:
            lev= ' -level ' + self.dict['Level']
 

        rl = self.dict['Resolution'].split("x")
        try:
            width = rl[0]
            height = rl[1]
        except IndexError:
            raise TestException("Error: the text of Resolution in Parameter element should be in the format of 120x320, 120 means width, and 320 means height ")

        cmd1 = set + self.prefix + 'va_encode -w ' + width + ' -h ' + height + ' -srcyuv ' + Clip + op  + ' -framecount ' + self.dict['FrameCount'] + ' -t ' + self.dict['Codec'] +\
 recp + didc + pro + lev + itpp + idrp + qpp + fpsp + rcp + brp + psnrp + fslp + slip
        print "Command:"
        print cmd1 + "\n"
        self.rt_dict.setdefault('cmd', cmd1)

        print "Execute Output: "
        stdout,stderr = self.cli.execute(cmd1)
        if stdout == '':
            raise TestException("Error: No content in log. You may use a wrong test tool or wrong platform ")
        outfile = open('log' + str(self.step_id),'w+')
        outfile.writelines(stderr)
        outfile.writelines(stdout)
        outfile.close()

        outfile='log' + str(self.step_id)
        dp = DataParser()
        try:
            psnr_value = self.dict['PSNR']
        except KeyError, e:
            raise TestException("Error: no PSNR element found in Parameter element")
        if cmp(psnr_value, 'Off'):
            PSNR = dp.psnr(outfile)
            print PSNR
            self.rt_dict.setdefault('PSNR', PSNR)
            try:
                recyuv_value = self.dict['RecYUV']
            except KeyError, e:
                raise TestException("Error: no RecYUV element found in Parameter element")   
            try:
                cmd2 = "rm -f %s" %path.Result + recyuv_value
            except AttributeError, e:
                raise TestException("Error: no Result in path.py, maybe there is something wrong during run setup.py ")
            self.cli.execute(cmd2)

        fps = dp.fps(outfile)
        self.rt_dict.setdefault('FPS', fps)
        self.cli.teardown()
        return self.rt_dict

    def headerlog_parse(self):
        file = path.Result + self.dict['Log']        
        begin_frameno = self.dict['BeginFrameNo']
        end_frameno = self.dict['EndFrameNo']
        fps = self.dict['FPS']
        windowsize = self.dict['WindowSize']

        min_bitrate = 0
        max_bitrate = 0
        max_ssize = 0
        min_ssize = 0
        min_scnt = 0
        max_scnt = 0
        min_i_interval = 0
        max_i_interval = 0
        min_idr_interval = 0
        max_idr_interval = 0

        self.cli.download(file,'hlog')

        if not os.path.isfile('hlog'):
            print 'log not exist'
        else:
            fd = open('hlog')

            slice_size = 0
            slice_no = 0
	    i_no = 0
	    pre_idr_fno = 0
	    idr_no = 0
	    idr_interval = 0
            fps = int(fps)/(1000/int(windowsize))
            framecnt = int(end_frameno) - int(begin_frameno)

            for line in fd.readlines():
                ost1 = line.find('Slice')
                pre_fno = 0
                if ost1 > 0 :
                    list = line.split(' ')
                    t = 0 
                    for l in list:
                        if not cmp(l,'frame_num'):
                            fno = t-1
                        if not cmp(l,'(slice'):
                            sno = t-1
                        if not cmp(l.strip(),'bits)'):
                            ssno = t-1
                        t += 1
                    frame_no = list[fno]
                    slice_no = list[sno]
                    ssize = list[ssno]

                    if int(frame_no) >= int(begin_frameno) and int(frame_no) <= int(end_frameno):
                        if int(frame_no) == int(begin_frameno) and int(slice_no)==0:
                            pre_bitrate = 0
                            bitrate = 0
    			    pre_fno = int(frame_no)
                            pre_sno = 0
                            min_ssize = int(ssize)
                            max_ssize = int(ssize)
	            
			    #calculate IDR frame interval
			ost2 = line.find('IDR')
                        if ost2 > 0:
                            if int(frame_no) !=0 and pre_idr_fno == 0:
                                min_idr_interval = int(frame_no)
                                max_idr_interval = int(frame_no)
                        else:
                            idr_interval = int(frame_no) - pre_idr_fno
 
                        pre_idr_fno = int(frame_no)
                        if idr_interval > max_idr_interval:
                            max_idr_interval = idr_interval
                        if idr_interval < min_idr_interval:
                            min_idr_interval = idr_interval
			    
			#calculate IDR frame interval

                        # calculate bitrate 
                        if int(framecnt) > int(fps):
                            if  int(frame_no)%fps == 0 and int(slice_no)==0:
                                if pre_bitrate == 0:
                                    min_bitrate = bitrate
                                    max_bitrate = bitrate
                                    pre_bitrate = bitrate
                                else:
                                    pre_bitrate = bitrate
                                    if pre_bitrate > max_bitrate:
                                        max_bitrate = pre_bitrate
                                    if pre_bitrate < min_bitrate:
                                        min_bitrate = pre_bitrate
                                bitrate = 0
                            bitrate += int(ssize)
                    
	                # calculate slice number
                        if int(frame_no) != pre_fno:
                            if int(frame_no) == (int(begin_frameno)+1):
		                min_scnt = pre_sno
                                max_scnt = pre_sno

                            if pre_sno > max_scnt:
                                max_scnt = pre_sno
                            if pre_sno < min_scnt:
                                min_scnt = pre_sno

                            pre_fno = int(frame_no)

                        pre_sno = int(slice_no)
            
		        # calculate slice size
                        if int(ssize) > max_ssize:
                            max_ssize = int(ssize)
                        if int(ssize) < min_ssize:
                            min_ssize = int(ssize)
	            
                    else:
                        break
   	    max_scnt += 1
  	    min_scnt += 1
	    os.remove('hlog')

        self.rt_dict.setdefault('MaxBitrate',max_bitrate)
        self.rt_dict.setdefault('MinBitrate',min_bitrate)
        self.rt_dict.setdefault('MaxSliceSize',max_ssize)
        self.rt_dict.setdefault('MinSliceSize',min_ssize)
        self.rt_dict.setdefault('MaxSliceNum',max_scnt)
        self.rt_dict.setdefault('MinSliceNum',min_scnt)
        self.rt_dict.setdefault('MaxIDRInterval',max_idr_interval)
        self.rt_dict.setdefault('MinIDRInterval',min_idr_interval)

    	self.cli.teardown()
        return self.rt_dict
                    
    def jpeg_encode(self):
        
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        try:
            inputFile = self.dict['InputFile']
        except KeyError, e:
            raise TestException("Error: no InputFile element found in Parameter element")
        try:
            resolution = self.dict['Resolution']
        except KeyError, e:
            raise TestException("Error: no Resolution element found in Parameter element")
        rl = self.dict['Resolution'].split("x")
        if len(rl) != 2:
            raise TestException("Error: the text of Resolution must be in the format like 120x340, 120 means width, and 340 means height ")
        width = rl[0]
        height = rl[1]
        try:
            OutputFile = self.dict['OutputFile']
        except KeyError, e:
            raise TestException("Error: no OutputFile element found in Parameter element")
        try:
            Quality = self.dict['Quality']
        except KeyError, e:
            raise TestException("Error: no Quality element found in Parameter element")
        
        if self.dict['FrameCount'] is None or not cmp(self.dict['FrameCount'],'Off'):
            fc = ''
        else:
            fc = ' -c ' + self.dict['FrameCount']
        
        prefix = path.vd_clip + 'Image/'
        
        cmd =  "penwell_jpegEncode" + " -w " + width+ " -h " + height + " -f " + prefix + inputFile + " -o " + prefix + OutputFile + " -q " + Quality + fc
        
        print "Command:"
        print cmd + "\n"
        self.rt_dict.setdefault('cmd', cmd)

        print "Execute Output: "
        stdout,stderr = self.cli.execute(cmd)
        if stdout == '':
            raise TestException("Error: No content in log. You may use a wrong test tool or wrong platform ")
        outfile = open('log' + str(self.step_id), 'w+')
        outfile.writelines(stderr)
        outfile.writelines(stdout)
        outfile.close()
        
        #obtain time consumption
        fd = open('log' + str(self.step_id))
        textlist = fd.readlines()
        try:
            text = textlist[len(textlist)-1]
        except IndexError, e:
            print inblue("Tips: maybe you executed this case in a wrong platform.")
            os.system('rm -f ./log' + str(self.step_id))
            raise TestException("JPEG log error: no content in JPEG log!")
        ost1 = text.find("JPEEGs in") + 10
        ost2 = text.find("ms") + 2
        TimeCons = text[ost1:ost2]
        self.rt_dict.setdefault('TimeConsumption', TimeCons)
        fd.close()
        
        #obtain Compression ratio
        self.cli.download(prefix + inputFile , './' + inputFile)
        self.cli.download(prefix + OutputFile + '0000.jpg' , './' + OutputFile + '0000.jpg')
        self.cli.execute("mv " + prefix + OutputFile + '0000.jpg ' + path.Result)
        inputFileSize = os.path.getsize('./' + inputFile)
        outputFileSize = os.path.getsize('./' + OutputFile + '0000.jpg')
        result = float(outputFileSize) / float(inputFileSize) * 100
        comRatio = '%.2f'%result + '%'

        self.rt_dict.setdefault('CompressionRatio', comRatio)
        
        #obtain psnr
        res = os.system('djpeg -bmp -outfile 1.bmp '+ OutputFile + '0000.jpg')
        res = os.system("./resource/yuvtool convert -s " + resolution + " -i 1.bmp -ifourcc BMP -o 1.nv12 -ofourcc NV12 ")
        res = os.system('./resource/yuvtool psnr -s ' + resolution +' -i ' + inputFile + ' -o 1.nv12 >psnr.log')
        try:
            fd = open('psnr.log')
        except IOError, e:
            raise TestException("ERROR: psnr.log doesn't exist.")
        textlist = fd.readlines()
        text = textlist[len(textlist)-1]
        ost1 = text.find("PSNR") + 6
        ost2 = text.find("bytes") - 2
        psnr = text[ost1:ost2]
#        print "PSNR: " + text[ost1:ost2]
        self.rt_dict.setdefault('PSNR', psnr)
        fd.close()
        
#        #get psnr in Criteria
#        bmpInputFile = self.dict['InputFile'].split(".")[0] + '.bmp'
#        self.cli.download(prefix + bmpInputFile, './' + bmpInputFile)
#        os.system("cjpeg -quality " + Quality + " -outfile psnr_outbmp " + './' + bmpInputFile)
#        os.system('djpeg -bmp -outfile 2.bmp psnr_outbmp')
#        os.system("./resource/yuvtool convert -s " + resolution + " -i 2.bmp -ifourcc BMP -o 2.nv12 -ofourcc NV12")
#        os.system('./resource/yuvtool psnr -s ' + resolution +' -i ' + inputFile + ' -o 2.nv12 >psnr_2.log')
#        fd = open('psnr_2.log')
#        textlist = fd.readlines()
#        text = textlist[len(textlist)-1]
#        ost1 = text.find("PSNR") + 6
#        ost2 = text.find("bytes") - 2
#        psnr_2 = text[ost1:ost2]
#        print "PSNR: " + text[ost1:ost2]
#        self.rt_dict.setdefault('PSNRinCriteria', psnr_2)
#        fd.close()
#        
#        os.system('rm -f ./' + bmpInputFile)
#        os.system('rm -f ./psnr_outbmp')
#        os.system('rm -f ./2.bmp')
#        os.system('rm -f ./2.nv12')
#        os.system('rm -f ./psnr_2.log')

       
        #delete locale files
        os.system('rm -f ./' + inputFile)
        os.system('rm -f ./' + OutputFile + '0000.jpg')
        os.system('rm -f ./1.nv12')
        os.system('rm -f ./1.bmp')
        os.system('rm -f ./psnr.log')

        self.cli.teardown()
        return self.rt_dict
    
    def libVAAPI(self):
        
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        try:
            cmdname = self.dict['cmdname']
        except KeyError, e:
            raise TestException("Error: no cmdname element found in Parameter element") 
        try:
            serialNo = self.dict1['serialNumber']
        except KeyError, e:
            raise TestException("Error: no serialNumber element found in device profile")  
        
        #execute
        cmd  = "cd /cache/LibVA-API_Test/ ; ./" + cmdname + " ; echo $?"
        stdout,stderr = executeShell(cmd, serialNo)
        
        #generate log file
        outfile = open('log' + str(self.step_id), 'w+')
        outfile.writelines(stderr)
        outfile.writelines(stdout)
        outfile.close()
        
        #obtain cmdReturn value
        fd = open('log' + str(self.step_id))
        textlist = fd.readlines()
        for text in textlist:
            if text == '\r\n':
                textlist.remove(text)
        try:
            text = textlist[len(textlist)-1]
        except IndexError, e:
            print inblue("Tips: maybe you executed this case in a wrong platform.")
            os.system('rm -f ./log' + str(self.step_id))
            raise TestException("JPEG log error: wrong JPEG log!")
        
        self.rt_dict.setdefault('CmdReturn', text)
        return self.rt_dict
        
            
            
            
            
            
            
            
            
            
            
