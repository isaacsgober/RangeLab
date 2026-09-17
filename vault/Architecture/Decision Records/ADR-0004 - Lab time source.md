# ADR-0004 - Lab time source

## Status

Accepted, and **revised 2026-09-17** by [ADR-0007 - Internet access through
vyos01](ADR-0007%20-%20Internet%20access%20through%20vyos01.md) and
[ADR-0006](ADR-0006%20-%20Infrastructure%20services%20outside%20the%20hypervisor.md). What changed:
the upstream is no longer [[Precision7730]]'s Windows Time service, and the lab's NTP server is
[[infra01]] rather than a nested [[ansible01]]. [[infra01]] syncs from public NTP through
[[vyos01]] and serves `10.10.10.0/24`. The rest of this record still holds - `makestep 1.0 -1` on
chrony nodes, no invented `local stratum`, ESXi's one-shot `-g` correction, and shutting down
rather than suspending.

Originally superseded the 2026-09-07 choice of an undisciplined [[ansible01]] as the lab's
time root (recorded in [[chrony]] and Journal/[[2026-09-07]]).

---

## Context

On 2026-09-07 [[ansible01]] became the lab NTP server with no upstream (`local stratum 10`).
The lab is offline, and using Windows as an NTP server was judged too fiddly. That design only
promised that lab nodes would agree with *each other*.

A clock sweep on 2026-09-15 found that promise had not held. The lab had split into two groups:

| Group | Nodes | Offset from Precision7730 |
|---|---|---|
| Tracked the Windows host | [[Precision7730]], [[esxi01]], [[dnsmasqhost]] | within 0.2 s |
| Tracked ansible01 | [[ansible01]], [[managed01]], [[vcenter01]] | −3 h 49 m 29 s |

- **ansible01 lost the time while esxi01 was suspended.** Its clock was correct at boot
  (`rtc_cmos: setting system clock to 2026-09-15T03:38:02 UTC`). Suspending [[esxi01]] in
  VMware Workstation freezes every VM nested inside it. On resume, esxi01 and dnsmasqhost
  (Workstation guests) were caught up to the host. ansible01 had nothing to catch up from: VMware
  Tools timesync was disabled and chrony had no source.
- **vcenter01 and managed01 followed ansible01** exactly as configured.
- **esxi01 was configured for ansible01 but refused it.** ESXi's ntpd runs with `-g`, which allows
  one large correction at startup only; after that it refuses corrections over 1000 s
  (`Time Synchronized: false`, stratum 16, "no peer for too long, server running free").
- **dnsmasqhost had no NTP at all.** chronyd was inactive and pointed at an unreachable internet
  pool.
- **Windows Time on Precision7730 was stopped** (startup type Manual).

vCenter and the host it manages were 3.8 hours apart. That much skew breaks authentication
tokens today, and it would break Kerberos at the Active Directory stage.

---

## Decision

[[Precision7730]], the only machine with internet access, is the lab's time source.

**Precision7730 (Windows Time):**
- Service set to Automatic and running, synced to `time.windows.com,0x8`.
- NTP server enabled: `TimeProviders\NtpServer\Enabled = 1`, `Config\AnnounceFlags = 5`.
- `Config\MinPollInterval = 6`, `Config\MaxPollInterval = 10`.
- Windows Firewall rule "NTP server (RangeLab VMnet10)": inbound UDP 123 from `10.10.10.0/24` only.

**Lab nodes:**

| Node | Client | Syncs from | Notes |
|---|---|---|---|
| [[ansible01]] | chrony | `10.10.10.1` | Still serves NTP to VMnet10. `local stratum 10` removed. |
| [[dnsmasqhost]] | chrony | `10.10.10.1` | chronyd enabled for the first time. |
| [[managed01]] | chrony | [[ansible01]] | |
| [[vcenter01]] | ntpd (VAMI timesync: NTP) | [[ansible01]] | The appliance's `ntp.conf` already has `tinker panic 0`. |
| [[esxi01]] | ntpd | [[ansible01]] | |

Every chrony node uses `makestep 1.0 -1`: step the clock whenever it is off by more than 1 s, not
only during the first three updates.

**Operations:** shut VMs down instead of suspending them. esxi01 has autostart enabled. On boot it
starts ansible01, then managed01, then vcenter01. On host shutdown it runs guest shutdown in reverse
order, giving vcenter01 600 s. dnsmasqhost sits outside esxi01, so power it on first and off last.

---

## Rationale

- A clock that boots correct and has a real upstream stays correct. An undisciplined clock inside
  a VM that gets suspended does not.
- Every VM runs on Precision7730, so it is up whenever the lab is.
- dnsmasqhost runs beside esxi01 in Workstation, so it takes time straight from the host. A suspend
  test (below) showed that a node following a server that can freeze gets dragged backward with it.
- `makestep 1.0 -1`, because a resumed guest can be minutes or hours behind. chrony's default only
  steps early after startup, and slewing a 3.8 h error would take about two days.
- Shutdown over suspend, because a boot reads the virtual hardware clock and starts NTP with no
  stale history. There is nothing to recover from.

---

## Consequences

Advantages

- Every node agrees with the others within about 0.15 s and with real time within about 1 s
  (checked 2026-09-15 against time.google.com, time.cloudflare.com, and time.windows.com).
- A cold shutdown and boot leaves every clock correct from the start (tested 2026-09-15).
- A suspended esxi01 can no longer pull dnsmasqhost backward.

Disadvantages

- **Windows Time is not precision-grade.** The lab runs about 1 s fast of real time. That's fine for
  the lab and for Kerberos, which tolerates 5 minutes.
- **Windows Time advertises ~8 s of dispersion for a few minutes after it starts.** Right after the
  service starts or restarts it reports about 8 s of root dispersion, and chrony (3 s limit) and
  ntpd (1.5 s limit) reject that. It halves with each poll (8.16 → 4.16 → 2.16 → 1.15 → 0.64 →
  0.38 s at a 64 s poll), and nodes hold their time until then. At a 1024 s poll it settles near
  1.1 s, which leaves little headroom under ntpd's limit - see [[Known-Issues]].
  `LocalClockDispersion` does not help; it only applies when Windows runs on its own CMOS clock.
- **Suspending esxi01 still costs accuracy.** After a 5.5-minute test suspend, the nested nodes came
  back 330 s behind. They recovered in stages: ansible01 after about 6.5 minutes, managed01 after
  about 12, and vcenter01 after about 15. chrony and ntpd distrust a source until the pre-suspend
  samples age out. Accepted; shut down instead where practical.
- **Precision7730 is the only time source.** If Windows Time stops, the lab drifts together again.
- **The Windows-side settings live outside the repo.** They have to be reapplied if the host is
  rebuilt.

---

## Related

- [[NTP Hierarchy]]
- [[chrony]]
- [[Precision7730]]
- [[ansible01]]
- [[managed01]]
- [[dnsmasqhost]]
- [[esxi01]]
- [[vcenter01]]
- [[Known-Issues]]
- [[Troubleshooting]]
- [[2026-09-07]]
- [[2026-09-15]]
