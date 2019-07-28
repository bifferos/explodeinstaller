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

```
 ./explodeinstaller.py &lt;iso name&gt; &lt;output directory&gt;
```

You will see that the contents of the ISO are written to the output
directory.  Example:

```
./explodeinstaller.py /tmp/slackware64-14.2-install-dvd.iso tmp_iso
```

This creates a structure like this:

```bash
└── tmp_iso
    ├── _EFI_BOOT_initrd.img
    ├── _isolinux_initrd.img
    └── isofs
```

There will be one 'isofs' subdir and zero or more initrd
subdirs.  Extracted initrds are prefixed with an underscore '_'.  If 
you want to add files to the initrd you need to do two things:  
 - First you need to add the file to the relevant initrd directory.  
 - Then, you need to update the spec file.

Under the 'isofs' directory you will see that the initrd contents have been
replaced by a text file with a line per included  entry, for example:

```bash
bash-5.0$ head tmp_iso/isofs/isolinux/initrd.img 
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

This format is described in the gen_init_cpio help output.

Recreate your new file with:

```
./gen_init_cpio tmp_iso/isofs/isolinux/initrd.img > new_initrd.img
```
Now you can compress it, then copy it back over the original iso file
location at 'tmp_iso/isofs/isolinux/initrd.img' and you should be able
to recreate your install DVD.



