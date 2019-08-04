Introduction
============

explodeinstaller: ISO Extraction utility

This extraction utility has been writen to assist in the scripted
modification of Slackware install CDs, although it may be useful for
other distributions.

It differs from other scripts in that it allows editing of all files
including the ramdisk contents without being root, and without resorting
to FUSE or ISO mounting, it therefore works on a Mac.


Setup
=====

Install pycdlib, from github.  You require version 1.8, not released
at time of writing.  Obtain pycdlib direct from:
https://github.com/clalancette/pycdlib

Install the python modules in requirements[23].txt.
```
sudo python -m pip3 install -r requirements3.txt
```
should do the trick.

Compile the gen_init_cpio program by just typing 'make', and put it in
your path.  This is the same program found in the kernel sources at 
usr/gen_init_cpio.c, and is only included here to avoid the depency 
on the kernel sources.  This is only required for re-assembly, not exploding.

Finally, 
```
sudo python setup.py install
```
Will install the extension.


Exploding
=========

Usage is simple.  From Python:

```
import explodeinstaller
explodeinstaller.extract_all("slackware64-14.2-install-dvd.iso", "tmp_iso")
```

You will see that the contents of the ISO are written to the output
directory:

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
etc....
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
import explodeinstaller
explodeinstaller.assemble_all("tmp_iso", "slackware_mod.iso")
```

Any initrd directories will be re-packed into their respective positions in
the isofs directory heirarchy.  If for some reason you want to actually
change the location an initrd gets written to you'll need to edit the hidden
file .index in the top level of the exploded directory.  You'll see this is
a json file indicating meta-data that needs to be stored between execution
of the exploder and the assembler.  It also determines the compression to be
used when re-packing the initrds.


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
result in the same sized initrd file.
