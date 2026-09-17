# Troubleshooting Log

_Add an entry every time something breaks and gets fixed. Phase 2 requires at least one
entry; Phase 6 requires DNS, SSH, and at least one Ansible issue covered.

## Entry template

### [Date] — [Short title]

**System(s) affected:**

**Symptom:**

**Diagnosis steps:**

**Root cause:**

**Fix:**

**Verification:**

---

### 2026-09-05 — DNS Resolution Failure

**System(s) affected:**
[[esxi01]], [[vcenter01]], [[dnsmasqhost]]

**Symptom:**
vCenter VAMI 503, name resolution failing between hosts.

**Diagnosis steps:**
Successfully pinged [[10.10.10.2]]
Viewed `systemctl status dnsmasq`
Checked [[dnsmasq]] logs; found message "`unknown interface ens160`". 
Checked status of interface ens160; interface was up.

**Root cause:**
Startup race; [[dnsmasq]] was attempting to start before ens160 was up.

**Fix:**
Edited dnsmasq.conf:
	Replaced `bind-interfaces` command with `bind-dynamic`.

**Verification:**
Rebooted [[dnsmasqhost]], and verified DNS functionality from all hosts.
From Precision 7730:
``` cmd
C:\>nslookup vcenter01.rangelab.local 10.10.10.2
Server:  dnsmasqhost.rangelab.local
Address:  10.10.10.2

Name:    vcenter01.rangelab.local
Address:  10.10.10.15


C:\>nslookup 10.10.10.15 10.10.10.2
Server:  dnsmasqhost.rangelab.local
Address:  10.10.10.2

Name:    vcenter01.rangelab.local
Address:  10.10.10.15
```

VAMI recovered without further intervention.

---

### 2026-09-06 — vCenter unable to add ESXi host

> **Resolved 2026-09-15 — see that entry below.** The certificate hypothesis here was wrong.
> The real lead was already in this entry's diagnosis: `nslookup` getting NXDOMAIN from
> 127.0.0.1, which is VCSA's embedded dnsmasq rather than systemd-resolved.

**System(s) affected:**
[[vcenter01]], [[esxi01]]

**Symptom:**
"Add standalone host" task (to add [[esxi01]] to vCenter) failed at approximately 80% completion:
`A general system error occurred: Unable to push CA certificates and CRLs to host esxi01.rangelab.local`

A later attempt failed differently:
`A general system error occurred: Error: system_error Messages: vapi.invalid.result.code<Recv of frame failed with code: 503 Service Unavailable>`

**Diagnosis steps:**

Ruled out time skew:
	compared `date` on vcenter01 against `esxcli system time get`
	on esxi01; hosts agreed within ~3 seconds.

Ruled out certificate service failure:
	`service-control --status` on vcenter01 showed `vmcad`, `vmafdd`, and 
	`vmware-certificateauthority` (relevant to first attempt failure) all running.
	Learned that services (`vmcam`, `vmware-imagebuilder`, `vmware-netdumper`, 
	`vmware-rbd-watchdog`, `vmware-vcha`, `liagent`, `vc-salt`) are optional components 
	not involved in host attachment.

Ruled out disk exhaustion on esxi01:
	`vdf -h` showed all ramdisks well under capacity
	(`/tmp` at 0%, `/etc` at 9%, root at 25%).

Investigated name resolution from vcenter01. Found inconsistent behavior:
	 `nslookup esxi01.rangelab.local` ret. NXDOMAIN from the local stub resolver at 127.0.0.1
	 `nslookup esxi01.rangelab.local 10.10.10.2` ret. 10.10.10.10 (correct)
	 `resolvectl query esxi01.rangelab.local` resolves correctly via eth0
	 `resolvectl flush-caches` did not correct this behavior

Confirmed correct VAMI settings (DNS server set manually to 10.10.10.2).
`/etc/resolv.conf` lists `nameserver 127.0.0.1` before `nameserver 10.10.10.2`;
Learned that this loopback entry is inserted by systemd-resolved, which VCSA uses for internal
service discovery.

On each attempt, the vSphere Client showed a certificate warning which showed the
host's certificate with Common Name `localhost.localdomain`. This was the default self-signed
certificate generated at ESXi install time, before the host's FQDN was configured.

**Root cause:**
UNCONFIRMED: The host was presenting a default certificate issued for `localhost.localdomain` rather than `esxi01.rangelab.local`, which vCenter could not reconcile with the 
hostname it was connecting to. ~~The DNS inconsistency was investigated but appears unrelated, as resolution succeeds via the path systemd-resolved actually uses.~~

**Fix:**
Deferred; not a priority at this point in the project.

**Verification:**
N/A

**Notes:**
The host's FQDN was configured earlier the same day (`esxcli system hostname get`
reported correct values), but the certificate was not regenerated at that time and
still carried the installation-time common name.

---

