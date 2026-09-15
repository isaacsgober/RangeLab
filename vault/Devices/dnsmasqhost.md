# dnsmasqhost

## Purpose

To host [[dnsmasq]], which provides DNS service for Range Lab.

---
## Status

**Running**

---
## Operating System

Rocky Linux
### Version

10.2 (x86)

---
## Hostname

dnsmasqhost

## Domain

rangelab.local

## FQDN

dnsmasqhost.rangelab.local

---
## IP Address

[[10.10.10.2]]

---

## Hosted On

[[Precision7730]]

---
## Network

[[VMnet10]]

---
## Management

SSH Login Cmd:
ssh dnsmasqhost

---
## Resources

### CPU

1 vCPU
### Memory

2GB
### Storage

20GB

---

## Services

- [[dnsmasq]]
- [[chrony]] — NTP client of [[Precision7730]]

---

## Notes

2026-09-15:
	Time syncs from [[Precision7730]] via [[chrony]] (`server 10.10.10.1 iburst`, `makestep 1.0 -1`). chronyd was inactive before this date. It uses the host rather than [[ansible01]] because it runs beside [[esxi01]] in Workstation: during a suspend test, following ansible01 pulled this node's clock back 330 s. See [ADR-0004](../Architecture/Decision%20Records/ADR-0004%20-%20Lab%20time%20source.md).
	Its virtual hardware clock runs on the host's local time, not UTC, so it boots about 5 hours off until chrony corrects it.
	Not part of esxi01's autostart. Power it on before esxi01 and off after, so DNS is up whenever vCenter is.

---

## Related

