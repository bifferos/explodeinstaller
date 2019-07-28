Introduction
============

explodeinstaller: ISO Extraction utility

This extraction utility has been writen to assist in the scripted
modification of Slackware install CDs, although it may be useful for
other distributions.

It differs from other scripts in that it allows editing of all files
including the ramdisk contents without being root, and without resorting
to FUSE or ISO mounting.  It therefore stands some chance of working
on a Mac (untested).


Setup
=====

You require Python2 for this.  The code is mostly compatible with Python3
patches welcome for a Python3 port.

Install the python modules in requirements.txt.  
`sudo pip install -r requirements.txt` should do the trick.

Compile the gen_init_cpio program by just typing 'make'.  This is the
same program found in the kernel sources at usr/gen_init_cpio.c, and
is only included here to avoid the depency on the kernel sources.
This is only required for re-assembly, not extraction.


Usage
=====

Usage is simple.  Run as:

```
 ./explodeinstaller.py <iso name> <output directory>
```

You will see that the contents of the ISO are written to the output
directory.  Example:

```
./explodeinstaller.py /tmp/slackware64-14.2-install-dvd.iso tmp_iso
```

This creates a directory structure like this:

```bash
└── tmp_iso
    ├── _EFI_BOOT_initrd.img/
    ├── _EFI_BOOT_initrd.img.spec
    ├── _isolinux_initrd.img/
    ├── _isolinux_initrd.img.spec
    └── isofs/
```

There will be one 'isofs' subdir and zero or more initrd
subdirs.  Extracted initrds are prefixed with an underscore '_'.  

If for some reason you don't find your initrd here, then you may need to
modify the explodeinstaller.py source to change the list of search 
locations for initrd.  Most of the time the initrd will be somewhere like
/isolinux/initrd.img.

If you want to change scripts in the initrd, just go ahead and edit them.

If you want to add files to the initrd, you need to do two things:
 - First you need to add the file to the relevant initrd directory.  
 - Then, you need to update the spec file.

You will see that each initrd directory is accompanied by a .spec file,
in the above example there would be one like this:

```bash
bash-5.0$ head tmp_iso/_isolinux_initrd.img.spec 
slink cdrom /var/log/mount 777 0 0
dir bin 755 0 0
slink bin/rm busybox 777 0 0
file bin/gzip tmp_iso/_isolinux_initrd.img/bin/gzip 755 0 0
slink bin/logname busybox 777 0 0
file bin/uuidgen tmp_iso/_isolinux_initrd.img/bin/uuidgen 755 0 0
slink bin/pstree busybox 777 0 0
file bin/tar-1.13 tmp_iso/_isolinux_initrd.img/bin/tar-1.13 755 0 0
file bin/busybox tmp_iso/_isolinux_initrd.img/bin/busybox 755 0 0
slink bin/watch busybox 777 0 0
```

This format is described in the gen_init_cpio help output, so execute
that program without arguments to see the options.


Assumptions
===========

It's assumed your ISO image uses Rockridge extensions for the filesystem. 
They've been so common on ISO images that explodeinstaller doesn't even 
check to see if the image has them.  There are sure to be errors when reading 
UDF or non-RR images.


Caveats
=======

The two most likely forms of initrd compression have been catered for, 
gzip (slackware 14.2) and lz (current).  Other compression options would
have to be added to the source.  This won't be too hard.

Another thing about compression is that explodeinstaller doesn't figure 
out what options were used on the original ISO, so recompressing may not
result in the same sized file.

Two ISO reading libraries are used:  pycdlib and isoparser.  pycdlib is
quite fast but doesn't handle links or reading the boot image properly.
isoparser is slow, but seems to fare better.  So pycdlib does extraction of 
most of the files, and when it throws an exception isoparser takes over. 
This seems to be a good tradeoff, however if pycdlib gets 'fixed' then this
code may break.

Although the code is compatible with Python 3, the exploder doesn't seem to
work with it.  I'll continue to develop against six to leave the door open
for a Python port to python3 but don't intend to spend any time actually
getting it working when this meets my needs.  Patches welcome.