### 2026-09-08 — Persistent journald not activating after Ansible deploy

**System(s) affected:**
[[ansible01]], [[managed01]] — Phase 3 playbook (`Ansible/site.yml`)

**Symptom:**
The playbook deployed `/etc/systemd/journald.conf.d/rangelab.conf` (`Storage=persistent`)
and its handler restarted `systemd-journald`. The run was green — every task `ok`/`changed`,
handler fired — but `/var/log/journal/` did not exist and `journalctl` was still writing to
`/run/log/journal/` (volatile).

**Diagnosis steps:**
- `file rangelab.conf` → `ASCII text` (ruled out a UTF-8 BOM).
- `cat -A rangelab.conf` → `[Journal]^M$` / `Storage=persistent^M$` — CRLF line endings. The
  file was authored on Windows and `scp`'d straight over, bypassing git's `eol=lf`
  normalisation (still untracked).
- After the CRLF fix, `systemd-analyze cat-config systemd/journald.conf` confirmed journald
  was merging the drop-in and `Storage=persistent` was in effect.
- `journalctl --header` still showed `/run/log/journal/…` with a correct config and a fresh
  `systemctl restart systemd-journald`.
- `systemctl status systemd-journald` confirmed the handler's restart had actually happened.
- Manually created `/var/log/journal` and restarted journald — still volatile.

**Root cause:**
Two issues stacked.
1. CRLF in the drop-in: journald read `Storage=persistent\r`, did not recognise the value,
   and fell back to `auto` — which only uses `/var/log/journal/` if it already exists.
2. Even with a correct config, a live `systemctl restart systemd-journald` does not complete
   the volatile→persistent migration on RHEL-family. That is a boot-time sequence:
   `systemd-tmpfiles-setup` creates the directory, `systemd-journald` starts against it,
   `systemd-journal-flush` moves the runtime logs to disk.

**Fix:**
- Converted `Ansible/files/journald-rangelab.conf` to LF endings with a trailing newline;
  re-`scp`'d.
- Added a `file` task to `site.yml` creating `/var/log/journal` (`mode: "2755"`,
  `group: systemd-journal`) and a second handler running `journalctl --flush`. Handlers are
  ordered restart-then-flush (handlers run in definition order, not `notify` order).

**Verification:**
- [[managed01]]: rebooted → `journalctl --header` shows `/var/log/journal/…`.
- [[ansible01]]: not rebooted. Ran the updated playbook — the new task and handlers reached
  persistent storage with no reboot. Third run: `changed=0` on both hosts, no handlers.

**Notes:**
`.gitattributes` (`* text=auto eol=lf`) only normalises during git operations. An untracked
file copied out-of-band keeps its Windows endings — the reason this file must be committed,
and an argument for `git`-based sync over raw `scp`.

---

### 2026-09-08 — Duplicate machine-id on cloned node

**System(s) affected:**
[[managed01]] (cloned from [[ansible01]])

**Symptom:**
Both hosts' persistent journal directories were named
`/var/log/journal/49098572b4a2433c8cae4c8ed299ac21/` — the same machine ID.
`cat /etc/machine-id` was identical on both.

**Diagnosis steps:**
Compared `/etc/machine-id` on each host. The 2026-09-06 clone was meant to reset it (with hostname, IP, SSH host keys) but the reset did not occur.

**Root cause:**
[[managed01]] kept `/etc/machine-id` from the [[ansible01]] clone; it was never regenerated.

**Fix:**
On [[managed01]]:
```
sudo rm -f /etc/machine-id
sudo systemd-machine-id-setup
sudo reboot
```

**Verification:**
[[managed01]] `/etc/machine-id` is now `29f938c8ef834cd983295458147d28c1`, distinct from
[[ansible01]]. A new journal directory was created under the new ID; the stale `49098572…`
directory was rm'd.

**Notes:**
No functional impact in the current lab (static addressing, no central journal collection), but a shared machine-id collides for anything that assumes it is unique. Clone generalization (machine-id, SSH host keys, hostname, IP) should be a documented, verified checklist — see `Ansible/README.md`.

---

### 2026-09-15 — vCenter unable to add ESXi host (resolved)

Resolves the 2026-09-06 entry above. Investigated 2026-09-14 → 2026-09-15.

**System(s) affected:**
[[vcenter01]], [[esxi01]], [[dnsmasqhost]]

