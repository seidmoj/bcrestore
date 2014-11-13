cat > /usr/lib/udev/rules.d/50-automount-usb.rules << FFF

KERNEL!="sd[a-z][0-9]", GOTO="media_by_label_auto_mount_end"  
IMPORT{program}="/sbin/blkid -o udev -p %N"  
ENV{ID_FS_LABEL}!="", ENV{dir_name}="%E{ID_FS_LABEL}"  
ENV{ID_FS_LABEL}=="", ENV{dir_name}="usbhd-%k"  
ACTION=="add", ENV{mount_options}="relatime"  
ACTION=="add", ENV{ID_FS_TYPE}=="vfat|ntfs", ENV{mount_options}="$env{mount_options},utf8,gid=100,umask=002"  
ACTION=="add", RUN+="/bin/mkdir -p /media/%E{dir_name}", RUN+="/bin/mount  /dev/%k /media/%E{dir_name}"  
ACTION=="remove", ENV{dir_name}!="", RUN+="/bin/umount -l /media/%E{dir_name}", RUN+="/bin/rmdir /media/%E{dir_name}"  
LABEL="media_by_label_auto_mount_end"

FFF

systemctl restart systemd-udevd.service
