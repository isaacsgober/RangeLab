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
- [[chrony]] — lab NTP server

---
## Notes

Package installation is handled through a local repository built from the Rocky 10.2 DVD ISO, mounted at `/mnt/rocky-iso`. The `baseos`, `appstream`, and `extras` repos are disabled; `local-baseos` and `local-appstream` are defined in `/etc/yum.repos.d/local-iso.repo`.

The ISO is mounted read-only at `/mnt/rocky-iso` at boot via `/etc/fstab` (`/dev/sr0`, `iso9660`, `ro,nofail`); `nofail` lets the node boot even if the ISO is detached from the virtual drive. See [ADR-0003](../Architecture/Decision%20Records/ADR-0003%20-%20Local%20ISO%20package%20repository.md).

Hosts the `ansible` service account defined in [ADR-0002](../Architecture/Decision%20Records/ADR-0002%20-%20Dedicated%20service%20account). 

This machine was cloned to create [[managed01]].

`ansible-core` is installed rather than the full `ansible` package.

Serves NTP to the [[VMnet10]] segment via [[chrony]] (`local stratum 10`, `allow 10.10.10.0/24`). It has no upstream, so it is the lab's undisciplined time root — see [[chrony]] for the tradeoff.

The `ansible` service account authenticates to managed nodes with an Ed25519 SSH key at `~ansible/.ssh/id_ed25519`. The private key stays on this host and is excluded from the repo.

---
## Related

- [[esxi01]]
- [[managed01]]
- [[VM Network]]
- [[chrony]]
