#!/usr/bin/env python

import os
import sys
import explodeinstaller

temp_dir = "tmp_dir"


shell_addition = r"""
# Snippit of shell code to inject into rc.S (or maybe somewhere else)
dd if=/dev/sda of=/tmp/mbr.bin bs=512 count=1
dd if=/dev/zero of=/tmp/zero.bin bs=512 count=1

if diff /tmp/zero.bin /tmp/mbr.bin
then
  echo "No MBR found, creating a single large partition for install"
  echo start=2048 | sfdisk /dev/sda
fi
""".split("\n")


# Ensure the tmp directory doesn't exist.
os.system("rm -rf %s" % temp_dir)


# Extract the ISO
explodeinstaller.extract_all(sys.argv[1], temp_dir)


file_to_change = os.path.join(temp_dir,"_isolinux_initrd.img/etc/rc.d/rc.S"


new_file = []
for line in open(file_to_change).readlines():
    if line.startswith('echo -n "slackware login: "'):
        print("Found marker, inserting new code")
        for nl in shell_addition:
            new_file.append(nl)
    new_file.append(line)

open(file_to_change, "wb").write("".join(new_file))
print("Data written to %r" % file_to_change)

 
# Re-make the ISO.
explodeinstaller.assemble_all(temp_dir, "generated.iso")

