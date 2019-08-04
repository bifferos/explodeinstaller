#!/usr/bin/env python

import os
import re
import sys
import pexpect

VM_NAME = "slack_test"


# Expect a dialog containing given text
def expect_dlg(p, txt):
    IN = "qq\x1b[0;7m\x0f"
    OUT = "\x1b[0;7m\x0eqq"
    p.expect_exact(IN + txt + OUT)

def expect_dlg_re(p, txt):
    IN = r"qq\x1b\[0;7m\x0f"
    OUT = r"\x1b\[0;7m\x0eqq"
    p.expect(IN + txt + OUT)


os.system("VBoxManage startvm %s" % VM_NAME)

p = pexpect.spawn("socat STDIO,rawer UNIX-CONNECT:/tmp/vbox,forever", timeout=120, logfile=sys.stdout)

p.expect("Default kernel will boot in")
p.expect("boot: ")
p.send("\r\n")

p.expect("Enter 1 to select a keyboard map: ")
p.send("\n")

p.expect("slackware login: ")
p.send("root\n")

prompt="root@slackware:/# "

p.expect(prompt)
p.send("echo start=2048 | sfdisk /dev/sda\n")
p.expect(prompt)

p.send("setup\n")


# Target partition
expect_dlg_re(p, r"Slackware Linux Setup \(version .{1,8}\)")
p.send("t\n")

p.interact(escape_character=None)

