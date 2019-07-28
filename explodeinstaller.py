#!/usr/bin/env python2

"""
Although this is partially working with Python 3, please use python2 for the time being.  The dependent
isoparser library doesn't seem to work properly.
"""

import os
import isoparser
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
INITRD_IMAGES = ["/EFI/BOOT/initrd.img","/isolinux/initrd.img"]


def extract_one_iso_file(iso_in, iso_parser, src, dest):
    local_path = dest + src
    try:
        iso_in.get_file_from_iso(local_path, rr_path=src)
    except pycdlib.pycdlibexception.PyCdlibInvalidInput as e:
        print(repr(str(e)))
        if str(e) == "Symlinks have no data associated with them":
            if os.path.exists(local_path):
                os.unlink(local_path)
            local_dir, local_link_name = os.path.split(local_path)
            src = src.split("/")[1:]
            record = iso_parser.record(*src)
            created = False
            for i in record.susp_entries:
                if i.signature == "SL":
                    print(i.path)
                    old_dir = os.getcwd()
                    os.chdir(local_dir)
                    print("Creating link", i.path, local_link_name)
                    os.symlink(i.path, local_link_name)
                    created = True
                    os.chdir(old_dir)
            if not created:
                raise ValueError("Found symlink, but can't find SUSP entry for target")
        elif str(e) == "Cannot write out a file without data":
            src = src.split("/")[1:]
            data = iso_parser.record(*src).content
            print("Alternative Extraction", local_path)
            open(local_path, "wb").write(data)
        else:
            raise ValueError("Unrecognised exception")


def walk_iso(iso_file, isofs_dir):
    """The main walking mechanism is the first level extractor, it just extracts the files
       and creates any links for iso filesystem
    """
    iso_in = pycdlib.PyCdlib()
    iso_in.open(iso_file)
    iso_parser = isoparser.parse(iso_file)
    iso_out = pycdlib.PyCdlib()
    iso_out.new(joliet=3)
    os.mkdir(isofs_dir)
    for path, dirs, files in iso_in.walk(rr_path="/"):
        for dirname in dirs:
            dst = isofs_dir + os.path.join(path, dirname)
            print("creating  dir %r" % dst)
            os.mkdir(dst)
        for file in files:
            src = os.path.join(path, file)
            extract_one_iso_file(iso_in, iso_parser, src, isofs_dir)


def get_file_opener(path):
    p = Popen(["file", path], stdout=PIPE)
    out, err = p.communicate("")
    if out.find("gzip") != -1:
        return gzip.open
    elif out.find("XZ compressed data") != -1:
        return lzma.open
    raise ValueError("Unexpected compression type")


def walk_initrd(initrd_path, initrd_dir):
    opener = get_file_opener(initrd_path)

    print("Extracting initrd at %r" % initrd_path)
    fp = opener(initrd_path)
    fp_out = six.StringIO()
    ext_init_cpio.g_inodes = {}
    while ext_init_cpio.process_entry(fp, initrd_dir, fp_out):
        pass
    # Replace the original initrd file with the spec
    open(initrd_path, "wb").write(fp_out.getvalue())


def extract_all(iso_file, out_dir):
    if os.path.exists(out_dir):
        raise ValueError("Output directory %r exists" % out_dir)
    os.mkdir(out_dir)
    iso_explode_path = "isofs"
    isofs_dir = os.path.join(out_dir, iso_explode_path)
    walk_iso(iso_file, isofs_dir)
    index = {"ISO": iso_explode_path}

    for image in INITRD_IMAGES:
        initrd_path = isofs_dir + image
        if not os.path.exists(initrd_path):
            print("Skipping initrd path %r, doesn't exist" % initrd_path)
            continue
        escaped = image.replace("/", "_")
        index[escaped] = image
        initrd_dir = os.path.join(out_dir, "%s" % escaped)
        os.mkdir(initrd_dir)
        walk_initrd(initrd_path, initrd_dir)

    # Finally, make a dictionary to find everything.
    print("Writing index")
    open(os.path.join(out_dir, ".index"),"wb").write(json.dumps(index))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("iso", help="ISO file to extract")
    parser.add_argument("dir", help="output directory to dump files into (mustn't exist)")
    args = parser.parse_args()
    extract_all(args.iso, args.dir)


if __name__ == "__main__":
    main()

