# chrony

## Purpose

Time synchronization for Range Lab. [[ansible01]] runs `chronyd` as an NTP server for the
[[VMnet10]] segment; other Linux nodes sync from it.

---

## Host

[[ansible01]]

## IP

[[10.10.10.20]]

---

## Ports

123/UDP

---

## Configuration

The lab is offline — `2.rocky.pool.ntp.org` neither resolves nor routes, so there is **no
upstream time source**. [[ansible01]] uses its own system clock as an undisciplined
reference and serves that to the segment. Stock `/etc/chrony.conf` is preserved as
`/etc/chrony.conf.orig` on both hosts.

**Server — [[ansible01]]**, `/etc/chrony.conf`:

| Line | Effect |
| ---- | ------ |
| `#pool 2.rocky.pool.ntp.org iburst` | Distro internet pool, commented out — unreachable. |
| `local stratum 10` | Serve time despite having no real upstream; advertise stratum 10, a "local fallback" level that clients still accept. |
| `allow 10.10.10.0/24` | Answer NTP queries from VMnet10. Default is to answer none. |

firewalld: `ntp` service (123/UDP) added permanently.

`chronyc tracking` → `Stratum 10`, `Reference ID 7F7F0101` (127.127.1.1, the internal
reference clock), `Leap status: Normal`. `timedatectl` → `System clock synchronized: no`,
which is expected: nothing external confirms this clock. ansible01 is the root.

**Client — [[managed01]]**, `/etc/chrony.conf`:

| Line | Effect |
| ---- | ------ |
| `# pool 2.rocky.pool.ntp.org iburst` | Distro internet pool, commented out. |
| `server ansible01.rangelab.local iburst` | Sync from ansible01 only. `iburst` brings the first sync down to seconds. |

`chronyc sources -v` → `^* ansible01.rangelab.local` (stratum 10). `chronyc tracking` →
`Stratum 11`, `Reference ID 0A0A0A14` (10.10.10.20). `timedatectl` →
`System clock synchronized: yes`.

---

## Dependencies

- [[ansible01]] running `chronyd`, reachable on 123/UDP
- [[dnsmasq]] — clients resolve the server as `ansible01.rangelab.local`

---

## Notes

**Limitation — undisciplined reference.** With no upstream, only *relative* agreement
between lab nodes is guaranteed; absolute time can drift from real-world time together.
Acceptable while the lab has no Kerberos/AD and nothing external-facing. Revisit when
Active Directory is added (a domain controller normally becomes the authoritative time
source) or if an upstream path becomes available.

[[vcenter01]] is **not** yet a client of this server — the VCSA keeps its own time
configuration. See [[vCenter]].

`chrony` package updates are limited to the Rocky 10.2 DVD set — see [[ansible01]].

---

## Related

- [[ansible01]]
- [[managed01]]
- [[VMnet10]]
- [[dnsmasq]]
- [[vCenter]]
- [[Naming Convention]]
