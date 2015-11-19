#!/usr/bin/python
 
import paramiko
import sys
import time
import datetime
import re
sys.path.append("/usr/share/fence")
from fencing import *
 
device_opt = [  "help", "version", "agent", "quiet", "verbose", "debug", "action", "ipaddr", "login", "passwd", "passwd_script", "ssl", "port", "uuid", "separator", "ipport", "power_timeout", "shell_timeout", "login_timeout", "power_wait" ]
 
options = check_input(device_opt, process_input(device_opt))
 
f = open("/var/log/cluster/fence_esxi.log","w+")
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
f.write(st + " starting fencing.\n")
f.write("--plug " + options["--plug"] + "\n")
f.write("--ip " + options["--ip"] + "\n")
f.write("--username " + options["--username"] + "\n")
f.write("--password " + options["--password"] + "\n")
 
client = paramiko.SSHClient()
client.load_system_host_keys()
client.connect(options["--ip"],username=options["--username"],password=options["--password"])
 
command="esxcli vm process list | grep ^" + options["--plug"]  + " -A 1 | tail -n 1 | sed \'s/  */ /g\' | cut -d \" \" -f 4"
 
f.write("Cmd: " + command + "\n")
 
stdin, stdout, stderr = client.exec_command(command)
while not stdout.channel.exit_status_ready():
        f.write("Waiting for command to finish... \n")
        time.sleep(2)
 
wwid = stdout.read()
f.write("wwid: " + wwid + "\n")
 
if len(wwid) < 2:
    f.write("VM not found or alread offline \n")
    client.close()
    sys.exit(1)
 
f.write("VM found \n")
command="esxcli vm process kill --type=soft --world-id=" + wwid
f.write("Cmd: " + command + "\n")
 
stdin, stdout, stderr = client.exec_command(command)
while not stdout.channel.exit_status_ready():
        f.write("Waiting for command to finish... \n")
        time.sleep(2)
 
#Give the VM some time to shut down gracefully
time.sleep(30)
f.write("Waited 30 seconds \n")
 
command="vm-support -V | grep centos | cut -d \"(\" -f 2 | cut -d \")\" -f 1"
f.write("Cmd: " + command + "\n")
 
stdin, stdout, stderr = client.exec_command(command)
while not stdout.channel.exit_status_ready():
        f.write("Waiting for command to finish... \n")
        time.sleep(2)
 
status = stdout.read()
f.write("VM Status: " + status + "\n")
sregex = re.compile('Running')
 
if sregex.search(status):
    f.write("VM still running, hard kill required \n")
    command="esxcli vm process kill --type=hard --world-id=" + wwid
    f.write("Cmd: " + command + "\n")
    stdin, stdout, stderr = client.exec_command(command)
    while not stdout.channel.exit_status_ready():
            f.write("Waiting for command to finish... \n")
            time.sleep(2)
 
    time.sleep(30)
else:
    f.write("VM successfully soft killed \n")
 
#Get VM info while powered off
command="vim-cmd vmsvc/getallvms | grep " + options["--plug"] + " | sed 's/  */ /g' | cut -d \" \" -f 1"
f.write("Cmd: " + command + "\n")
stdin, stdout, stderr = client.exec_command(command)
while not stdout.channel.exit_status_ready():
        f.write("Waiting for command to finish... \n")
        time.sleep(2)
 
vmid = stdout.read()
 
#Start VM back up
command="vim-cmd vmsvc/power.on " + vmid
f.write("Cmd: " + command + "\n")
stdin, stdout, stderr = client.exec_command(command)
 
while not stdout.channel.exit_status_ready():
    f.write("Waiting for command to finish... \n")
    time.sleep(2)
 
f.write("fence_esxi exiting...")
f.close()
client.close()
sys.exit(0)