**Symptom:**
"Add standalone host" for `esxi01.rangelab.local` stalled at 80% ("Retrieving data from
vCenter agent") for ~15 minutes, then failed:
`A general system error occurred: Unable to push CA certificates and CRLs to host esxi01.rangelab.local`

For the whole stall, `vpxd.log` repeated this every ~31 s:
```
[TrustedInfrastructure.HostConfig] Failed to collect uploaders for host esxi01.rangelab.local.
  vapi.invalid.result.code<Recv of frame failed with code: 503 Service Unavailable>
[TrustedInfrastructure.HostConfig] PrepareHostSecurity attempt N failed. Retrying ...
```
Some attempts left a host object in the inventory, stuck in `DISCONNECTED`.

**Diagnosis steps:**

Traced the 503. The failing call was `/hgw/host-NNNN/api` — vCenter's host gateway
(`vmware-envoy-hgw`) forwarding a vAPI request to the host. Envoy's access log showed it
never picked a destination at all:
```
POST /hgw/host-5008/api 503 no_healthy_upstream UH 31000ms
```
vpxd creates that route when the add starts, and the route finds the host by DNS name (its
cluster config carries `dns_refresh_rate`). Everything on esxi01 was healthy: `hostd`,
`vpxa`, `envoy`, and `apiForwarder` (8098) were listening, and `hostd.log` showed vpxd's
session arriving. vCenter could reach the host. The gateway couldn't resolve its name.

Compared resolution paths on vcenter01:
```
getent ahosts esxi01.rangelab.local         → 10.10.10.10   (NSS → systemd-resolved)
nslookup esxi01.rangelab.local 127.0.0.1    → NXDOMAIN
nslookup esxi01.rangelab.local 10.10.10.2   → 10.10.10.10
```
`/etc/resolv.conf` lists `nameserver 127.0.0.1` first. `ss -lnup` showed that 127.0.0.1:53
is **VCSA's own embedded dnsmasq**, not systemd-resolved (whose stub is 127.0.0.53 — this
corrects the 2026-09-06 note). Envoy queries the `resolv.conf` nameservers itself instead of
going through NSS. `getent` succeeded even when run as the `envoy-hgw` user, while the
gateway still had no endpoint. `curl` through VCSA's Envoy system proxy showed the same
split: esxi01 by hostname hung for 20 s, by IP it answered in 30 ms. Anything using NSS kept
working, which made the fault look intermittent.

Read the embedded dnsmasq's query log (`/var/log/vmware/dnsmasq.log`):
```
query[A] esxi01.rangelab.local from 127.0.0.1
cached esxi01.rangelab.local is NXDOMAIN
```
It was answering an A query from a *negative* cache entry, although 10.10.10.2 serves that A
record correctly. The cached NXDOMAIN had to come from a query of another type.

Checked what dnsmasqhost returns for AAAA:
```
nslookup -debug -type=AAAA esxi01.rangelab.local. 10.10.10.2     → rcode = NXDOMAIN
nslookup -debug -type=AAAA vcenter01.rangelab.local. 10.10.10.2  → rcode = NXDOMAIN
nslookup -debug -type=AAAA ansible01.rangelab.local. 10.10.10.2  → rcode = NXDOMAIN
nslookup -debug -type=A    esxi01.rangelab.local. 10.10.10.2     → rcode = NOERROR, 1 answer
```
This is the trailing `can't find ...: NXDOMAIN` that follows every `nslookup` against
10.10.10.2. It had been written off as a harmless IPv6 miss.

Ruled out along the way: MTU (`vmkping -I vmk0 <vcenter> -d -s 1472` passed), reverse DNS
(PTR resolves from both hosts), disk and memory (all volumes under 31%, 5.6 GiB available),
licensing (Evaluation, valid to 2026-11-07), and `vmware-imagebuilder` (started; no change).

**Root cause:**
[[dnsmasqhost]] answers **NXDOMAIN** to AAAA queries for lab hosts that only have an A
record. The correct answer is `NOERROR` with no records. NXDOMAIN means the name doesn't
exist at all, for any record type.

VCSA ships its embedded dnsmasq with `neg-ttl=3600`, so it caches negative replies for an
hour even when they carry no TTL of their own. Any AAAA lookup of esxi01 (`nslookup` sends
one automatically) left "esxi01 does not exist" in that cache, and the cache then answered
A lookups with NXDOMAIN too. 127.0.0.1 is the first nameserver, and NXDOMAIN is a final
answer, so lookups never fell through to 10.10.10.2.

With esxi01 unresolvable, every `PrepareHostSecurity` call through the gateway got a 503,
and vCenter never finished provisioning the host (esxi01's `vpxa.cfg` held no vCenter
configuration). An hourly cycle fits the intermittency: the cache entry expires, resolution
briefly works, and the next AAAA lookup poisons it again. That would explain partial
progress (a host object, a new certificate) appearing and then stalling.

**Fix:**
On [[vcenter01]], with the original config backed up to `/etc/dnsmasq.conf.bak-rangelab`:
```
# /etc/dnsmasq.conf
host-record=esxi01.rangelab.local,esxi01,10.10.10.10
host-record=vcenter01.rangelab.local,vcenter01,10.10.10.15
neg-ttl=10                                  # was 3600
server=/rangelab.local/10.10.10.2           # redundant: already forwarded there via resolv.conf
server=/10.10.10.in-addr.arpa/10.10.10.2    # same
```
```
systemctl restart dnsmasq                   # full restart clears the cache
service-control --restart vmware-envoy-hgw  # masked in systemd, so systemctl refuses it
```
`host-record` makes the embedded dnsmasq answer those names itself, for every record type.
It never forwards them, so it never picks up dnsmasqhost's bad AAAA answer. The shorter
`neg-ttl` limits the damage for other lab names.

