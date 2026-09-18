# vSwitch0

> **Pre-rebuild content.** Describes the lab as built before 2026-09-16, including the
> `rangelab.local` domain. Rewritten when Stage 4 of [[Build-Sequence]] rebuilds it.


## Purpose

Default virtual switch on esxi01, providing management and VM connectivity.

---

## Type

Standard vSwitch

---

## Host

[[esxi01]]

---

## Uplinks

- vmnic0

---

## Port Groups

- [[VM Network]]
- Management Network

---

## Configuration

MTU: 1500

Security policy:

| Setting             | Value  |
| ------------------- | -------|
| Promiscuous Mode    | Reject |
| MAC Address Changes | Reject |
| Forged Transmits    | Reject |

---

## Notes

---

## Related

- [[VM Network]]
- [[VMnet10]]
- [[esxi01]]