# managed01

## Purpose

Ansible managed node.

---
## Status

Running

---
## Operating System

Rocky Linux
### Version

10.2 (x86_64)

---
## Hostname

managed01
## Domain

rangelab.local
## FQDN

managed01.rangelab.local

---
## IP Address

[[10.10.10.21]]

---
## Hosted On

[[esxi01]]

---
## Network

[[VM Network]]

---
## Management

SSH: `<user>@managed01.rangelab.local`

---
## Resources

### CPU

2 vCPU
### Memory

2GB
### Storage

30GB

---
## Services

- [[chrony]] — NTP client of [[ansible01]]

---
## Notes

Package installation is handled through a local repository built from the Rocky 10.2 DVD ISO, mounted at `/mnt/rocky-iso`. The `baseos`, `appstream`, and `extras` repos are disabled; `local-baseos` and `local-appstream` are defined in `/etc/yum.repos.d/local-iso.repo`.

The **ISO mount** is **not persistent** — it must be remounted after a reboot, or added to `/etc/fstab`.

Managed by [[ansible01]] using the `ansible` service account defined in [ADR-0002](../Architecture/Decision%20Records/ADR-0002%20-%20Dedicated%20service%20account). 

This machine was cloned from [[ansible01]].

`ansible-core` is installed rather than the full `ansible` package.

`~ansible/.ssh/authorized_keys` holds [[ansible01]]'s Ed25519 public key — the `ansible` account is reachable by key from the control node (Phase 2 / [ADR-0002](../Architecture/Decision%20Records/ADR-0002%20-%20Dedicated%20service%20account)).

Time is synced from [[ansible01]] via [[chrony]] (`server ansible01.rangelab.local iburst`).

---
## Related

- [[esxi01]]
- [[ansible01]]
- [[VM Network]]
- [[chrony]]
