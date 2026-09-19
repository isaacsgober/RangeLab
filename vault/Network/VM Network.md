# VM Network

## Purpose

Port group for virtual machines on [[esxi01]]'s [[vSwitch0]]. Its members sit on the lab network,
[[VMnet10]], through the vSwitch's uplink.

---

## Type

ESXi standard port group

---

## IPv4 Network

No addressing of its own; see [[VMnet10]].

VLAN ID: 0 (untagged)

---

## Members

- [[vcenter01]]
- [[managed01]]

---

## Notes

VMnet10 is the Workstation host-only network on [[Precision7730]]; VM Network is one layer inside
it. esxi01's uplink, `vmnic0`, is its `vmxnet3` adapter on VMnet10, so VMs on this port group share
`10.10.10.0/24` with the nodes attached to VMnet10 directly: [[vyos01]], [[infra01]], and
[[ansible01]].

---

## Related

- [[vSwitch0]]
- [[VMnet10]]
- [[esxi01]]
- [[VM Layout]]
