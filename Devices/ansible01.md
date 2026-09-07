# ansible01

## Purpose

Ansible management node.

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

ansible01
## Domain

rangelab.local
## FQDN

ansible01.rangelab.local

---
## IP Address

[[10.10.10.20]]

---
## Hosted On

[[esxi01]]

---
## Network

[[VM Network]]

---
## Management

SSH: `<user>@ansible01.rangelab.local`

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

- [[Ansible]]

---
## Notes

Package installation is handled through a local repository built from the Rocky 10.2 DVD ISO, mounted at `/mnt/rocky-iso`. The `baseos`, `appstream`, and `extras` repos are disabled; `local-baseos` and `local-appstream` are defined in `/etc/yum.repos.d/local-iso.repo`.

The **ISO mount** is **not persistent** — it must be remounted after a reboot, or added to `/etc/fstab`.

Hosts the `ansible` service account defined in [ADR-0002](../Architecture/Decision%20Records/ADR-0002%20-%20Dedicated%20service%20account). 

This machine was cloned to create [[managed01]].

`ansible-core` is installed rather than the full `ansible` package.

---
## Related

- [[esxi01]]
- [[managed01]]
- [[VM Network]]
