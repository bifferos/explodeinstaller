#!/bin/bash

# Adapt a Slackware ISO so it boots over serial port
# And then create a VirtualBox VM to run the ISO.

ISO_PATH=/tmp/slackware64-14.2-install-dvd.iso
VM_NAME=slack_test
VBOX_SOCKET=/tmp/vbox

rm -rf tmp_dir

# Extract the ISO
../../explodeinstaller.py $ISO_PATH  tmp_dir

CFG=tmp_dir/isofs/isolinux/isolinux.cfg

mv $CFG $CFG.tmp
echo "serial 0 115200" > $CFG
cat $CFG.tmp | sed "s/SLACK_KERNEL=huge.s/SLACK_KERNEL=huge.s console=ttyS0/" >> $CFG
rm $CFG.tmp

../../assembleinstaller.py --skiprd tmp_dir generated.iso

VBoxManage createvm --name $VM_NAME --register
VBoxManage modifyvm $VM_NAME --memory 512
VBoxManage modifyvm $VM_NAME --nic1 nat
VBoxManage modifyvm $VM_NAME --boot1 dvd
VBoxManage storagectl $VM_NAME --name IDE --add ide
VBoxManage createmedium disk --filename disk.vdi --size 20480
VBoxManage storageattach $VM_NAME --storagectl IDE --port 0 --device 0 --type hdd --medium disk.vdi
VBoxManage storageattach $VM_NAME --storagectl IDE --port 1 --device 0 --type dvddrive --medium generated.iso
VBoxManage modifyvm $VM_NAME --uart1 0x3f8 4 --uartmode1 server $VBOX_SOCKET

