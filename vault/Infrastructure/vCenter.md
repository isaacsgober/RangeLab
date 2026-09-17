
# vCenter

> **Pre-rebuild content.** Describes the lab as built before 2026-09-16, including the
> `rangelab.local` domain. Rewritten when Stage 5 of [[Build-Sequence]] rebuilds it.


## Purpose

To provide centralized management of ESXi hosts and virtual infrastructure; it is the management plane.

---

## Host

[[vcenter01]]

---
## Ports

- 443/TCP - HTTPS; vSphere Client, vCenter Server API, and other vCenter services
- 80/TCP - HTTP; redirects to HTTPS
- 5480/TCP - HTTPS; vCenter Server Appliance Management Interface (VAMI)

---

## Configuration

- Deployment Type: VMware vCenter Server Appliance (VCSA) 
- Deployment Size: Tiny 
- Version: 9.1
---

## Dependencies

- [[esxi01]] 
- [[VMnet10]] 
- [[datastore01-02]] 
- [[dnsmasq]]
- NTP - [[vcenter01]] syncs from [[chrony]] on [[ansible01]] (VAMI timesync mode: NTP). See [ADR-0004](../Architecture/Decision%20Records/ADR-0004%20-%20Lab%20time%20source.md).

---
## Notes

The VMware vCenter Server Appliance (VCSA) is a preconfigured virtual appliance that contains vCenter and all of the software required to run vCenter.

---

## Related

- [[vcenter01]] 
- [[esxi01]] 
- [[ESXi]] 
- [[vSphere]] 
- [[VMnet10]] 
- [[datastore01-02]]
- [[chrony]]