# VM Network

## Purpose

Default port group on [[vSwitch0]], the primary vSwitch for [[esxi01]]. Attached VMs are connected to [[VMnet10]] through the vSwitch uplink.

---
## Type

ESXi Standard Port Group

---
## IPv4 Network

No addressing of its own.
See [[VMnet10]].

---
## Members

- [[ansible01]]
- [[managed01]]
- [[vcenter01]]

---
## Notes

Distinct from [[VMnet10]], which is the VMware Workstation host-only network on [[Precision7730]]. VM Network sits one layer above: [[esxi01]]'s vSwitch uplinks into VMnet10, so VMs on this port group share the same subnet as machines attached to VMnet10 directly (such as [[dnsmasqhost]]).

---
## Related

- [[vSwitch0]]
- [[VMnet10]]
- [[esxi01]]
- [[ansible01]]
- [[managed01]]