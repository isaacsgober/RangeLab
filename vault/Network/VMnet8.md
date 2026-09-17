# VMnet8

## Purpose

Workstation's NAT network. It is the lab's only path to the internet: [[vyos01]] uses it as its WAN
side and translates [[VMnet10]] traffic onto it.

No lab node other than vyos01 is attached to it.

---

## Type

NAT

---

## IPv4 Network

Subnet: 192.168.132.0

CIDR: /24

Gateway: 192.168.132.2 (Workstation's NAT service)

DNS: 192.168.132.2 (the same service, acting as a DNS proxy) — **unused by the lab**; it is too
slow for [[vyos01]]'s recursor, which forwards to public resolvers instead. See [[Troubleshooting]]
(2026-09-17).

DHCP: Enabled, `.128 – .254`, managed by Workstation

Host Adapter: 192.168.132.1

---

## Members

- [[Precision7730]] (host adapter)
- [[vyos01]] — `eth0`, `192.168.132.3/24`, static, deliberately below the DHCP range

---

## Notes

Addresses here are Workstation's defaults, not chosen by the lab; [[ADR-0001 - IP addressing plan]]
covers [[VMnet10]] only.

Traffic from the lab is translated twice — by vyos01 onto this network, then by Workstation onto
the host's LAN. Nothing on the host's LAN can reach the lab inward.

---

## Related

- [[vyos01]]
- [[VMnet10]]
- [[Precision7730]]
