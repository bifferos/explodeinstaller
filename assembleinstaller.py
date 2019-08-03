#!/usr/bin/env python

"""
   Copyright (c) Bifferos (bifferos@gmail.com) 2019.
   Permission is given to use this code for any purpose.  Derived works must contain this copyright notice.
"""

import os
import sys
import json
import six
import argparse
import datetime
from subprocess import Popen, PIPE
try:
    import lzma
except ImportError:
    from backports import lzma
import gzip


def make_iso_fs(file_path, iso_name):
    iso_rel = os.path.join("..", "..", iso_name)
    command = [
        'mkisofs', '-o', iso_rel, '-R', '-J', '-V', 'explode installer',
        '-hide-rr-moved', '-hide-joliet-trans-tbl',
        '-v', '-d', '-N', '-no-emul-boot', '-boot-load-size', '4', '-boot-info-table',
        '-b', 'isolinux/isolinux.bin',
        '-c', 'isolinux/isolinux.boot',
        '-sort', 'isolinux/iso.sort',
        '-preparer', "assemble installer",
        '-publisher', "assemble installer",
        '-A', "Slackware",
        '-eltorito-alt-boot', '-no-emul-boot', '-eltorito-platform', '0xEF', '-eltorito-boot',
        'isolinux/efiboot.img',
        '.']
    print(" ".join(command))
    p = Popen(command, shell=False, cwd=file_path)
    p.communicate("")


def most_recent(path):
    """Most recent file in a path"""
    latest = 0
    for root, dirs, names in os.walk(path):
        latest = max([os.stat(os.path.join(root, name)).st_mtime for name in names]+[latest])
    return latest


def get_file_opener(name, output):
    if name == "gzip":
        return gzip.open(output, "wb")
    if name == "lzma":
        return lzma.open(output, "wb", check=lzma.CHECK_CRC32)
    raise ValueError("Unexpected compression type")


def gen_init_cpio(spec, output, type_str):
    p = Popen([os.path.join(sys.path[0], "gen_init_cpio"), spec], stdout=PIPE)
    data = p.communicate("")[0]
    fp = get_file_opener(type_str, output)
    fp.write(data)
    fp.close()
    print("Written file %r with %r compression" % (output, type_str))


def assemble_all(dir_path, iso_name):
    if not os.path.isdir(dir_path):
        raise ValueError("dir path doesn't exist")
    meta = json.loads(open(os.path.join(dir_path, ".index"), "rb").read())
    isofs_path = os.path.join(dir_path, meta["ISO"])

    for escaped, actual in six.iteritems(meta["initrds"]):
        output_path = isofs_path + actual[0]
        original_time = os.stat(output_path).st_mtime
        print("Initrd date: %s" % datetime.datetime.fromtimestamp(original_time))
        extracted_time = most_recent(os.path.join(dir_path, escaped))
        spec_time = os.stat(actual[1]).st_mtime
        print("Spec date: %s" % datetime.datetime.fromtimestamp(spec_time))
        latest_time = max(spec_time, extracted_time)
        print("Latest content date: %s" % datetime.datetime.fromtimestamp(extracted_time))
        if latest_time > original_time:
            gen_init_cpio(actual[1], output_path, actual[2])
        else:
            print("Skipping regeneration of initrd, it's hasn't been modified.")

    make_iso_fs(isofs_path, iso_name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="directory created by explodeinstaller.")
    parser.add_argument("iso", help="iso image to create")
    args = parser.parse_args()
    assemble_all(args.dir, args.iso)


if __name__ == "__main__":
    main()