Then removed the stale `DISCONNECTED` host object and added esxi01 by FQDN with root
credentials. (Reconnecting the old object failed with `vim.fault.InvalidLogin`.)

This was a workaround on one client. The source was fixed on dnsmasqhost later the same day,
and this workaround was then removed. See "dnsmasqhost answered NXDOMAIN to AAAA queries"
below.

**Verification:**
```
nslookup esxi01.rangelab.local 127.0.0.1   → 10.10.10.10
POST /api/vcenter/host                     → HTTP 201 in 5.37 s   (previously a 15-minute hang)
host-5017  esxi01.rangelab.local  CONNECTED   stable at t+0 / +45 / +90 s
```
vCenter now inventories `vcenter01`, `ansible01`, `managed01`, and datastores
`datastore01-01` and `datastore01-02`. The workaround survived a vcenter01 reboot before it was
removed.

**Notes:**
The same investigation turned up four other problems. Each was real, but none was the
blocker: the add kept failing the same way after each fix, until the dnsmasq change.

- **vcenter01 was CPU-starved.** 2 vCPUs, 15-minute load average 13.46. trustmanagement
  requests took 27–50 s, and VAMI returned intermittent 503s. Resized to 6 vCPU / 15 GiB
  (load ≈ 0.4).
- **`vmware-certificateauthority` and `vmware-topologysvc` were stopped.** Started both. Both
  were running on 2026-09-06; when or why they stopped is unknown.
- **A certificate problem created by the troubleshooting itself.** Adding esxi01 *by IP*, as a
  test, made VMCA reissue its certificate with only `IP Address:10.10.10.10` in the SAN.
  Re-adding by hostname then failed TLS name checking (`SSLVerifyException: Host name does
  not match the subject name(s) in certificate`). Fixed with a `certool`-issued VMCA
  certificate that carried a DNS SAN. The successful add later replaced it with VMCA's
  standard host certificate.
- **The 2026-09-14 DNS change had no effect.** Appending `DNS=10.10.10.2` to
  `/etc/systemd/resolved.conf` seemed to fix default lookups, but `nslookup` asks 127.0.0.1
  first either way; most likely the negative cache entry had just expired. The 2026-09-06
  entry had already recorded the real signature (NXDOMAIN from 127.0.0.1) and ruled it out.
  The lines were removed on 2026-09-15, after the source fix below.

---

### 2026-09-15 — Lab clocks 3 h 49 m apart

**System(s) affected:**
[[ansible01]], [[managed01]], [[vcenter01]], [[esxi01]], [[dnsmasqhost]], [[Precision7730]]

**Symptom:**
A parallel clock sweep, run to verify the 2026-09-14 NTP configuration, split the lab into two
groups (offsets from Precision7730):
```
ansible01   −13768.7 s    managed01    −13768.7 s    vcenter01   −13768.3 s
esxi01          −0.2 s    dnsmasqhost      −0.1 s
```
vcenter01 and managed01 were synchronized to ansible01. esxi01 was configured for ansible01 but
reported `Time Synchronized: false`.

**Diagnosis steps:**
- **ansible01:** `Stratum 10` from its local reference, with no sources. `chronyc clients` showed
  managed01, esxi01, and vcenter01 all polling it, and vcenter01's ntpd and managed01's chrony were
  locked to it.
- **esxi01:** ntpd running with `-g` at `stratum 16`. `ntpq` showed reach 377 to ansible01 but the
  peer wasn't selected, and the log said `no peer for too long, server running free now`.
- **dnsmasqhost:** chronyd inactive, configured for `pool 2.rocky.pool.ntp.org`, which is
  unreachable offline.
- **Precision7730:** `w32tm /query /status` → "The service has not been started". Windows Time was
  Stopped, startup type Manual.
