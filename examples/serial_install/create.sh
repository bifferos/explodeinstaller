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

../../assembleinstaller.py tmp_dir generated.iso


