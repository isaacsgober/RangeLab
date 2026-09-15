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

6 vCPU

### Memory

16 GB

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

2026-09-15:
	Resized to 6 vCPU and 16 GB. At 2 vCPU the appliance was CPU-starved (15-minute load average 13.46).
	Now manages [[esxi01]].
	The appliance's embedded dnsmasq (`127.0.0.1`) has hand-edited `host-record` entries and `neg-ttl=10` that VCSA's own tooling doesn't manage — see [[Troubleshooting]] (2026-09-15) and [[Known-Issues]].

---

## Related

- [[esxi01]]
- [[vCenter]]
- [[datastore01-02]]
- [[VMnet10]]