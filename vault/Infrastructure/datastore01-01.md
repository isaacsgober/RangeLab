# datastore01-01

## Purpose
Default ESXi system datastore created during installation.

This datastore primarily stores ESXi system files and should not be used for Range Lab virtual machines unless necessary.

---
## Type
VMFS 6
## Capacity
13.75 GB
## Free Space
12.34 GB  (2026-08-03)
___
## Located On
[[esxi01]]
## Physical Disk

- VMware Virtual Disk
- 142 GB

---

## Intended Use

- ESXi system files
- Boot-related data
- Small configuration files

**Do not use for regular virtual machines.**

---

## Notes

During the initial ESXi 9 installation, the installer allocated most of the 142 GB virtual disk to the **ESX-OSData** partition, leaving only a small VMFS datastore (~14 GB).

Because there was no unallocated disk space remaining, this datastore could not be expanded.

To provide sufficient storage for Range Lab virtual machines, a second virtual disk was added to [[esxi01]], and [[datastore01-02]] was created.

Renamed from `datastore1` on 2026-09-07 to match the `datastore<HH>-<NN>` form in [[Naming Convention]].

---

## Related

- [[esxi01]]
- [[datastore01-02]]
- [[Naming Convention]]