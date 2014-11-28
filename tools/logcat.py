import sys
from exception.testexception import TestException

def get_locat_file_name(monitor_thread_dict):
    # monitor_thread_dict 's format is defined in pytest
    # its data is like{monitor_thread:monitor_ele}
    for monitor in monitor_thread_dict.keys():
        monitor_ele = monitor_thread_dict[monitor]
        if monitor_ele.get('name').strip() == 'logcat':
            parameter_ele = monitor_ele.find('Parameter')
            file_name = ''
            if parameter_ele is not None:
                output_eles = parameter_ele.findall('output')
                if len(output_eles) == 0:
                    raise TestException("Error: <output object='log'></output> should exist in Monitor element with name logcat")
                output_log_exist_flag = False
                #check if <output object="log"></output> exists
                for output in output_eles:
                    if output.get('object') is not None and output.get('object').strip() == 'log':
                        output_log_exist_flag = True
                        output_text= output.text
                        if output_text is not None and output_text.strip() != '':
                            file_name = output_text
                        break
                if file_name == '':
                    file_name = 'step_' + step_id + '_logcat'
                return file_name
            else:
                raise TestException("Error: no Parameter element found in logcat monitor.")
    
def logcat_dec(logcat_file_path):
    try:
        rdict = {}
        decodeframecount = obtainValue(logcat_file_path, "decodeFrameCount")
        renderframecount = obtainValue(logcat_file_path, "renderFrameCount")
        dropframecount = obtainValue(logcat_file_path, "dropFrameCount")
        emptyframecount = obtainValue(logcat_file_path, "emptyFrameCount") 
        playbackDuration = obtainValue(logcat_file_path, "playbackDuration") 
#        decode_FPS = obtainValue(logText, "decode_FPS")
        render_FPS = obtainValue(logcat_file_path, "render_FPS")

        rdict.setdefault('decodeFrameCount', decodeframecount)
        rdict.setdefault('renderFrameCount', renderframecount)
        rdict.setdefault('dropFrameCount', dropframecount)
        rdict.setdefault('emptyFrameCount', emptyframecount)
#        rdict.setdefault('decode_FPS', decode_FPS)
        rdict.setdefault('render_FPS', render_FPS)
        rdict.setdefault('playbackDuration', playbackDuration)
                
        '''
        print "g_decodeframecount: " + g_decodeframecount
        print "g_renderframecount: " + g_renderframecount
        print "g_dropframecount: " + g_dropframecount
        print "g_emptyframecount: " + g_emptyframecount
        print "decode_FPS: " + decode_FPS
        print "render_FPS: " + render_FPS
        '''
        
        return rdict      
    except Exception, e:
        raise  TestException(e)
        
    
def obtainValue(logcat_file_path, key):
    value = ''
    locat_file = open(logcat_file_path)
    for line in locat_file:
        if line.find(key) != -1:
            comma_items = line.split(',')
            for item in comma_items:
                if item.find(key) != -1:
                    value = item.split('=')[1].strip()
                    if key.strip() == 'playbackDuration':
                        value = value.split('.')[0]
    return value
