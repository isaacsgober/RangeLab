# chrony

> **Pre-rebuild content.** Describes the lab as built before 2026-09-16, including the
> `rangelab.local` domain. Rewritten when Stage 3 of [[Build-Sequence]] rebuilds it.


## Purpose

Time synchronization for Range Lab. [[ansible01]] runs `chronyd` as the NTP server for the VMs
nested on [[esxi01]], and takes its own time from [[Precision7730]]. See
[ADR-0004](../Architecture/Decision%20Records/ADR-0004%20-%20Lab%20time%20source.md).

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

Time comes from the internet through [[Precision7730]]. Windows Time on the host syncs to
`time.windows.com` and serves NTP on [[VMnet10]] at `10.10.10.1`.

| Node | Client | Syncs from |
| ---- | ------ | ---------- |
| [[ansible01]] | chrony | `10.10.10.1` |
| [[dnsmasqhost]] | chrony | `10.10.10.1` |
| [[managed01]] | chrony | [[ansible01]] |
| [[vcenter01]] | ntpd (VAMI) | [[ansible01]] |
| [[esxi01]] | ntpd | [[ansible01]] |

Stock `/etc/chrony.conf` is preserved as `/etc/chrony.conf.orig` on [[ansible01]] and
[[managed01]]. The configuration as it was before 2026-09-15 is saved as
`/etc/chrony.conf.bak-rangelab` on ansible01, managed01, and dnsmasqhost.

**Server - [[ansible01]]**, `/etc/chrony.conf`:

| Line | Effect |
| ---- | ------ |
| `server 10.10.10.1 iburst` | Upstream is Precision7730. `iburst` brings the first sync down to seconds. |
| `makestep 1.0 -1` | Step the clock whenever it is off by more than 1 s. The default only steps in the first three updates, which cannot recover a VM that resumes hours behind. |
| `# local stratum 10` | Commented out 2026-09-15. With a real upstream, losing it should leave clients unsynchronized rather than quietly serving a possibly frozen clock. |
| `allow 10.10.10.0/24` | Answer NTP queries from VMnet10. The default is to answer none. |

firewalld: `ntp` service (123/UDP) added permanently.

`chronyc tracking` → `Reference ID 0A0A0A01` (10.10.10.1), `Stratum 6`.

**Clients - [[managed01]] and [[dnsmasqhost]]**, `/etc/chrony.conf`:

| Line | Effect |
| ---- | ------ |
| `server ansible01.rangelab.local iburst` | managed01 syncs from ansible01. |
| `server 10.10.10.1 iburst` | dnsmasqhost syncs from Precision7730 directly. It runs beside esxi01 in Workstation, so it must not follow a server that freezes whenever esxi01 is suspended. |
| `makestep 1.0 -1` | Same as the server. |

`chronyc sources` → `^*` on the configured source. managed01 is at stratum 7, dnsmasqhost at 6.

---

## Dependencies

- [[Precision7730]] running Windows Time as an NTP server, reachable on 123/UDP
- [[ansible01]] running `chronyd`, reachable on 123/UDP
- [[dnsmasq]]: clients resolve the server as `ansible01.rangelab.local`

---

## Notes

**Windows Time dispersion.** Right after Windows Time starts, Precision7730 advertises about 8 s
of root dispersion. chrony rejects sources above 3 s (`chronyc selectdata` marks them `d`), and
ntpd rejects above 1.5 s. The dispersion halves with each poll and settles within a few minutes. At a
1024 s poll it settles near 1.1 s - see [[Known-Issues]].

**Suspends.** Suspending [[esxi01]] freezes the nested VMs' clocks. On resume, chrony and ntpd
distrust their source until the pre-suspend samples age out ("Jitter ... exceeds maxjitter of
1.000 seconds"), so recovery takes 6–15 minutes. Prefer shutting down; see
[ADR-0004](../Architecture/Decision%20Records/ADR-0004%20-%20Lab%20time%20source.md).

`chrony` package updates are limited to the Rocky 10.2 DVD set - see [[ansible01]].

---

## Related

- [[NTP Hierarchy]]
- [[ansible01]]
- [[managed01]]
- [[dnsmasqhost]]
- [[Precision7730]]
- [[esxi01]]
- [[vcenter01]]
- [[VMnet10]]
- [[dnsmasq]]
- [[vCenter]]
- [[Naming Convention]]
