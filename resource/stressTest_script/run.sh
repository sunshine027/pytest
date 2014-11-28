#!/system/bin/sh
BIN_DIR=/system/LibVA-API_Test/ 

if [ $# -ne 1 ]; then
	echo "$0 <case name>"
	exit
fi

echo " "
echo "-= $(basename $exe) =-"
$BIN_DIR$1 && res='pass' || res=$?
echo "$(basename $1):$res"
echo "-----------------------------------------------------"
