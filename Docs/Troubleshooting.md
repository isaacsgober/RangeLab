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