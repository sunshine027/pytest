#!/usr/bin/expect

set timeout 20
set path [lindex $argv 0]
spawn scp -r $path shihui@172.16.120.166:/var/ftp/RapidRunner_ResultClip/
expect "*password*"
send "shihui\r"
expect "*#"
exit
