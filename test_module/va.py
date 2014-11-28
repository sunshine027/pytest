import sys
import os
import commands
from exceptions import IOError, AttributeError, KeyError

from conf import path
import conf
from tools.dataparser import DataParser
from exception.testexception import TestException
from tools.color import inred, ingreen, inblack, inyellow, inblue, inpurple, inwhite
from tools.shellExecutor import executeShell
from tools.client import execute_command_on_server
from test_module import script_path
from tools.get_execution_info import get_clip_path, get_result_path

LIBVA_FILE_PATH = '/system/LibVA-API_Test/'
LIBVA_SCRIPT_PATH = '/sdcard/'

class utility:
    def __init__(self, step_id, par_dict, dev_dict, crt, caseFolderName, all_monitor_thread_dict, stepType, platform):
        self.step_id = step_id
        self.dict = par_dict
        self.dict1 = dev_dict
        self.crt = crt
        self.caseFolderName = caseFolderName
        self.stepType = stepType
        self.platform = platform
        
        print "Parameter List: "
        for key in self.dict:
            print key , ": " , self.dict[key]
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
            from tools.client import sshAccessor as accessor
        if not cmp(self.dict1['Connect'], 'adb'):
            self.prefix = '/system/bin/'
            from tools.client import adbAccessor as accessor
        self.cli = accessor(self.dict1)
        self.Clip_Path = get_clip_path()

    def decode(self):
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        try:
            if not cmp(self.dict['Format'], 'H263'):
                vld = 'mpeg4vld'
            else:
                vld = self.dict['Format'].lower() + 'vld'
        except KeyError:
            raise TestException("Error: no Format element found in Parameter element ")
        try:
            inp = self.Clip_Path + self.dict['Format'] + '/' + self.dict['InputFile']
        except KeyError:
            raise TestException("Error: no InputFile element found in Parameter element ")
        outp = ''
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
            hp = ' -headerlog ' +  get_result_path() + self.dict['Headerlog']
            

        if self.dict.get('FullScreen') is None or not cmp(self.dict['FullScreen'], 'Off'):
            fsp = ''
        else:
            fsp = ' -k'

        if self.dict.get('Display') is None or not cmp(self.dict['Display'],'overlay'):
            dp = ''
        else:
            dp = 'PSB_VIDEO_CTEXTURE=1 '

        cmd = dp + self.prefix + vld + ' -x -i ' + inp + outp + crcp + wdp + fpsp + rp + hp + fsp
        print cmd
        self.rt_dict.setdefault('cmd', cmd)

        if self.stepType == 0 or self.stepType == 10:
            if self.stepType == 10:
                return "noResult"
        
        if self.stepType == 0 or self.stepType == 20:
            #execute in remote device
            print "Execute Output: \n"
            self.cli.execute_test(cmd, self.step_id)
            try:
                outfile = open('log' + str(self.step_id), 'r') 
            except IOError, e:
                print inred("Error: cannot generat log.")
                os.system("touch log" + str(self.step_id)) 
                outfile = open('log' + str(self.step_id), 'r')
            stdout = outfile.read()
            outfile.close()
            
            outfile='log' + str(self.step_id)
            dp = DataParser()
            try:
                crc_value = self.dict['CRC']
            except KeyError, e:
                raise TestException("Error: no CRC element found ")
            try:
                outputYUV_value = self.dict['OutputFile']
            except KeyError, e:
                raise TestException("Error: no OutputFile element found ")
    
            if cmp(crc_value, 'Off'):
                NV, YV = dp.vld_crc(outfile)
                self.rt_dict.setdefault('NV12_CRC', NV)
                self.rt_dict.setdefault('YV12_CRC', YV)
            fps = dp.fps(outfile)
            self.rt_dict.setdefault('FPS', fps)
            self.cli.teardown() 
           
        if self.stepType == 0 or self.stepType == 30:
            if self.stepType == 30:
                return "noResult"
            
        return self.rt_dict

    def encode(self):
        
        print "Command for va_log detection:"
                
        #enable va_log
        stdout,stderr = self.cli.execute("echo \\\"LIBVA_TRACE=/data/1\\\" > /etc/libva.conf")
        
        #delete original 
        stdout,stderr = self.cli.execute("rm -rf /data/1.*")
        
        print ""
        
        for item in self.dict:
            if self.dict[item] == None:
                raise TestException("Error: No text in element '" + item + "', please check the case profile.")
        try:
            inp = self.Clip_Path + self.dict['Format'] + '/' + self.dict['InputFile']
        except KeyError, e:
            raise TestException("Error: no InputFile element found in Parameter element")
        try:
            if cmp(self.dict1['Platform'], 'MFLD'):
                set = ''
            else:
                set = 'MFLD=1 '
        except KeyError, e:
            raise TestException("Error: no Platform element found in device's profile ")

        if self.dict.get('Format') is None or self.dict.get('Resolution') is None or self.dict.get('IntraPeriod') is None:
            self.tc_dict.setdefault('rt','F')
            return self.tc_dict

        if self.dict.get('RecYUV') is None or not cmp(self.dict['RecYUV'],'Off'):
            recp = ''
        else:
            recp = ' -recyuv ' +  get_result_path() + self.dict['RecYUV']

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

        if self.dict['RcMode'] is None or not cmp(self.dict['RcMode'],'Off'):
            rcp = ''
        else:
            rcp = ' -rcEnable -rcMode ' + self.dict['RcMode']

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
            fslp = ' -frame_size_log ' + get_result_path() + self.dict['FrameSizeLog']
        if self.dict['OutputFile'] is None or not cmp(self.dict['OutputFile'], 'Off'):
            op = ' -o /dev/null'
        else:
            op = ' -o ' + get_result_path() + self.dict['OutputFile']
            #create directory
            self.cli.execute('mkdir -p ' + get_result_path()) 
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

        cmd = set + self.prefix + 'va_encode -w ' + width + ' -h ' + height + ' -srcyuv ' + inp + op  + ' -framecount ' + self.dict['FrameCount'] + ' -t ' + self.dict['Format'] +\
 recp + didc + pro + lev + itpp + idrp + qpp + fpsp + rcp + brp + psnrp + fslp + slip
        self.rt_dict.setdefault('cmd', cmd)

        print cmd
        if self.stepType == 0 or self.stepType == 10:        
            #download clip if it does not exist in self.Clip_Path + 'YUV/'
            stdout, stderr = self.cli.execute("ls " + inp)
            flag = stdout.find("No such file or directory")
            if flag < 0:
                pass
            else:
                print '\nDownloading %s ......' %self.dict['InputFile']
                status, output = commands.getstatusoutput("wget --no-proxy " + config.VIDEO_CLIP_DOWNLOAD_PATH + self.dict['InputFile'])
                if status != 0:
                    raise TestException("Error: failed download " + self.dict['InputFile'] + ", maybe the clip storing address is invalid!\n")
                else:
                    print ingreen(self.dict['InputFile'] + " downloaded successfully.\n")
                    print ("Push " + self.dict['InputFile'] + " into device ......")
                    self.cli.upload(self.dict['InputFile'], self.Clip_Path + '/' + self.dict.get('Format') +'/')
                    os.system("rm -rf " + self.dict['InputFile'])

            if self.stepType == 10:
                return "noResult"
        
        if self.stepType == 0 or self.stepType == 20:
            #execute cmd
            print "Execute Output: \n"
            self.cli.execute_test(cmd, self.step_id)
            try:
                outfile = open('log' + str(self.step_id), 'r') 
            except IOError, e:
                print inred("Error: cannot generat log.")
                os.system("touch log" + str(self.step_id))
                outfile = open('log' + str(self.step_id), 'r') 
            dp = DataParser()
            try:
                psnr_value = self.dict['PSNR']
            except KeyError, e:
                raise TestException("Error: no PSNR element found in Parameter element")
            if cmp(psnr_value, 'Off'):
