
# Snipit of shell code to inject into rc.S (or maybe somewhere else)
dd if=/dev/sda of=/tmp/mbr.bin bs=512 count=1
dd if=/dev/zero of=/tmp/zero.bin bs=512 count=1

if diff /tmp/zero.bin /tmp/mbr.bin
then
  echo "No MBR found, creating a single large partition for install"
  echo start=2048 | sfdisk /dev/sda
fi

