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
hostname it was connecting to. The DNS inconsistency was investigated but appears unrelated, as resolution succeeds via the path systemd-resolved actually uses.

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