Introduction
============

explodeinstaller: ISO Extraction utility

This extraction utility has been writen to assist in the automated
re-creation of Slackware install CDs, although it may be useful for
other distributions.

It differs from other scripts in that it allows editing of all files
including the ramdisk contents without being root, and without resorting
to FUSE or ISO mounting.  It therefore stands some chance of working
on a Mac.


Setup
=====

Install the python modules in requirements.txt.  
`sudo pip install -r requirements.txt` should do the trick.

Compile the gen_init_cpio program by just typing 'make'.  This is the
same program found in the kernel sources at usr/gen_init_cpio.c, and
is only included here to avoid the depency on the kernel sources.
This is only required for re-assembly, not extraction.


Usage
=====

Usage is simple.  Run as:

 ./explodeinstaller.py <iso name> <output directory>

You will see that the contents of the ISO are written to the output
directory.  There will be one 'isofs' subdir and zero or more initrd
subdirs.  Extracted initrds are prefixed with an underscore '_'.  If 
you want to add files to the initrd you need to do two things:  
 - First you need to add the file to the relevant initrd directory.  
 - Then, you need to update the spec file.

Under the 'isofs' directory you will see that the initrd contents have been
replaced by a text file,  With an entry per file or device node in the initrd.
This format is described in the gen_init_cpio help output.


