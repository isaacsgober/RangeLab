# esxi01

## Purpose

Nested ESXi host. Runs [[vcenter01]] and [[managed01]], the nodes the lab exists to manage. Lab
services (routing, DNS, time, the Ansible control node) stay outside it so the hypervisor can be
rebuilt or broken without taking them down; see ADR-0006.

---

## Status

**Running** - installed 2026-09-18

---

## Operating System

VMware ESXi

### Version

9.1.0.0200, build 25557999 (`VMware-VMvisor-Installer-9.1.0.0200.25557999.x86_64.iso`)

---

## Hostname

esxi01

## Domain

rangelab.internal

## FQDN

esxi01.rangelab.internal

---

## Hosted On

[[Precision7730]] (VMware Workstation)

---

## Network

[[VMnet10]]

IPv4: [[10.10.10.10]]
Mask: 255.255.255.0
Gateway: [[10.10.10.3]] ([[vyos01]])
DNS: [[10.10.10.2]] ([[infra01]]); search `rangelab.internal`

The DNS record comes from `dns_extra_records` in the Ansible `group_vars`, since esxi01 is not an
Ansible-managed node.

---

## Management

Host Client: `https://esxi01.rangelab.internal`
SSH: `root@esxi01.rangelab.internal` (enabled in the DCUI)

---

## Resources

### CPU

6 vCPU (1 socket, 6 cores); hardware virtualization exposed to the guest (`vhv.enable`)

### Memory

64 GB

---

## Storage

| Disk | Size | Controller | Use |
| ---- | ---- | ---------- | --- |
| 1 | 128 GB, thin | PVSCSI | ESXi system; no datastore |
| 2 | 400 GB, thin | PVSCSI | [[datastore01-01]] |

The boot disk produces no datastore: ESXi 9 claims about 138 GB for system media and creates a
local VMFS datastore only above roughly 142 GB.

---

## Datastores

- [[datastore01-01]] - VMFS 6, on disk 2

---

## Hosted Virtual Machines

- [[vcenter01]]
- [[managed01]] *(Stage 6)*

---

## Notes

2026-09-18:
	Firmware is EFI, forced by the ESXi 9 guest profile. `rtc.diffFromUTC = "0"` is set in the `.vmx`.
	NTP: `ntpd` synced to `infra01.rangelab.internal` (`ntpq -p` shows `*`), set with `esxcli system ntp set --server=infra01.rangelab.internal --enabled=true`. ESXi's `ntpd` runs with `-g`: one large correction at startup, then corrections over 1000 s are refused. See [[chrony]] and [[NTP Hierarchy]].
	Certificate: VMCA-issued on the add to vCenter by FQDN, replacing the installer's self-signed `localhost.localdomain` certificate with no manual regeneration. Subject and SAN `esxi01.rangelab.internal`, valid to 2031-09-17.
	Evaluation license expires 2026-12-16 (89 days remaining on 2026-09-18).

---

## Related

- [[vcenter01]]
- [[managed01]]
- [[datastore01-01]]
- [[VMnet10]]
- [[infra01]]
- [[Build-Sequence]]
