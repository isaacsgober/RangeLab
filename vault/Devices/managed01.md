# managed01

## Purpose

Ansible-managed Rocky node nested inside [[esxi01]]: the node the lab's configuration management
exists to manage.

---

## Status

**Running** - built 2026-09-18

---

## Operating System

Rocky Linux

### Version

10.2 (x86_64), Minimal Install, EFI firmware

---

## Hostname

managed01

## Domain

rangelab.internal

## FQDN

managed01.rangelab.internal

---

## IP Address

[[10.10.10.21]]

Gateway `10.10.10.3` ([[vyos01]]); DNS `10.10.10.2` ([[infra01]]). The DNS record is generated
from the Ansible inventory.

---

## Hosted On

[[esxi01]], on [[datastore01-01]] (thin)

---

## Network

[[VMnet10]], through esxi01's VM Network port group; `vmxnet3` (`ens33`)

---

## Management

SSH: `labadmin@managed01.rangelab.internal` (password)
Ansible: as `ansible`, by key from [[ansible01]]

---

## Resources

### CPU

2 vCPU

### Memory

2 GB

### Storage

30 GB, thin, PVSCSI

---

## Services

- [[chrony]] client of [[infra01]]

---

## Notes

2026-09-18:
	Installed from `Rocky-10.2-x86_64-boot.iso`, pulling packages from the Rocky mirrors; see [[Build-Sequence]] Stage 6.
	Joined Ansible by the Stage 3.4 procedure: DNS record published first with `--limit dns_servers --tags dns`, then bootstrapped and converged by name.
	`open-vm-tools` 13.0.10 is installed, which esxi01's guest shutdown depends on. Second in esxi01's startup order, first to stop.
	Not a clone of any other VM. The pre-rebuild managed01 was a clone of ansible01 and inherited its machine-id and a broken package source.

---

## Related

- [[esxi01]]
- [[ansible01]]
- [[infra01]]
- [[datastore01-01]]
- [[Build-Sequence]]
