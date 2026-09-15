# esxi01

## Purpose

Nested ESXi lab host

---

## Status

**Running**

---

## Operating System

VMware ESXi

### Version

9.1.0.0200.25557999 (Release Build)

---

## Hostname

esxi01

## Domain

rangelab.local

## FQDN

esxi01.rangelab.local

---

## Hosted On

[[Precision7730]] (VMware Workstation)

---

## Network

[[VMnet10]]

IPv4: [[10.10.10.10]]
Mask: 255.255.255.0
Gateway: [[10.10.10.1]] (To be updated.)
DNS: [[10.10.10.2]]

---

## Management

Web Interface:
https://10.10.10.10

vCenter: managed by [[vcenter01]] (added 2026-09-15)

---

## Resources

### CPU

12 vCPUs

### Memory

32 GB

---

## Storage

Disk 1
- 142 GB
- ESXi system
- [[datastore01-01]]

Disk 2
- 224 GB
- [[datastore01-02]]

---

## Datastores

- [[datastore01-01]] (13.75 GB)
- [[datastore01-02]] (224 GB)

---

## Hosted Virtual Machines

- [[vcenter01]]
- [[ansible01]]
- [[managed01]]

---

## Notes

2026-09-15:
	Resized from 8 to 12 vCPUs in VMware Workstation.
	Added to vCenter by FQDN once the add-host failure was resolved — see [[Troubleshooting]] (2026-09-15).

---

## Related

- [[Precision7730]]
- [[vcenter01]]
- [[ansible01]]
- [[managed01]]
- [[VMnet10]]
- [[datastore01-01]]
- [[datastore01-02]]
