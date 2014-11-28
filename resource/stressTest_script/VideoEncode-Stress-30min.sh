#!/bin/bash
if [ "$#" -lt 2 ]
then
    echo "Usage: ./VideoEncode-Stress-30min.sh  serialnumber encode_count"
    exit 1
fi
adb -s $1 shell "am start -n com.android.camera/.VideoCamera"
sleep 2
i=1
while [ $i -le $2 ]
do
    echo $i
    sleep 1
    adb -s $1 shell "input keyevent 27"
    sleep 1770
    adb -s $1 shell "input keyevent 27"
    i=$((i+1))
#    rm /sdcard/DCIM/Camera -rf
    sleep 5
done
echo "Done!!!"