- **ansible01's boot:** its kernel log showed `rtc_cmos 00:01: setting system clock to
  2026-09-15T03:38:02 UTC`, which was correct. VMware Tools timesync was Disabled.
- **Usage pattern:** esxi01 is regularly suspended in Workstation, sometimes with dnsmasqhost left
  running.

**Root cause:**
ansible01 was the lab's time root, with no upstream (`local stratum 10`). While esxi01 was
suspended, every VM nested inside it froze. On resume, esxi01 and dnsmasqhost, which run directly
in Workstation, were caught up to the host's clock. ansible01 had nothing to catch up from and
carried on from where it stopped, 3 h 49 m behind. vcenter01 and managed01 followed it. esxi01
refused to, because ESXi's ntpd allows one large correction at startup (`-g`) and after that refuses
corrections over 1000 s.

**Fix:**
Made [[Precision7730]] the upstream
([ADR-0004](../Architecture/Decision%20Records/ADR-0004%20-%20Lab%20time%20source.md)):
- **Precision7730:** Windows Time set to Automatic and synced to `time.windows.com`. NTP server
  enabled (`NtpServer\Enabled = 1`, `AnnounceFlags = 5`), with `MinPollInterval 6` and
  `MaxPollInterval 10`. Firewall rule allowing UDP 123 from `10.10.10.0/24`.
- **ansible01:** `server 10.10.10.1 iburst` and `makestep 1.0 -1`; `local stratum 10` removed.
- **managed01:** `makestep 1.0 -1`.
- **dnsmasqhost:** `server 10.10.10.1 iburst` and `makestep 1.0 -1`; chronyd enabled.
- **vcenter01 and esxi01:** ntpd restarted, so each took its one startup correction.

At first chrony ignored the host, because Windows advertised 8.16 s of root dispersion and chrony
rejects sources over 3 s (`chronyc selectdata` showed `d`). Setting `LocalClockDispersion = 0` had
no effect, because that value only applies when Windows runs on its own CMOS clock. The real cause
was Windows Time's sample filter starting pessimistic after the service restart. At the 64 s poll
the dispersion halved with every sample (8.16 → 4.16 → 2.16 → 1.15 → 0.64 → 0.38 s). ansible01
then selected the host and stepped +13768.6 s, and its clients followed.

**Verification:**
- Sweep at 2026-09-15 17:49Z: all six clocks within 0.35 s of each other.
- Cold shutdown and boot of esxi01 with autostart: every clock correct from boot, within 0.15 s.
  ntpd on esxi01 and vcenter01 showed `sys.peer` with `flash=00`.
- Against time.google.com, time.cloudflare.com, and time.windows.com, queried directly over NTP:
  the lab runs about 1 s fast.

**Notes:**
- **Suspend test.** A 5.5-minute suspend of esxi01 brought the nested nodes back 330 s behind.
  Recovery took about 6.5 minutes for ansible01, 12 for managed01, and 15 for vcenter01. chrony
  and ntpd distrust a source until the pre-suspend samples age out (`Jitter of 10.10.10.1 exceeds maxjitter of 1.000 seconds`).  dnsmasqhost was never suspended, but following ansible01 pulled
  its clock back 330 s, which is why it now syncs from the host directly. That cost is accepted for
  suspends, and shutting down is preferred; see [[Known-Issues]].
- **github.com's `Date` header is not a clock reference.** It is served from a CDN cache and once
  read 10 s off. Query NTP servers directly.
- **SSH drops during the suspend test** were OpenSSH 9.9's per-source penalties (`drop connection
  ... penalty: exceeded LoginGraceTime`). Connections that could not finish logging in while esxi01
  was frozen counted against this host's address, and sshd refused it until the penalty expired.

---

### 2026-09-15 — dnsmasqhost answered NXDOMAIN to AAAA queries

Source of the vCenter add-host failure above. Tracked as Linear ISA-6.

**System(s) affected:**
[[dnsmasqhost]] and every lab DNS client; [[vcenter01]] is where it broke something.

**Symptom:**
For every lab name, dnsmasqhost answered A queries with the right address but answered AAAA
queries with `NXDOMAIN`, meaning "this name does not exist". vCenter's embedded dnsmasq cached
that and then refused esxi01's A record too, which stalled add-host (entry above).

**Diagnosis steps:**
All lab names are defined in `/etc/dnsmasq.conf` (dnsmasq 2.90). `/etc/dnsmasq.d/` is empty and
`/etc/hosts` is stock.
```
domain=rangelab.local
local=/rangelab.local/
local=/10.10.10.in-addr.arpa/
address=/esxi01.rangelab.local/10.10.10.10
ptr-record=10.10.10.10.in-addr.arpa,esxi01.rangelab.local
# ...one address= / ptr-record= pair per host
```
Queried more than A and AAAA with `dig @10.10.10.2`:
```
esxi01.rangelab.local       A     NOERROR   10.10.10.10
esxi01.rangelab.local       AAAA  NXDOMAIN
esxi01.rangelab.local       MX    NXDOMAIN
esxi01.rangelab.local       TXT   NXDOMAIN
foo.esxi01.rangelab.local   A     NOERROR   10.10.10.10
nosuch.rangelab.local       A     NXDOMAIN
dig -x 10.10.10.10                NOERROR   esxi01.rangelab.local.
```
Only A queries and PTR lookups worked, and a subdomain that doesn't exist resolved to esxi01.
Both point at `address=`. The manual on the server (`zcat /usr/share/man/man8/dnsmasq.8.gz`)
describes `--address` as supplying an address for any host in the given domains. It also notes
a change in 2.86 for queries of other record types: "From 2.86, the query is sent upstream."

**Root cause:**
`address=/esxi01.rangelab.local/10.10.10.10` is a rule for a domain, not a record for a host. It
answers A queries for that name and every name under it, and nothing else. Since 2.86, a query of
any other type skips the rule and is handled by the next rule that matches. Here that was
`local=/rangelab.local/`, which answers only from local data and has no upstream, so it replied
NXDOMAIN. The manual says only that such queries go upstream; the NXDOMAIN is what `local=` was
observed to do with them.

**Fix:**
On dnsmasqhost, with the original saved as `/etc/dnsmasq.conf.bak-rangelab`, replaced the ten
`address=` / `ptr-record=` lines with one line per host:
```
host-record=dnsmasqhost.rangelab.local,10.10.10.2
host-record=esxi01.rangelab.local,10.10.10.10
host-record=vcenter01.rangelab.local,10.10.10.15
host-record=ansible01.rangelab.local,10.10.10.20
host-record=managed01.rangelab.local,10.10.10.21
```
```
dnsmasq --test              # syntax check OK
systemctl restart dnsmasq
```
`host-record` defines the name itself, with its A record and matching PTR. A query for a type the
name doesn't have gets `NOERROR` with no answer.

Then, on vcenter01, restored the stock `/etc/dnsmasq.conf` from `.bak-rangelab` and restarted
dnsmasq. The workaround is kept as `/etc/dnsmasq.conf.workaround-rangelab`. Removing it was the
only way to show that the source fix works on its own.

**Verification:**
From dnsmasqhost (`dig @10.10.10.2`), for all five lab names:
```
A       → NOERROR, the host's address        AAAA → NOERROR, no answer
MX, TXT → NOERROR, no answer                 PTR  → one record each
foo.esxi01.rangelab.local A → NXDOMAIN   (the subdomain match is gone)
nosuch.rangelab.local A     → NXDOMAIN   (unknown names still fail correctly)
```
From Precision7730, `nslookup -debug -type=AAAA <name>.rangelab.local. 10.10.10.2` showed
`rcode = NOERROR` for all five names.

On vcenter01, with the stock embedded dnsmasq (`neg-ttl=3600`), three rounds of AAAA then A:
```
dig @127.0.0.1 esxi01.rangelab.local AAAA   → NOERROR, no answer
dig @127.0.0.1 esxi01.rangelab.local A      → 10.10.10.10
dnsmasq.log: cached esxi01.rangelab.local is NODATA-IPv6
curl https://esxi01.rangelab.local/ through the Envoy proxy → HTTP 200 in 0.04 s
```
Over the next five minutes (19:22–19:27Z), vCenter's API kept showing
`esxi01.rangelab.local CONNECTED`. The host gateway logged 100 requests to esxi01 with no 503s.
The embedded dnsmasq handled 3,942 queries and cached 67 `NODATA-IPv6` answers, with no NXDOMAIN
for any lab host.

**Notes:**
- A cached `NODATA-IPv6` answer only says "no IPv6 address". It doesn't affect the A lookup, so the
  stock `neg-ttl=3600` is harmless now.
- The manual's own way to restore the old behavior is an extra `local=/<name>/` line for each
  `address=` name. `host-record` was chosen instead because it is a real host record and doesn't
  match subdomains.
- The `server=` lines and `neg-ttl=10` on vcenter01 went away with the rest of the workaround.
- Also removed the 2026-09-14 `DNS=10.10.10.2` / `Domains=rangelab.local` lines from vcenter01's
  `/etc/systemd/resolved.conf` (backup `.bak-rangelab`). VAMI already sets both on the
  interface, so `resolvectl status` and `/etc/resolv.conf` still list `10.10.10.2` and
  `search rangelab.local`. `getent`, `resolvectl query`, `dig @127.0.0.1`, and the Envoy proxy
  all still resolved esxi01 afterward. vcenter01's DNS configuration is now entirely stock.

---

### 2026-09-15 — esxi01 DCUI shows the short hostname (expected behavior)

**System(s) affected:**
[[esxi01]]

**Symptom:**
The DCUI welcome screen reads `To manage this host, go to: https://esxi01/`, followed by
`https://10.10.10.10/ (STATIC)`, rather than `https://esxi01.rangelab.local/`.

