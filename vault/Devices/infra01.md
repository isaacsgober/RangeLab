# infra01

## Purpose

Lab services node: DNS and NTP for [[VMnet10]]. Replaces dnsmasqhost, which ran the same role
in the pre-rebuild lab without being managed by Ansible.

It runs in Workstation rather than on [[esxi01]], so the lab's name resolution and clock do not
depend on the hypervisor being up. That was the flaw behind the 3 h 49 m clock split in the old
lab.

---

## Status

**Running** - installed 2026-09-17. Services are configured in Stage 3, not by hand.

---

## Operating System

Rocky Linux

### Version

10.2 (x86_64), Minimal Install, BIOS firmware

---

## Hostname

infra01

## Domain

rangelab.internal

## FQDN

infra01.rangelab.internal

---

## IP Address

[[10.10.10.2]]

Gateway `10.10.10.3` ([[vyos01]]). DNS `10.10.10.2`: this node resolves through its own dnsmasq, as every
node does.

---

## Hosted On

[[Precision7730]] (VMware Workstation)

---

## Network

[[VMnet10]]

---

## Management

SSH: `labadmin@10.10.10.2`

---

## Resources

### CPU

1 vCPU

### Memory

2 GB

### Storage

20 GB, thin

---

## Services

- [[dnsmasq]] - authoritative for `rangelab.internal` and `10.10.10.in-addr.arpa`, forwarding
  everything else to [[vyos01]]
- [[chrony]] - NTP server for `10.10.10.0/24`, syncing from the public pool through [[vyos01]]

Both are configured by Ansible roles, not by hand. Records and time sources derive from the
inventory; see [[Build-Sequence]] Stage 3.

---

## Notes

2026-09-17:
	Installed from the Rocky 10.2 DVD with the [[Build-Sequence]] Stage 2 settings. Root account locked; `labadmin` is the administrator.
	`rtc.diffFromUTC = "0"` in the `.vmx`, and the installer's time zone set to UTC.
	The DVD is installation media only. This node uses the normal Rocky repositories over the internet through [[vyos01]], which is what ADR-0003's local ISO repository existed to work around.
	Firmware is BIOS: Workstation offers no UEFI for this guest profile. Rocky's automatic partitioning therefore creates a `biosboot` partition rather than an EFI system partition, so there is no `/boot/efi`.

	The DNS servers entered at install remain in this node's NetworkManager connection profile, but are inert: the `dns` role sets `dns=none`, so NetworkManager no longer writes `/etc/resolv.conf`. Removing that drop-in would let the installer's values return.

---

## Verification

First boot, 2026-09-17:

| Check | Result |
| ----- | ------ |
| `ip -br addr`, `ip route` | `10.10.10.2/24`, default via `10.10.10.3` |
| `ping 10.10.10.3` | Replies |
| `sudo dnf makecache` | Metadata cache created in 12 s |
| `timedatectl` | `Etc/UTC (UTC, +0000)`, **RTC in local TZ: no** |
| `getenforce` | `Enforcing` |

`timedatectl` also reported `System clock synchronized: no` and `NTP service: n/a`, which is
expected - a Minimal install has no time service, and chrony arrives with the `ntp_server` role in
Stage 3. The RTC read about a minute behind the system clock at that point.

---

## Related

- [[vyos01]]
- [[ansible01]]
- [[VMnet10]]
- [[Build-Sequence]]
- [[IP Index]]
