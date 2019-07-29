#!/usr/bin/env python

"""
Create a Slackware ISO with the console on the serial port.  Note that this is only for the install,
you still need to change inittab to get a terminal on first boot.

Here are some instructions that seem to work well for testing it:
https://www.gonwan.com/2014/04/07/setting-up-serial-console-on-virtualbox/
"""

import os
import argparse


def patch_isolinux_for_serial(root):
    file_to_change = os.path.join(root,"isofs/isolinux/isolinux.cfg")

    new_file = ["serial 0 115200\n"]
    for line in open(file_to_change).readlines():
        if line.strip().startswith('append'):
            line = line.rstrip() + " " + 'console=ttyS0,115200' + '\n'
        new_file.append(line)

    open(file_to_change, "wb").write("".join(new_file))
    print("Data written to %r" % file_to_change)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("iso", help="Original slackware ISO")
    args = parser.parse_args()
    temp_dir = "tmp_dir"
    os.system("../../explodeinstaller.py %s %s" % (args.iso, temp_dir))
    patch_isolinux_for_serial(temp_dir)
    out_file = os.path.join(temp_dir, "generated.iso")
    os.system("../../assembleinstaller.py %s %s" % (temp_dir, out_file))
    print("ISO has been generated at %s" % out_file)


if __name__ == "__main__":
    main()
