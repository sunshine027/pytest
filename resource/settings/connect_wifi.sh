#!/bin/bash 
adb -s $1 root
adb -s $1 remount
sleep 1
adb -s $1 shell  svc wifi disable  
sleep 2
adb -s $1 shell  svc wifi enable 
sleep 2
adb -s $1 shell input keyevent 3
sleep 2
adb -s $1 shell input keyevent 82
sleep 2

adb -s $1 shell sendevent /dev/input/event0  0003 0057 00000017
adb -s $1 shell sendevent /dev/input/event0  0003 0053 00000020
adb -s $1 shell sendevent /dev/input/event0  0003 0054 00000757
adb -s $1 shell sendevent /dev/input/event0  0000 0000 00000000
adb -s $1 shell sendevent /dev/input/event0  0003 0057 4294967295
adb -s $1 shell sendevent /dev/input/event0  0000 0000 00000000
sleep 1
adb -s $1 shell sendevent /dev/input/event0 0003 0057 00000153
adb -s $1 shell sendevent /dev/input/event0 0003 0053 00000704
adb -s $1 shell sendevent /dev/input/event0 0003 0054 00000279
adb -s $1 shell sendevent /dev/input/event0 0000 0000 00000000
adb -s $1 shell sendevent /dev/input/event0 0003 0057 4294967295
adb -s $1 shell sendevent /dev/input/event0 0000 0000 00000000
sleep 1

adb -s $1 shell sendevent /dev/input/event0 0003 0057 00000154
adb -s $1 shell sendevent /dev/input/event0 0003 0053 00000917
adb -s $1 shell sendevent /dev/input/event0 0003 0054 00001011
adb -s $1 shell sendevent /dev/input/event0 0000 0000 00000000
adb -s $1 shell sendevent /dev/input/event0 0003 0057 4294967295
adb -s $1 shell sendevent /dev/input/event0 0000 0000 00000000
sleep 1
adb -s $1 shell input text 9L02

adb -s $1 shell sendevent /dev/input/event0 0003 0057 00000155
adb -s $1 shell sendevent /dev/input/event0 0003 0053 00000305
adb -s $1 shell sendevent /dev/input/event0 0003 0054 00000412
adb -s $1 shell sendevent /dev/input/event0 0000 0000 00000000
adb -s $1 shell sendevent /dev/input/event0 0003 0057 4294967295
adb -s $1 shell sendevent /dev/input/event0 0000 0000 00000000
sleep 1

adb -s $1 shell sendevent /dev/input/event0 0003 0057 00000156
adb -s $1 shell sendevent /dev/input/event0 0003 0053 00000692
adb -s $1 shell sendevent /dev/input/event0 0003 0054 00000367
adb -s $1 shell sendevent /dev/input/event0 0000 0000 00000000
adb -s $1 shell sendevent /dev/input/event0 0003 0057 4294967295
adb -s $1 shell sendevent /dev/input/event0 0000 0000 00000000
sleep 1

adb -s $1 shell sendevent /dev/input/event0 0003 0057 00000157
adb -s $1 shell sendevent /dev/input/event0 0003 0053 00000299
adb -s $1 shell sendevent /dev/input/event0 0003 0054 00000361
adb -s $1 shell sendevent /dev/input/event0 0000 0000 00000000
adb -s $1 shell sendevent /dev/input/event0 0003 0057 4294967295
adb -s $1 shell sendevent /dev/input/event0 0000 0000 00000000
sleep 1
adb -s $1 shell input text intel

adb -s $1 shell sendevent /dev/input/event0 0003 0057 00000158
adb -s $1 shell sendevent /dev/input/event0 0003 0053 00000749
adb -s $1 shell sendevent /dev/input/event0 0003 0054 00000976
adb -s $1 shell sendevent /dev/input/event0 0000 0000 00000000
adb -s $1 shell sendevent /dev/input/event0 0003 0057 4294967295
adb -s $1 shell sendevent /dev/input/event0 0000 0000 00000000
sleep 1

adb -s $1 shell sendevent /dev/input/event0 0003 0057 00000159
adb -s $1 shell sendevent /dev/input/event0 0003 0053 00000063
adb -s $1 shell sendevent /dev/input/event0 0003 0054 00000715
adb -s $1 shell sendevent /dev/input/event0 0000 0000 00000000
adb -s $1 shell sendevent /dev/input/event0 0003 0057 4294967295
adb -s $1 shell sendevent /dev/input/event0 0000 0000 00000000
sleep 10
adb -s $1 shell input keyevent 3



