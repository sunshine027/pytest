#!/bin/bash

if [ "$#" -ne 2 ]; then
   echo "Usage: ./rotation_host.sh <device_id> <orientation>"
   echo "Details:"
   echo "        orientation: 0/1/2"
   exit 1
fi


EVENT=`adb -s $1 shell "cat /proc/bus/input/devices" | grep "Name=\"accel\"" -A 4 | grep "Handlers" | awk -F= '{print $NF}'`
E=`echo $EVENT|cut -c1-6`
GETEVENT="/dev/input/$E"

i=5

case $2 in
     0 )
        while [ $i -gt 1 ];
        do
          adb -s $1 shell sendevent $GETEVENT 0002 0000 32
          adb -s $1 shell sendevent $GETEVENT 0002 0001 4294966304
          adb -s $1 shell sendevent $GETEVENT 0002 0002 64
          adb -s $1 shell sendevent $GETEVENT 0000 0000 0
          i=`expr $i - 1`
        done
     ;;
     1 )
        while [ $i -gt 1 ];
        do
          adb -s $1 shell sendevent $GETEVENT 0002 0000 4294966272
          adb -s $1 shell sendevent $GETEVENT 0002 0001 32
          adb -s $1 shell sendevent $GETEVENT 0002 0002 4294967200
          adb -s $1 shell sendevent $GETEVENT 0000 0000 0
          i=`expr $i - 1`
        done
     ;;
     2 )
        while [ $i -gt 1 ];
        do
          adb -s $1 shell sendevent $GETEVENT 0002 0000 1040
          adb -s $1 shell sendevent $GETEVENT 0002 0001 4294967280
          adb -s $1 shell sendevent $GETEVENT 0002 0002 96
          adb -s $1 shell sendevent $GETEVENT 0000 0000 0
          i=`expr $i - 1`
        done
     ;;
     * )
        exit 0
     ;;
esac
