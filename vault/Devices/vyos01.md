# vyos01

## Purpose

The lab router. It is the default gateway for [[VMnet10]], translates lab traffic out to the
internet, and forwards DNS for the lab. Built first in the 2026-09-16 rebuild — every other node is
installed with `10.10.10.3` as its gateway. See [[Build-Sequence]] Stage 1.

---

## Status

**Running** — built 2026-09-16

---

## Platform

VyOS

### Version

| `show version` | Value |
| -------------- | ----- |
| Version | VyOS 2026.02 |
| Release train | `circinus` |
| Release flavor | `generic` |
| Built on | 2026-02-09 20:41 UTC, build commit `e4c4eddad9b984` |
| Boot via | installed image |

Installed from `vyos-2026.02-generic-amd64.iso` with `install image` — "boot via: installed image"
is what distinguishes that from running the live ISO.

This is a **stream** release, not LTS. It logs in with a banner calling itself a technology preview
for a future LTS release and warning against production use. That is acceptable here: the lab is a
portfolio environment, VyOS LTS images are behind a subscription, and the router's job is small and
fully captured in [[vyos01.config]], so replacing it is a rebuild rather than a migration.

---

## Hostname

vyos01

## Domain

rangelab.internal

## FQDN

vyos01.rangelab.internal

*The FQDN does not resolve yet; the lab zone starts existing when infra01 serves DNS.*

---

## IP Address

[[10.10.10.3]] (LAN) — also `192.168.132.3/24` on the WAN side

---

## Hosted On

[[Precision7730]] (VMware Workstation)

---

## Interfaces

| Interface | MAC | Network | Address | Purpose |
| --------- | --- | ------- | ------- | ------- |
| `eth0` | `00:0c:29:5c:a9:f6` | [[VMnet8]] | `192.168.132.3/24` | WAN — uplink to Workstation's NAT service |
| `eth1` | `00:0c:29:5c:a9:00` | [[VMnet10]] | `10.10.10.3/24` | LAN — the lab network |

Each interface is pinned to its MAC with `hw-id`, so the names cannot swap across reboots. `.3` is
static and below Workstation's VMnet8 DHCP range (`.128–.254`), so the WAN address cannot move.

---

## Routing

| Route | Next hop |
| ----- | -------- |
| `0.0.0.0/0` | `192.168.132.2` — Workstation's NAT gateway on VMnet8 |
| `10.10.10.0/24` | Connected, `eth1` |
| `192.168.132.0/24` | Connected, `eth0` |

---

## NAT

Source rule 100, "Lab to internet": traffic from `10.10.10.0/24` leaving `eth0` is translated with
`masquerade` — rewritten to whatever address `eth0` holds.

Lab traffic is therefore translated twice: once by vyos01 onto VMnet8, once by Workstation onto the
host's LAN. Nothing outside can open a connection inward, which is intentional.

---

## Services

| Service | Configuration | Notes |
| ------- | ------------- | ----- |
| DNS forwarding | `listen-address 10.10.10.3`, `allow-from 10.10.10.0/24`, `name-server 192.168.132.2` | `allow-from` keeps it from being an open resolver; `listen-address` keeps it off the WAN side. Lab nodes use it directly until infra01 exists, then infra01 answers `rangelab.internal` and forwards the rest here. |
| SSH | `listen-address 10.10.10.3` | LAN only. |
| NTP | VyOS defaults: servers `time1`–`time3.vyos.net`, `allow-client` for RFC 1918, loopback, and link-local | Shipped with the image, not configured for this lab. The lab's own time design is still [[chrony]] on infra01 — see [[Rebuild-Plan]] §4.3. |

---

## Firewall Rules

None. vyos01 forwards and translates, but filters nothing. Its WAN side sits on Workstation's
private NAT network rather than the internet, so it is not directly exposed. A firewall policy is a
deferred follow-up — see [[Rebuild-Plan]].

---

## VLANs

None.

---

## Management

SSH: `ssh vyos@10.10.10.3`
Console: Workstation KVM console

---

## Resources

### CPU

1 vCPU

### Memory

4 GB

### Storage

20 GB, thin, single `.vmdk`

Firmware BIOS; guest OS profile Debian 12 64-bit; LSI Logic SCSI controller; two `e1000` adapters.

---

## Notes

2026-09-16:
	`rtc.diffFromUTC = "0"` is set in `vyos01.vmx`. Workstation otherwise gives the guest a hardware clock on the host's *local* time, which Linux reads as UTC — the reason dnsmasqhost used to boot five hours in the past.
	VyOS edits a candidate configuration: `configure` to enter it, `compare` to see the pending change, `commit` to make it live, and `save` to write `/config/config.boot`. A commit that is not saved is lost at reboot. `system config-management commit-revisions 100` keeps the last 100 committed revisions on the router itself.
	The running configuration is exported to [[vyos01.config]] as `set` commands, with the password hash replaced by a placeholder.
	Verified at build: both interfaces up, default route present, and `ping` to `192.168.132.2`, `1.1.1.1`, and `vyos.net` all replied — the last one proving DNS forwarding works.
	The Windows host keeps `10.10.10.1` on its VMnet10 adapter with no gateway, so host routing is unchanged by the lab having one.

---

## Related

- [[Precision7730]]
- [[VMnet10]]
- [[VMnet8]]
- [[vyos01.config]]
- [[IP Index]]
- [[Naming Convention]]
- [[Build-Sequence]]
- [[Rebuild-Plan]]
