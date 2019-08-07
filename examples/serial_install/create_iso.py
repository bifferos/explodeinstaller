#!/usr/bin/env python

import os
import explodeinstaller

# Adapt a Slackware ISO so it boots over serial port
# And then create a VirtualBox VM to run the ISO.

ISO_PATH="/tmp/slackware64-14.2-install-dvd.iso"
VM_NAME="slack_test"
VBOX_SOCKET="/tmp/vbox"
temp_dir="tmp_dir"

os.system("rm -rf %s" % temp_dir)

# Extract the ISO
explodeinstaller.extract_all(ISO_PATH, temp_dir)

CFG="tmp_dir/isofs/isolinux/isolinux.cfg"

data = b"serial 0 115200\n" + open(CFG, "rb").read()
data = data.replace("SLACK_KERNEL=huge.s", "SLACK_KERNEL=huge.s console=ttyS0")

open(CFG, "wb").write(data)

explodeinstaller.assemble_all(temp_dir, "generated.iso")