**Diagnosis steps:**
Reproduced it over SSH rather than at the console. `dcui` runs inside an SSH session, so the
screen can be captured from a pseudo-terminal:
```
ssh -tt root@esxi01.rangelab.local "stty rows 30 cols 100; TERM=xterm dcui"
```
Every name setting already had the FQDN:
```
esxcli system hostname get   Host Name: esxi01   Domain Name: rangelab.local
                             Fully Qualified Domain Name: esxi01.rangelab.local
hostname                     esxi01.rangelab.local
/Misc/HostName               esxi01.rangelab.local
/etc/hosts                   10.10.10.10  esxi01.rangelab.local esxi01
DNS                          server 10.10.10.2, search rangelab.local
                             PTR 10.10.10.10 → esxi01.rangelab.local
```
Checked Broadcom KB 406630: when the Default TCP/IP Stack has no domain name, ESXi puts the
short name in certificate requests. Not the case here. `vim-cmd hostsvc/net/info` shows the
default stack with `hostName = "esxi01"` and `domainName = "rangelab.local"`.

Tried `strace` on `dcui` to see where the name comes from. ESXi refuses (`Ptrace is disabled`),
and that security control was left on.

Tested the two ways a name lookup could produce the URL instead:
- **Hosts file.** ESXi checks `files` before `dns`. Temporarily changed the `/etc/hosts` line to
  `10.10.10.10 esxi01.hoststest.invalid esxi01`, started `dcui`, then restored the file (its
  checksum matched the backup). The screen still showed `https://esxi01/`.
