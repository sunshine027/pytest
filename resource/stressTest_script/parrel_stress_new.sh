#!/bin/bash
i=1
while [ $i -le $2 ]
do
	echo $i
	adb -s $1 shell "am start -a android.intent.action.VIEW -d file://$3Stress/h264_1080p_3s.3gp -t video/* && mediaplayer --input_file $3Stress/1080p_h264_10s.3gp --mode thumb"
	sleep 20
	i=$((i+1))
done
echo "Done!!"
