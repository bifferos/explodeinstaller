#!/bin/sh

# Ensure the tmp directory doesn't exist.
rm -rf tmp_dir

# Extract the ISO
../../explodeinstaller.py $1 tmp_dir

# Do the patching in Python.  There are many ways you can do this, of course.
./patch_init.py
 
# Re-make the ISO.
../../assembleinstaller.py tmp_dir generated.iso
