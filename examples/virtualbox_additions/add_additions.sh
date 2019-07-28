#!/bin/sh

# Ensure the tmp directory doesn't exist.
rm -rf tmp_dir

# Extract the ISO
../../explodeinstaller.py $1 tmp_dir

# Assuming VirtualBox installed, copy the additions from the virtualbox ISO
# into the 'extra' directory
iso-read -e VBoxLinuxAdditions.run -i /opt/VirtualBox/additions/VBoxGuestAdditions.iso \
	-o tmp_dir/isofs/extra/VBoxLinuxAdditions.run
 
# Re-make the ISO.  Since we didn't change the initrds, can skip their recreation.
../../assembleinstaller.py --skiprd tmp_dir generated.iso
