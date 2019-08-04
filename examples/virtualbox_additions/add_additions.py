#!/usr/bin/env python

import os
import sys
import explodeinstaller

temp_dir = "tmp_dir"

# Ensure the tmp directory doesn't exist.
os.system("rm -rf %s" % temp_dir)

# Extract the ISO
explodeinstaller.extract_all(sys.argv[1], temp_dir)

# Assuming VirtualBox installed, copy the additions from the virtualbox ISO
# into the 'extra' directory
os.system("iso-read -e VBoxLinuxAdditions.run -i /opt/VirtualBox/additions/VBoxGuestAdditions.iso "
	"-o tmp_dir/isofs/extra/VBoxLinuxAdditions.run")
 
# Re-make the ISO.
explodeinstaller.assemble_all(temp_dir, "generated.iso")
