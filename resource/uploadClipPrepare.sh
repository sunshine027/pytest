#!/usr/bin/expect

set timeout 20
spawn ssh shihui@172.16.120.166
expect "*password*"
send "shihui\r"

expect "*#"
send "sudo -i\r"
expect "*password*"
send "shihui\r"

expect "*#"
send "cd /var/ftp\r"
expect "*#"
send "mkdir RapidRunner_ResultClip/"
expect "*#"
send "chmod 777 RapidRunner_ResultClip"

expect "*#"
send "exit\r"
sleep 1
expect "*#"

exit
 

