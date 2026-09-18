# datastore01-01

## Purpose

Primary datastore on [[esxi01]]. Holds every VM the host runs.

---

## Type

VMFS 6

## Capacity

400 GB (thin-provisioned virtual disk)

## Free Space

Record after Stage 5.

___

## Located On

[[esxi01]]

## Physical Disk

- esxi01 disk 2, PVSCSI
- 400 GB

---

## Intended Use

- [[vcenter01]]
- [[managed01]]

---

## Notes

2026-09-18:
	Created in the Host Client after install. It is the host's only datastore: the 128 GB boot disk is below the size at which ESXi 9 creates a local datastore. The pre-rebuild lab's `datastore01-01` was a 13.75 GB remainder on a 142 GB boot disk, unused; this name now belongs to the real datastore under the [[Naming Convention]] (first datastore on host 01).

---

## Related

- [[esxi01]]
- [[Naming Convention]]
- [[Build-Sequence]]
