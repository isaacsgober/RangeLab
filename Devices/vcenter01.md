# vcenter01

## Purpose

To host [[vCenter]]
To provide centralized management of VMware virtual machines/environment

---

## Status

**Running**

---

## Operating System

VMware vCenter Server Appliance
### Version

9.1

---

## Hostname

vcenter01

## Domain

rangelab.local

## FQDN 

vcenter01.rangelab.local

---
## IP Address

[[10.10.10.15]]

---

## Hosted On

[[esxi01]]

---

## Network

[[VMnet10]]

---
## Management

vSphere Client: https://vcenter01.rangelab.local (10.10.10.15)
VAMI: https://vcenter01.rangelab.local:5480

---
## Resources

### vCPU

### Memory

### Storage
#### Datastore
[[datastore01-02]]

---

## Services

VMware [[vCenter]]

---

## Notes

2026-08-04:
	Temporary gateway and DNS settings were used during deployment; lab does not yet contain a router or internal DNS server.

---

## Related

- [[esxi01]]
- [[vCenter]]
- [[datastore01-02]]
- [[VMnet10]]