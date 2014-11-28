#!/system/bin/bash
echo "insmod ko files start..."
insmod usbnet.ko
insmod asix.ko
echo "insmod ko files finished..."
netcfg eth0 dhcp
netcfg
setprop service.adb.tcp.port 5555
stop adbd
start adbd

