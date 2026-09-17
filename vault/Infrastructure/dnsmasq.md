# dnsmasq

> **Pre-rebuild content.** Describes the lab as built before 2026-09-16, including the
> `rangelab.local` domain. Rewritten when Stage 3 of [[Build-Sequence]] rebuilds it.


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

**Interface:** ens160 (`interface=ens160`, `bind-dynamic`)

**How records are defined:** each lab host is one `host-record` line in `/etc/dnsmasq.conf`.
That single line creates both the host's A record and its PTR record.

```
domain=rangelab.local
local=/rangelab.local/            # answer these zones from local data only; never forward
local=/10.10.10.in-addr.arpa/
host-record=dnsmasqhost.rangelab.local,10.10.10.2
host-record=esxi01.rangelab.local,10.10.10.10
host-record=vcenter01.rangelab.local,10.10.10.15
host-record=ansible01.rangelab.local,10.10.10.20
host-record=managed01.rangelab.local,10.10.10.21
```

To add a host, add a `host-record=<fqdn>,<ip>` line, run `dnsmasq --test`, then
`systemctl restart dnsmasq`. A name defined this way exists for every record type, so a query
for a type it doesn't have (AAAA, MX) gets `NOERROR` with no answer.

Don't use `address=/<name>/<ip>`. It is a rule for a whole domain: it also answers for every
subdomain, and it made AAAA queries for lab hosts return NXDOMAIN until 2026-09-15 - see
[[Troubleshooting]].

**Forward DNS records:**

| Hostname                     | IP Address    |
| ---------------------------- | ------------- |
| `dnsmasqhost.rangelab.local` | `10.10.10.2`  |
| `esxi01.rangelab.local`      | `10.10.10.10` |
| `vcenter01.rangelab.local`   | `10.10.10.15` |
| `ansible01.rangelab.local`   | `10.10.10.20` |
| `managed01.rangelab.local`   | `10.10.10.21` |

**Reverse DNS (PTR) records:**

|               |                              |
| ------------- | ---------------------------- |
| IP Address    | PTR Hostname                 |
| `10.10.10.2`  | `dnsmasqhost.rangelab.local` |
| `10.10.10.10` | `esxi01.rangelab.local`      |
| `10.10.10.15` | `vcenter01.rangelab.local`   |
| `10.10.10.20` | `ansible01.rangelab.local`   |
| `10.10.10.21` | `managed01.rangelab.local`   |

**Configuration file:**

`/etc/dnsmasq.conf`

---

## Dependencies

[[dnsmasqhost]]
	interface ens160
---

## Notes

dnsmasq is config'd such that it should start on boot of [[dnsmasqhost]].

The configuration from before the 2026-09-15 `host-record` change is saved on dnsmasqhost as
`/etc/dnsmasq.conf.bak-rangelab`.

---

## Related

[[dnsmasqhost]]
[[VMnet10]]
[[vcenter01]]
[[vCenter]]
[[esxi01]]
