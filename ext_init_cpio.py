#!/usr/bin/env python2

"""
   Copyright (c) Bifferos (bifferos@gmail.com) 2019.
   Permission is given to use this code for any purpose.  Derived works must contain this copyright notice.
"""


import os
import argparse
import sys


TYPE_SOCKET = 0o0140000
TYPE_SLINK = 0o0120000
TYPE_FILE = 0o0100000
TYPE_NODE_BLOCK = 0o0060000
TYPE_DIR = 0o0040000
TYPE_NODE_CHAR = 0o0020000
TYPE_PIPE = 0o0010000


def read8(fp):
    return int(fp.read(8), 16)


def padding(fp):
    while fp.tell() & 3:
        fp.read(1)


g_inodes = {}


def process_entry(fp, out_dir, fp_out):
    if fp.read(6) != "070701":
        raise ValueError("Only 'new' CPIO format is accepted")
    ino = read8(fp)
    cpio_mode = read8(fp)
    uid = read8(fp)
    gid = read8(fp)
    nlink = read8(fp)
    mtime = read8(fp)
    filesize = read8(fp)
    devmajor = read8(fp)
    devminor = read8(fp)
    rdevmajor = read8(fp)
    rdevminor = read8(fp)
    namesize = read8(fp) - 1
    check = read8(fp)

    # read name
    name = fp.read(namesize)
    # terminator
    fp.read(1)

    if name == "TRAILER!!!":
        return False
    padding(fp)

    if name == ".":
        return True

    # Now the file, if there is one.
    file_data = fp.read(filesize)
    padding(fp)

    entry = 0o0170000 & cpio_mode
    mode = cpio_mode & 0o7777

    if entry == TYPE_SOCKET:
        fp_out.write("sock %s %o %d %d\n" % (name, mode, uid, gid))
    elif entry == TYPE_SLINK:
        fp_out.write("slink %s %s %o %d %d\n" % (name, file_data, mode, uid, gid))
    elif entry == TYPE_FILE:
        hard_link = False
        if ino in g_inodes:
            hard_link = True
            sys.stderr.write("Existing name: %r\n" % g_inodes[ino])
            sys.stderr.write("New name: %r\n" % name)
            raise ValueError("Can't deal with hard links, sorry")
        g_inodes[ino] = name
        path = os.path.join(out_dir, name)
        dir_name = os.path.dirname(path)
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        fp_out.write("file %s %s %o %d %d\n" % (name, path, mode, uid, gid))
        if hard_link:
            sys.stderr.write("Possible hard link:")
        open(path, "wb").write(file_data)
        os.utime(path, (mtime, mtime))
    elif entry == TYPE_NODE_BLOCK:
        fp_out.write("nod %s %o %d %d b %d %d\n" % (name, mode, uid, gid, rdevmajor, rdevminor))
    elif entry == TYPE_DIR:
        fp_out.write("dir %s %o %d %d\n" % (name, mode, uid, gid))
    elif entry == TYPE_NODE_CHAR:
        fp_out.write("nod %s %o %d %d c %d %d\n" % (name, mode, uid, gid, rdevmajor, rdevminor))
    elif entry == TYPE_PIPE:
        fp_out.write("dir %s %o %d %d\n" % (name, mode, uid, gid))
    else:
        raise ValueError("Invalid type")

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cpio", help="cpio file to read from")
    parser.add_argument("dir", help="output directory to dump files into")
    args = parser.parse_args()
    fp = open(args.cpio, "rb")
    while process_entry(fp, args.dir, sys.stdout):
        pass


if __name__ == "__main__":
    main()
