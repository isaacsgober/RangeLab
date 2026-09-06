# dnsmasq

## Purpose

To provide DNS service to machines in Range Lab

---

## Host

[[dnsmasqhost]]

## IP

[[10.10.10.2]]

---

## Ports

53/TCP
53/UDP

---

## Configuration

**DNS domain:** rangelab.local

**Interface:** ens160

**Forward DNS records:**

| Hostname                     | IP Address    |
| ---------------------------- | ------------- |
| `dnsmasqhost.rangelab.local` | `10.10.10.2`  |
| `esxi01.rangelab.local`      | `10.10.10.10` |
| `vcenter01.rangelab.local`   | `10.10.10.15` |
| `ansible01.rangelab.local`   | `10.10.10.20` |
| `rocky01.rangelab.local`     | `10.10.10.21` |

**Reverse DNS (PTR) records:**

|               |                              |
| ------------- | ---------------------------- |
| IP Address    | PTR Hostname                 |
| `10.10.10.2`  | `dnsmasqhost.rangelab.local` |
| `10.10.10.10` | `esxi01.rangelab.local`      |
| `10.10.10.15` | `vcenter01.rangelab.local`   |
| `10.10.10.20` | `ansible01.rangelab.local`   |
| `10.10.10.21` | `rocky01.rangelab.local`     |

**Configuration file:**

`/etc/dnsmasq.conf`

---

## Dependencies

[[dnsmasqhost]]
	interface ens160
---

## Notes

dnsmasq is config'd such that it should start on boot of [[dnsmasqhost]].

---

## Related

[[dnsmasqhost]]
[[VMnet10]]
[[vcenter01]]
[[vCenter]]
[[esxi01]]
