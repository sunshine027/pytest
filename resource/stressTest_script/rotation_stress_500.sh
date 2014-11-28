#!/bin/bash

if [ "$#" -lt 1 ]
then
    echo "Usage: ./rotation_stress_500.sh <device_number>"
    exit 1
fi
PWD=`pwd`
if [ -f $PWD/output.log ]
then
    rm -rf output.log
fi
j=1
time=1

while [ $time -le 240 ]
do
    adb -s $1 shell "am start -a android.intent.action.VIEW -d file://$3Stress/kauai_1080p_MPEG4_AVC_H.264_AAC_new.mp4 -t video/*"
    if [ $? -ne 0 ]
    then    
        echo "exit unexpectly,am start failed."
        exit 1
    fi
    while [ "$j" -le 45 ]
    do
        source ./resource/stressTest_script/rotate_host.sh $1 1
        source ./resource/stressTest_script/rotate_host.sh $1 2
        source ./resource/stressTest_script/rotate_host.sh $1 0
        sleep 1
        j=`expr $j + 1`
    done
    
    j=1
    echo $time
    sleep 60
    date
    time=`expr $time + 1`
done

