Test on ESXi 5.1 and 5.5

1. Install dependancies:

(RHEL/CentOS)
yum install python-paramiko

(Debian/Ubuntu)
apt-get install paramiko

2. Install script:

Copy to /usr/sbin/fence_esxi 

chmod +x /usr/sbin/fence_esxi 

3. Update cluster.conf

```
<code>
<fencedevices>
<fencedevice agent="fence_esxi" ipaddr="esx.FQDN.com" login="root" name="esx" passwd="YOURPASSWORDHERE" delay="60" />
</fencedevices>
</code>
```
