# Troubleshooting Log

_Add an entry every time something breaks and gets fixed. Phase 2 requires at least one
entry; Phase 6 wants DNS, SSH, and at least one Ansible issue covered._

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