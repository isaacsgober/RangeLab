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

Gateway: [[10.10.10.3]] ([[vyos01]])

DNS: [[10.10.10.3]] (vyos01 forwarding, until infra01 serves the lab zone at [[10.10.10.2]])

DHCP : Disabled

Host Adapter: 10.10.10.1 - an address on this network, not a gateway

---

## Members

- [[Precision7730]] (host adapter)
- [[vyos01]]
- [[infra01]]
- [[ansible01]]
- [[esxi01]]
- [[vcenter01]] (through esxi01)
- [[managed01]] (through esxi01)

---

## Notes

Not bridged: this network has no connection to the physical LAN of [[Precision7730]], and nothing
outside can open a connection into it.

Since 2026-09-16 it is no longer isolated *outbound*. [[vyos01]] routes and source-NATs it onto
[[VMnet8]], so lab nodes can reach the internet - package repositories and public NTP included.
The host adapter keeps `10.10.10.1` and serves no gateway, so Windows routing is unchanged.

Servers within the Range Lab use static IP addresses at this time.

---

## Related

- [[vyos01]]
- [[VMnet8]]
- [[IP Index]]
- [[Precision7730]]

