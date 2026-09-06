# datastore2

## Purpose
Primary datastore for the Range Lab virtual machines.

This datastore was created on a dedicated virtual disk to provide ample storage for lab workloads and future expansion.

---
## Type
VMFS 6
## Capacity
224.00 GB
## Free Space
222.337 GB (2026-08-03)
___
## Located On
[[esxi01]]
## Physical Disk

- VMware Virtual Disk
- 224 GB

---

## Intended Use

- Virtual machine files
- Virtual disks (VMDKs)
- ISO images
- VM snapshots
- Templates

**This is the primary datastore for all Range Lab virtual machines.**

---

## Notes

A second 224 GB virtual disk was added to [[esxi01]] after discovering that the default datastore (`[[datastore1]]`) could not be expanded.

The new disk was initialized with the VMFS 6 filesystem and configured as `datastore2`. All future virtual machines—including vCenter, Windows Server, Linux, and other Range Lab workloads—will be stored on this datastore.

___


## Related

- [[esxi01]]
- [[datastore1]]