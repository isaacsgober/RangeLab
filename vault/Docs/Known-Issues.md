# Known Issues & Limitations

Open problems and accepted limitations — things that are not bugs to fix right now, either
because nothing depends on them yet or because the constraint is deliberate. Issues that
were diagnosed **and fixed** live in [[Troubleshooting]].

---

## dnsmasqhost answers NXDOMAIN to AAAA queries for lab hosts

**Status:** open. Worked around on [[vcenter01]] only.

For every lab name checked (`esxi01`, `vcenter01`, `ansible01`), [[dnsmasqhost]] answers A
queries correctly but answers AAAA queries with `rcode = NXDOMAIN`. The correct reply is
`NOERROR` with no answer. NXDOMAIN means the name doesn't exist at all, so a caching resolver
that stores it will refuse the A record as well. That is what broke vCenter's add-host
([[Troubleshooting]] → 2026-09-15).

vcenter01 is protected by local `host-record` entries. Other clients are not: any client that
caches negative answers and looks up AAAA can hit the same failure.

Check: `nslookup -debug -type=AAAA esxi01.rangelab.local. 10.10.10.2` — read `rcode`.
Next step: find how dnsmasqhost defines the lab records, fix it there, then decide whether the
vcenter01 workaround is still needed.

---

## vcenter01 resolver changes are hand-edited and not durable

**Status:** accepted for now. Re-verify after any VAMI network change, reboot, or upgrade.

The add-host fix lives in appliance files that VCSA's own tooling doesn't manage:

- `/etc/dnsmasq.conf`: `host-record` entries and `neg-ttl=10`. The original is saved as
  `/etc/dnsmasq.conf.bak-rangelab`. The two `server=` lines added alongside them turned out to
  be redundant.
- `/etc/systemd/resolved.conf`: `DNS=10.10.10.2` / `Domains=rangelab.local`, appended
  2026-09-14. VMware's own `DNS=127.0.0.1` appears earlier in the same `[Resolve]` section.
  systemd appends repeated list values, so the effective list is `127.0.0.1 10.10.10.2`.
  Harmless, but it should be collapsed to one deliberate line, or reverted since it fixed
  nothing.

Both edits survived a full vcenter01 reboot on 2026-09-15. A VAMI network change or an
appliance upgrade could still regenerate them.

If the add-host failure returns, run `nslookup esxi01.rangelab.local 127.0.0.1` on vcenter01
first.

---

## Suspending esxi01 costs nested VMs up to 15 minutes of wrong time

**Status:** accepted. Prefer shutting down.

Suspending [[esxi01]] freezes the clocks of [[ansible01]], [[managed01]], and [[vcenter01]]. On
resume, each one is behind by however long the suspend lasted. chrony and ntpd won't use their
source again until the pre-suspend samples age out. After a 5.5-minute test suspend on 2026-09-15,
the nodes recovered in stages: ansible01 after about 6.5 minutes, managed01 after about 12, and
vcenter01 after about 15. A shutdown and boot avoids this entirely; see
[ADR-0004](../Architecture/Decision%20Records/ADR-0004%20-%20Lab%20time%20source.md).

---

## Little headroom between Windows Time dispersion and ntpd's limit

**Status:** open, with an optional fix.

[[esxi01]] and [[vcenter01]] run ntpd, which rejects a source whose root distance is over 1.5 s.
[[ansible01]] passes on the dispersion it receives from [[Precision7730]]. With Windows Time
polling every 1024 s (`MaxPollInterval = 10`), that settles near 1.1 s, leaving about 0.4 s of
headroom. At a 64 s poll it settled at 0.35 s.

Fix: on Precision7730, set
`HKLM\SYSTEM\CurrentControlSet\Services\W32Time\Config\MaxPollInterval` to `6`, then restart
Windows Time. Expect about 5 minutes of 8 s dispersion after the restart.

---

## esxi01 DCUI shows the short hostname

The esxi01 console (DCUI) banner shows `esxi01` rather than the FQDN
`esxi01.rangelab.local`. `esxcli system hostname get` reports the domain and FQDN correctly,
so the configuration is right — this is display-only, no functional impact.

---

## No offline path for Ansible content outside ansible-core

**Status:** accepted; workarounds in place. Candidate for its own ADR.

Lab nodes install packages only from the mounted Rocky 10.2 DVD
([[ADR-0003 - Local ISO package repository]]), and VMnet10 has no route off-subnet. The DVD
ships `ansible-core` but none of:

- **`ansible.posix`** — provides `authorized_key`. `site.yml` manages
  `~labadmin/.ssh/authorized_keys` directly with `ansible.builtin.file` + `ansible.builtin.copy`
  instead.
- **`ansible-lint`** — checklist L59. Deferred until there is an install path.
- **`yamllint`** — same.

Both `pip` and `ansible-galaxy` need an index the subnet cannot reach. Getting these onto
[[ansible01]] means staging them from a connected machine — `pip download` wheels or a
downloaded collection tarball, copied over `scp` and installed with `--no-index`. Not yet
attempted.

---

## vCenter evaluation license expires 2026-11-07

Administration → Licensing shows an Evaluation license. vCenter needs a real license, or the
appliance needs rebuilding, before then.