- **DNS.** Captured port 53 on vmk0 (`tcpdump-uw -i vmk0 -n port 53`) while `dcui` started. The
  only queries were ntpd's lookups of `ansible01.rangelab.local`; nothing for esxi01 or its PTR
  record.

**Root cause:**
Nothing is misconfigured. The DCUI doesn't look the name up; it prints the host's configured host
name. ESXi stores the name in two fields (`hostName = "esxi01"`, `domainName = "rangelab.local"`).
`esxcli system hostname set --host` accepts only letters, numbers, and hyphens, so the host-name
field can't hold an FQDN. The short URL is how the DCUI on this build (ESXi 9.1.0, build 25557999)
presents a correctly configured host.

**Fix:**
None needed. Removed the entry from [[Known-Issues]].

**Verification:**
The two tests above: changing what 10.10.10.10 resolves to didn't change the screen, and the DCUI
sent no DNS queries for the host.

**Notes:**
- `https://esxi01/` doesn't open from [[Precision7730]]. Windows doesn't add `rangelab.local` to
  single-label names, so `curl https://esxi01/` couldn't resolve the host. Use
  `https://esxi01.rangelab.local/` or the IP.
- The ESXi Host Client, vCenter, and the host certificate all use the FQDN. The short DCUI URL
  affects nothing else.

---

### 2026-09-15 — Root SSH to vcenter01 rejected with the correct password

Happened 2026-09-14; diagnosed 2026-09-15 from vcenter01's journal. All times are UTC.

**System(s) affected:**
[[vcenter01]]

**Symptom:**
On 2026-09-14, `ssh root@vcenter01.rangelab.local` rejected a password that worked at the VM
console a few minutes later. The work continued from the console. By the next night SSH logins
worked again, and nothing had been changed.

**Diagnosis steps:**
First suspected OpenSSH per-source penalties, which had dropped connections to ansible01 and
managed01 during the 2026-09-15 suspend test. Ruled out: vcenter01 runs OpenSSH 9.3 (`sshd -V`),
and per-source penalties arrived in 9.8. ansible01 runs 9.9p1, with
`persourcepenalties ... authfail:5 noauth:1 grace-exceeded:10`.

Read sshd's log for that evening (`journalctl -u sshd --since "2026-09-14 12:00"`):
```
2026-09-14 18:02:12  pam_mgmt_cli(sshd:auth): auth script returned error (251): Error getting authentication cookie from applmgmt service.
2026-09-14 18:02:12  pam_unix(sshd:auth): authentication failure; ... rhost=10.10.10.1  user=root
2026-09-14 18:02:17  error: PAM: Authentication failure for root from 10.10.10.1
2026-09-14 18:02:59  error: PAM: Authentication failure for root from 10.10.10.1
2026-09-14 18:04:04  error: PAM: Authentication failure for root from 10.10.10.1
2026-09-15 04:46:02  Accepted keyboard-interactive/pam for root from 10.10.10.1
```
Only the first attempt logged a `pam_unix` failure. The next two failed without one, so the
password check itself didn't fail; something else did.

Searched the full journal for the same window for authentication and lockout events:
```
17:59:44  python[10847]: pam_unix(passwd:auth): authentication failure; ... user=root
18:01:54  python[10847]: pam_unix(passwd:auth): authentication failure; ... user=root
18:01:58  python[10847]: pam_unix(passwd:auth): authentication failure; ... user=root
18:01:58  python[10847]: pam_faillock(passwd:auth): Consecutive login failures for user root account temporarily locked
18:07:29  login[77520]: ROOT LOGIN  on '/dev/tty1'
```
PID 10847 is `applmgmt`, the appliance management service behind the VAMI (`applmgmt.log`
entries carry the same PID).

