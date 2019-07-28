If you run the script ./auto_create_partition.sh providing an ISO as
argument the Slackware ISO will be patched to automatically create a
single partition spanning the entire disk immediately prior to login.
As a precaution, the partition will only be created if the MBR is in 
the zeroed state.

This is great for quick deploys to virtual machines and can
obviously be extended to do the complete install with some effort.

Only the legacy BIOS initrd is patched, you can adapt the patch script to do
the UEFI one.
