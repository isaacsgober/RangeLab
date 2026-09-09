# Known Issues & Limitations

Open problems and accepted limitations — things that are not bugs to fix right now, either
because nothing depends on them yet or because the constraint is deliberate. Issues that
were diagnosed **and fixed** live in [[Troubleshooting]].

---

## vCenter cannot add esxi01 as a managed host

**Status:** deferred. Nothing on the checklist needs vCenter to manage the host; VMs are
created through the ESXi host web UI.

The "Add standalone host" task fails at ~80%:
`Unable to push CA certificates and CRLs to host esxi01.rangelab.local` (a retry returned a 503).

Ruled out: time skew (~3 s), certificate services (`vmcad`/`vmafdd`/`vmware-certificateauthority`
all running), disk exhaustion on esxi01, and a DNS inconsistency that proved to be on a
resolution path VCSA doesn't actually use.

**Leading hypothesis (unconfirmed):** esxi01 still presents its install-time self-signed
certificate with CN `localhost.localdomain`. The FQDN was configured correctly later the
same day but the certificate was never regenerated. Candidate fix: regenerate the host
certificate (`/sbin/generate-certificates` or the host UI), restart `hostd`/`vpxa`, retry.

Full diagnosis: [[Troubleshooting]] → "2026-09-06 — vCenter unable to add ESXi host".

---

## vcenter01 has no configured time source

The lab now runs NTP ([[chrony]] on [[ansible01]], serving `10.10.10.0/24`), but
[[vcenter01]] is not a client of it and has no other enforced time source. On 2026-09-06 its
clock and esxi01's agreed within ~3 s, but nothing keeps them synced. This will matter more
at the Active Directory / Kerberos stage.

Options: point the VCSA at [[ansible01]], point it at [[esxi01]] (enable NTP there first), or
accept the drift and document it until the AD work. See [[vCenter]] (its Dependencies note
already flags this).

---

## esxi01 DCUI shows the short hostname

The esxi01 console (DCUI) banner shows `esxi01` rather than the FQDN
`esxi01.rangelab.local`. `esxcli system hostname get` reports the domain and FQDN correctly,
so the configuration is right — this is display-only, no functional impact. Possibly the
same install-time root as the certificate issue above.
