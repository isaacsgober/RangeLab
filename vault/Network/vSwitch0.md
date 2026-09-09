# vSwitch0

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