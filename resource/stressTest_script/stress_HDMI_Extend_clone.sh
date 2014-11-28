#!/bin/bash

time=1
if [ $# -ge 1 ]

then
    for time in {1..2000}
    do   
        adb -s $1 shell "am start -a android.intent.action.VIEW -d file://$3Stress/1080p_h264_10s.3gp -t video/*"
        echo $time
        adb -s $1 shell date
        time=`expr $time + 1`
        sleep 15
    done
else
     echo "wrong parameters."
fi
