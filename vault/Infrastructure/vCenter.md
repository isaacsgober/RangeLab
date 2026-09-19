# vCenter

## Purpose

Central management of [[esxi01]] and its VMs.

---

## Host

[[vcenter01]]

## IP of Host

[[10.10.10.15]]

---

## Ports

443/TCP (vSphere Client, API), 5480/TCP (VAMI)

---

## Configuration

| Setting | Value |
| ------- | ----- |
| Version | 9.1.0.0200, build 25573614 |
| SSO domain | `vsphere.local` |
| Datacenter | `rangelab` |
| Hosts | [[esxi01]], added by FQDN |
| Datastores | [[datastore01-01]] |
| VMs | [[vcenter01]], [[managed01]] |
| License | Evaluation, expires 2026-12-17 |

Host certificates are issued by VMCA when a host is added; esxi01's carries its FQDN.

---

## Dependencies

- [[infra01]] for DNS (forward and reverse) and time
- [[esxi01]], which hosts the appliance itself

---

## Notes

`Scripts/vcenter_inventory.py` lists VMs through `/api/vcenter/vm`.

---

## Related

- [[vcenter01]]
- [[esxi01]]
- [[managed01]]
- [[datastore01-01]]
- [[Build-Sequence]]
