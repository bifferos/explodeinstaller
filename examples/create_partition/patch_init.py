#!/usr/bin/env python 

file_to_change = "tmp_dir/_isolinux_initrd.img/etc/rc.d/rc.S"
file_to_insert = "./create.sh"

new_file = []
for line in open(file_to_change).readlines():
    if line.startswith('echo -n "slackware login: "'):
        print("Found marker, inserting new code")
        for nl in open(file_to_insert).readlines():
            new_file.append(nl)
    new_file.append(line)

open(file_to_change, "wb").write("".join(new_file))
print("Data written to %r" % file_to_change)
