# vSwitch0

## Purpose

The standard vSwitch on [[esxi01]], created by the installer. Carries both management traffic and
VM traffic onto [[VMnet10]].

---

## Type

Standard vSwitch

---

## Host

[[esxi01]]

---

## Uplinks

- `vmnic0`: esxi01's `vmxnet3` adapter on [[VMnet10]]

---

## Port Groups

| Port group | VLAN | Clients |
| ---------- | ---- | ------- |
| Management Network | 0 | `vmk0`, esxi01's management interface at `10.10.10.10` |
| [[VM Network]] | 0 | [[vcenter01]], [[managed01]] |

---

## Configuration

MTU: 1500
CDP: listen
Ports: 128 configured

Security policy:

| Setting | Value |
| ------- | ----- |
| Promiscuous mode | Reject |
| MAC address changes | Reject |
| Forged transmits | Reject |

---

## Notes

One uplink and no VLANs: the lab has a single flat network, and every VM on this switch is on
`10.10.10.0/24`. Segmentation belongs to a later stage of the roadmap.

Reject on all three security settings is correct here. VMs on this switch send from their own vNIC
MAC addresses, so nothing is forged at this layer. Their frames leave esxi01 through its single
adapter carrying their own MACs, which is a question for the outer switch, Workstation's VMnet10,
not for this policy.

---

## Related

- [[VM Network]]
- [[VMnet10]]
- [[esxi01]]
- [[VM Layout]]
