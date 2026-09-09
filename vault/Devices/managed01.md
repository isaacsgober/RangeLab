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

The ISO is mounted read-only at `/mnt/rocky-iso` at boot via `/etc/fstab` (`/dev/sr0`, `iso9660`, `ro,nofail`); `nofail` lets the node boot even if the ISO is detached from the virtual drive. See [ADR-0003](../Architecture/Decision%20Records/ADR-0003%20-%20Local%20ISO%20package%20repository.md).

The ISO image was already connected to this VM's drive (inherited from the [[ansible01]] clone), but nothing mounted it and there was no `/etc/fstab` entry, so the repository was dead after every boot until the fstab line was added on 2026-09-07.

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
