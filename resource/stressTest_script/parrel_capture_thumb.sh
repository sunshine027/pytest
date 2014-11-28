#!/bin/bash
#am start -n com.android.testcamera/.VideoCamera
adb -s $1 shell "am start -n com.android.camera/.VideoCamera"
sleep 2
i=1
while [ $i -le $2 ]
do
    echo $i
    sleep 1
    adb -s $1 shell "input keyevent 27 && mediaplayer --input_file $3Stress/1080p_h264_10s.3gp --mode thumb"
    sleep 10
    adb -s $1 shell "input keyevent 27"
    date
    i=$((i+1))
done
echo "Done!!!"