#                PSNR = dp.psnr(outfile)
#                print PSNR
#                self.rt_dict.setdefault('PSNR', PSNR)
                try:
                    recyuv_value = self.dict['RecYUV']
                except KeyError, e:
                    raise TestException("Error: no RecYUV element found in Parameter element")   
                try:
                    cmd2 = "rm -f %s" %get_result_path() + recyuv_value
                except AttributeError, e:
                    raise TestException("Error: no Result path in path.py, maybe there is something wrong during run setup.py ")
                self.cli.execute(cmd2)
                
            #copy psnr.log into result dir
            self.cli.download("/data/psnr.log", path.result_path + '/' + self.caseFolderName + '/' + self.step_id + ".psnr")
            self.cli.execute("rm -rf /data/psnr.log")
            
            #obtain yssim
            stdout = outfile.read()
            str1 = stdout.find("IMAGE QUALITY: yssim =") + 22
            if str1 == 11:
                print inred("Cannot find yssim value in log!")
                yssim = "null"
            else:
                str2 = stdout[str1: str1+20].find('\n')
                yssim = stdout[str1:str1+str2].replace('\n', '').replace(' ', '').replace('\r', '')
            self.rt_dict.setdefault('yssim', yssim)
            
            #obtain fps
            fps = dp.fps('log' + str(self.step_id))
            self.rt_dict.setdefault('FPS', fps)
            
            #obtain attrib[1].value
            stdout_text,stderr = self.cli.execute("head /data/1.0000.* -n 20")
            flag = stdout_text.find("attrib_list[1].value") + 23
            if flag == 22 :
                print inred("No attrib_list[1].value found in va_log.")
                attrib_value = "Off"
            else:
                attrib_value = stdout_text[flag : flag+10]
            stdout,stderr = self.cli.execute("rm /data/1.0000.*")
                    
            self.rt_dict.setdefault('AttribValue', attrib_value)
            
            outfile.close()
            self.cli.teardown()
                    
        if self.stepType == 0 or self.stepType == 30:
            
            #pull result clip to host
            os.system("mkdir -p " + path.resultClip_path + '/' + self.caseFolderName + '/')
            self.cli.download(get_result_path() + self.dict['OutputFile'], path.resultClip_path + '/' + self.caseFolderName + '/')
            
            if self.stepType == 30:
                return "noResult"
            
        return self.rt_dict

    def headerlog_parse(self):
        file = get_result_path() + self.dict['Log']        
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
            OutputFile = self.dict['OutputFile']
        except KeyError, e:
            raise TestException("Error: no OutputFile element found in Parameter element")
        prefix = get_clip_path() + 'Image/'
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
            Quality = self.dict['Quality']
        except KeyError, e:
            raise TestException("Error: no Quality element found in Parameter element")
        
        if self.dict['FrameCount'] is None or not cmp(self.dict['FrameCount'],'Off'):
            fc = ''
        else:
            fc = ' -c ' + self.dict['FrameCount']
        cmd =  "penwell_jpegEncode" + " -w " + width+ " -h " + height + " -f " + prefix + inputFile + " -o " + prefix + OutputFile + " -q " + Quality + fc
    
        print "Command:"
        print cmd + "\n"
        self.rt_dict.setdefault('cmd', cmd)

        if self.stepType == 0 or self.stepType == 10:
            if self.stepType == 10:
                return "noResult"
        
        if self.stepType == 0 or self.stepType == 20:
            #execute cmd
            print "Execute Output: \n"
            self.cli.execute_test(cmd, self.step_id)
            try:
                outfile = open('log' + str(self.step_id), 'r') 
            except IOError, e:
                print inred("Error: cannot generat log.")
                os.system("touch log" + str(self.step_id))
            stdout = outfile.read()
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
            self.cli.execute("mv " + prefix + OutputFile + '0000.jpg ' + get_result_path())
            try:
                inputFileSize = os.path.getsize('./' + inputFile)
                outputFileSize = os.path.getsize('./' + OutputFile + '0000.jpg')
            except OSError:
                raise TestException("Something wrong happens when executing the JPEG test. Can not find JPEG output file.")
            result = float(outputFileSize) / float(inputFileSize) * 100
            comRatio = '%.2f'%result + '%'
    
            self.rt_dict.setdefault('CompressionRatio', comRatio)
            
            #obtain psnr
            res = os.system('/opt/jpeg-8b/bin/djpeg -bmp -outfile 1.bmp '+ OutputFile + '0000.jpg')
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
            self.rt_dict.setdefault('PSNR', psnr)
            fd.close()
            
            #delete locale files
            os.system('rm -f ./' + inputFile)
            os.system('rm -f ./' + OutputFile + '0000.jpg')
            os.system('rm -f ./1.nv12')
            os.system('rm -f ./1.bmp')
            os.system('rm -f ./psnr.log')
    
            self.cli.teardown()
        
        if self.stepType == 0 or self.stepType == 30:
            if self.stepType == 30:
                return "noResult"
            
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
        
        if self.stepType == 0 or self.stepType == 10:
            if self.stepType == 10:
                return "noResult"
        
        if self.stepType == 0 or self.stepType == 20:
            #execute
            self._download_run_file(cmdname)
            self._push_script()
            cmd = 'sh ' + LIBVA_SCRIPT_PATH + 'run.sh ' + cmdname
            stdout,stderr = executeShell(cmd, serialNo)
            
            #generate log file
            outfile = open('log' + str(self.step_id), 'w+')
            outfile.writelines(stderr)
            outfile.writelines(stdout)
            outfile.close()
            
            if stdout.replace('\n', '').replace('\r', '').replace('\t', '').replace('-', '').strip().endswith('pass'):
                result = 0
            else:
                result = -1
            #delete libva file to save space in /system
            cmd = 'rm ' + LIBVA_FILE_PATH + cmdname
            self.cli.execute(cmd)
            self.rt_dict.setdefault('CmdReturn', result)
            
        
        if self.stepType == 0 or self.stepType == 30:
            if self.stepType == 30:
                return "noResult"
            
        return self.rt_dict
    
    def _download_run_file(self, cmdname):
        count = 0
        
        while count < 3:
            url = 'http://172.16.120.166/media_resource/MFLD_Android/LibVA-API_Test/'
            if self.platform is not None and self.platform.lower().strip() == 'ctp':
                url += 'CTP_PR1/'
            else:
                url += 'mfld_pr3/'
            url += cmdname
            download_url = 'wget --no-proxy ' + url
            execute_command_on_server(download_url, False)
            cmd = 'test -f ' + str('./' + cmdname) + " && echo 'File exists' || echo 'File not found'"
            stdout, stderr = execute_command_on_server(cmd, False)
            if stdout.strip() == 'File exists':
                self.cli.upload(cmdname, LIBVA_FILE_PATH)
                cmd = 'test -f ' + str(LIBVA_FILE_PATH + cmdname) + " && echo 'File exists' || echo 'File not found'"
                stdout, stderr = self.cli.execute(cmd)
                if stdout.strip() == 'File exists':
                    cmd = 'chmod 777 ' + str(LIBVA_FILE_PATH + cmdname) 
                    stdout, stderr = self.cli.execute(cmd)
                    os.system("rm -rf " + cmdname)
                    break
                else:
                    raise TestException("Error: can't push libva file to DUT")
            else:
                count += 1
        if count == 3:
            raise TestException("Error: can't download libva file with url: " + url)
        
    def _push_script(self):
        cmd = 'test -f ' + LIBVA_SCRIPT_PATH + 'run.sh' + " && echo 'File exists' || echo 'File not found'"
        stdout, stderr = self.cli.execute(cmd)
        if stdout.strip() == 'File exists':
            cmd = 'chmod 777 ' + str(LIBVA_SCRIPT_PATH + 'run.sh') 
            stdout, stderr = self.cli.execute(cmd)
        elif stdout.strip() == 'File not found':
            self.cli.upload(script_path + '/run.sh', LIBVA_SCRIPT_PATH)
            cmd = 'test -f' + LIBVA_SCRIPT_PATH + 'run.sh'  + " && echo 'File exists' || echo 'File not found'"
            stdout, stderr = self.cli.execute(cmd)
            if stdout.strip() == 'File exists':
                cmd = 'chmod 777 ' + str(LIBVA_SCRIPT_PATH + 'run.sh') 
                stdout, stderr = self.cli.execute(cmd)
            elif stdout.strip() == 'File not found':
                raise TestException("Error: can't push libva file script to DUT's directory: " + LIBVA_SCRIPT_PATH)
        
        
        
        
        
        
            
            
            
            
            
            
            
            
            
            