Read the lockout policy and the PAM stacks:
```
/etc/security/faillock.conf          deny = 3, even_deny_root, root_unlock_time = 300, fail_interval = 900
/etc/pam.d/system-auth               pam_faillock preauth → pam_unix → pam_faillock authfail
/etc/pam.d/sshd, /etc/pam.d/login    pam_mgmt_cli (appliance ticket) first, then include system-auth
```

**Root cause:**
`pam_faillock` locked root. Three failed root password checks through `applmgmt`, starting at
17:59:44, reached the appliance's limit (`deny = 3` within 15 minutes). `even_deny_root` applies
that limit to root, with a 5-minute lock. The SSH attempts at 18:02–18:04 arrived during the lock.
`pam_faillock preauth` refuses a locked account whatever password is typed, which is why the later
attempts failed with no `pam_unix` failure. The appliance's ticket module (`pam_mgmt_cli`) errored
on every SSH attempt, so sshd fell through to the locked `system-auth` path each time.

The console login at 18:07:29 succeeded. The logs don't show whether the lock had lapsed by then,
or whether the console took the `pam_mgmt_cli` path, which runs before `pam_faillock` in
`/etc/pam.d/login` and logged no error that time. They also don't show where the first three bad
passwords were typed. Those checks went through `applmgmt`, which serves both the VAMI login page
and the appliance's own SSH ticket check.

**Fix:**
None needed. The lock expired on its own, which is why SSH seemed to start working by itself. To
check for or clear a lock on the appliance:
```
faillock --user root           # recent failures; 3 within 15 minutes means locked
faillock --user root --reset   # clear them now instead of waiting
```

**Verification:**
On 2026-09-15, `faillock --user root` shows 0 failures, and root SSH logins are accepted.

**Notes:**
- On a hardened Linux host, "the correct password is rejected" often means a lockout, not a typo.
  Check `faillock` and the journal's `pam_faillock` lines before retrying: while the lock lasts, no
  password gets through.
- Check the OpenSSH version before blaming per-source penalties (`sshd -V`; they need 9.8 or
  later). They were the cause on the Rocky nodes but couldn't be on vcenter01.
---

### 2026-09-17 — vyos01's DNS forwarder returned SERVFAIL to every client

**System(s) affected:**
[[vyos01]], [[infra01]]

**Symptom:**
`sudo dnf makecache` on a freshly installed infra01 failed with
`Could not resolve host: mirrors.rockylinux.org`. vyos01 itself resolved names normally.

**Diagnosis steps:**
On infra01: `/etc/resolv.conf` held `nameserver 10.10.10.3` and `search rangelab.internal`; the
default route was via `10.10.10.3`; `ping 10.10.10.3` and `ping 1.1.1.1` both replied. So
addressing, routing, and NAT were all working, and only name resolution failed.
On vyos01: `show dns forwarding statistics` showed the recursor running with 26 cached entries.
`dig @192.168.132.2 rockylinux.org +short` answered `76.223.126.88` — upstream worked.
`dig @10.10.10.3 rockylinux.org +short` returned nothing — the forwarder did not.
`dig @10.10.10.3 rockylinux.org` gave `status: SERVFAIL` after **1505 ms**.
First hypothesis, wrong: DNSSEC records could not cross Workstation's NAT DNS proxy.
`dig @192.168.132.2 . DNSKEY +dnssec` disproved it — 1143 bytes came back with RRSIGs and EDNS
intact. What that query did show was its own cost: **2201 ms**.

**Root cause:**
A latency budget, not a misconfiguration. `service dns forwarding` is a PowerDNS Recursor, which
validates DNSSEC — one client query becomes several upstream round trips to build the chain — and
its default `network-timeout` is 1500 ms. Workstation's NAT DNS proxy at `192.168.132.2` answers,
but slowly enough (2201 ms measured cold) that the recursor gave up and returned SERVFAIL. The
router's own lookups were unaffected because they use `system name-server` and go straight out,
one query, no validation chain, with dig's far longer timeout.

**Fix:**
Point the forwarder at public resolvers instead, reached across the same NAT path:

```
delete service dns forwarding name-server 192.168.132.2
set service dns forwarding name-server 1.1.1.1
set service dns forwarding name-server 1.0.0.1
set system name-server 1.1.1.1
```

`system name-server` was moved as well, so the router's own lookups and the lab's take the same
path and Workstation's DNS proxy is out of the lab entirely.

**Verification:**
`dig @10.10.10.3 rockylinux.org` → `status: NOERROR`, 32 ms.
`sudo dnf makecache` on infra01 → metadata cache created in 12 s.

**Lesson:**
Stage 1's checks proved the *router* could resolve and stopped there. `system name-server` and
`service dns forwarding` are independent settings, so that proved nothing about clients. A
`dig @10.10.10.3` from the router would have caught this before infra01 existed; it is now a
required check in [[Build-Sequence]] 1.5.
