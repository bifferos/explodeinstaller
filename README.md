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


Exploding
=========

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

Modification
============

If you want to change files in the initrd, just go ahead and edit them.

If you want to add files to the initrd, you need to do two things:
 - First you need to add the file to the relevant initrd directory.  
 - Then, you need to update the spec file.

If you only want to add another directory, device, special file or link, 
then you only need to update the spec file.

You will see that each initrd directory is accompanied by a corresponding
.spec file, in the above example there would be one like this:

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

Obviously adding packages is just a matter of placing them in the isofs
directory.


Assembly
========

Once you've made any required changes to your set of files, you're ready to
re-assemble.  Run:

```
./assembleinstaller.py <exploded dir> <iso name>
```

Any initrd directories will be re-packed into their respective positions in
the isofs directory heirarchy.  If for some reason you want to actually
change the location an initrd gets written to you'll need to edit the hidden
file .index in the top level of the exploded directory.  You'll see this is
a json file indicating meta-data that needs to be stored between execution
of the exploder and the assembler.  It also determines the compression to be
used when re-packing.


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
