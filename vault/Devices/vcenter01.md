# vcenter01

## Purpose

vCenter Server for Range Lab: manages [[esxi01]] and the VMs on it.

---

## Status

**Running** - deployed 2026-09-18

---

## Operating System

VMware vCenter Server Appliance (Photon OS)

### Version

9.1.0.0200, build 25573614

---

## Hostname

vcenter01

## Domain

rangelab.internal

## FQDN

vcenter01.rangelab.internal

---

## IP Address

[[10.10.10.15]]

Gateway `10.10.10.3` ([[vyos01]]); DNS `10.10.10.2` ([[infra01]]). The DNS record comes from
`dns_extra_records`, since the appliance is not an Ansible-managed node.

---

## Hosted On

[[esxi01]], on [[datastore01-01]] (thin)

---

## Network

[[VMnet10]], through esxi01's VM Network port group

---

## Management

vSphere Client: `https://vcenter01.rangelab.internal/ui`
VAMI: `https://vcenter01.rangelab.internal:5480`
SSH: enabled; root lands in `appliancesh`, and `shell` switches to bash

SSO domain `vsphere.local`; administrator `administrator@vsphere.local`. Credentials in `creds.md`.

---

## Resources

Deployment size **Small**: 4 vCPU, 21 GB.

---

## Services

- [[vCenter]]

---

## Notes

2026-09-18:
	Deployed with the GUI installer from the Windows host, with final network values from the start; see [[Build-Sequence]] Stage 5. The pre-rebuild appliance was deployed with temporary values and fixed afterwards.
	Time: NTP from `infra01.rangelab.internal`, set in the installer.
	Machine certificate: `CN=vcenter01.rangelab.internal` with matching SAN, issued by VMCA, valid to 2028-09-18.
	Evaluation license expires 2026-12-17.
	CEIP is on. With egress through [[vyos01]], it transmits to Broadcom; reversible under Administration → Deployment.
	An appliance: changes go through the installer, VAMI, `appliancesh`, or the API. Ansible's roles do not apply to it; see [[Known-Issues]] and the VyOS/vCenter automation follow-up in [[Rebuild-Plan]].

---

## Related

- [[vCenter]]
- [[esxi01]]
- [[datastore01-01]]
- [[infra01]]
- [[Build-Sequence]]
