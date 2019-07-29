#!/usr/bin/env python

"""
   Copyright (c) Bifferos (bifferos@gmail.com) 2019.
   Permission is given to use this code for any purpose.  Derived works must contain this copyright notice.
"""

import os
import pycdlib
import ext_init_cpio
from subprocess import Popen, PIPE
import argparse
try:
    import lzma
except ImportError:
    from backports import lzma
import gzip
import json
import six

# The location of any initrd images is specific to each distribution and bootloader.  Since these are simply
# compressed cpio archives it would be expensive to figure out where they are.  Easiest way to deal with them
# Is hard-code the locations.  This list can be exhaustive, if any are missing they'll be ignored.
INITRD_IMAGES = ["/EFI/BOOT/initrd.img", "/isolinux/initrd.img"]


def extract_one_iso_file(iso_in, src, dest):
    local_path = dest + src
    record = iso_in.get_record(rr_path=src)
    if record.is_file():
        if record.rock_ridge is not None and record.rock_ridge.is_symlink():
            local_dir, local_link_name = os.path.split(local_path)
            old_dir = os.getcwd()
            os.chdir(local_dir)
            src = record.rock_ridge.symlink_path()
            dst = local_link_name
            print("symlink: %s -> %s" % (dst, src))
            os.symlink(src, dst)
            os.chdir(old_dir)
        else:
            print("file: %s" % src)
            iso_in.get_file_from_iso(local_path, rr_path=src)


def walk_iso(iso_file, isofs_dir):
    """The main walking mechanism is the first level extractor, it just extracts the files
       and creates any links for iso filesystem
    """
    iso_in = pycdlib.PyCdlib()
    iso_in.open(iso_file)
    iso_out = pycdlib.PyCdlib()
    iso_out.new(joliet=3)
    os.mkdir(isofs_dir)
    for path, dirs, files in iso_in.walk(rr_path="/"):
        for dirname in dirs:
            dst = isofs_dir + os.path.join(path, dirname)
            print("dir %s" % dst)
            os.mkdir(dst)
        for filename in files:
            src = os.path.join(path, filename)
            extract_one_iso_file(iso_in, src, isofs_dir)


def get_file_opener(path):
    p = Popen(["file", path], stdout=PIPE)
    out, err = p.communicate("")
    if out.find(b"gzip") != -1:
        return gzip.open, "gzip"
    elif out.find(b"XZ compressed data") != -1:
        return lzma.open, "lzma"
    raise ValueError("Unexpected compression type")


def walk_initrd(initrd_path, initrd_dir):
    opener, type_str = get_file_opener(initrd_path)

    print("Extracting initrd at %r" % initrd_path)
    fp = opener(initrd_path)
    fp_out = six.BytesIO()
    ext_init_cpio.g_inodes = {}
    while ext_init_cpio.process_entry(fp, initrd_dir, fp_out):
        pass
    # Replace the original initrd file with the spec
    spec = initrd_dir+".spec"
    open(spec, "wb").write(fp_out.getvalue())
    return spec, type_str


def extract_all(iso_file, out_dir):
    if os.path.exists(out_dir):
        raise ValueError("Output directory %r exists" % out_dir)
    os.mkdir(out_dir)
    iso_explode_path = "isofs"
    isofs_dir = os.path.join(out_dir, iso_explode_path)
    walk_iso(iso_file, isofs_dir)
    index = {"ISO": iso_explode_path}

    initrds = {}

    for image in INITRD_IMAGES:
        initrd_path = isofs_dir + image
        if not os.path.exists(initrd_path):
            print("Skipping initrd path %r, doesn't exist" % initrd_path)
            continue
        escaped = image.replace("/", "_")
        initrd_dir = os.path.join(out_dir, "%s" % escaped)
        os.mkdir(initrd_dir)
        spec, type_str = walk_initrd(initrd_path, initrd_dir)
        initrds[escaped] = (image, spec, type_str)

    index["initrds"] = initrds
    # Finally, make a dictionary to find everything.
    index_path = os.path.join(out_dir, ".index")
    print("Writing index to %s" % index_path)
    with open(index_path, "w") as fp:
        json.dump(index, fp)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("iso", help="ISO file to extract")
    parser.add_argument("dir", help="output directory to dump files into (mustn't exist)")
    args = parser.parse_args()
    extract_all(args.iso, args.dir)


if __name__ == "__main__":
    main()
