# VMnet10

## Purpose
Primary host-only network for Range Lab.

Provides isolated communication between host and virtual infrastructure.

---
## Type

Host-only

---

## IPv4 Network

Subnet: 10.10.10.0

CIDR: /24

Gateway: [[10.10.10.1]]

DNS: [[10.10.10.2]]

DHCP : Disabled

Host Adapter: 10.10.10.1

---

## Members

- [[Precision 7730]]
- [[dnsmasqhost]]
- [[esxi01]]
- [[vcenter01]]


---

## Notes

This network is isolated from the physical LAN of [[Precision 7730]].

Servers within the Range Lab use static IP addresses at this time.

---

## Related

N/A

