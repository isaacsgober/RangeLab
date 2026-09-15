# Known Issues & Limitations

Open problems and accepted limitations — things that are not bugs to fix right now, either
because nothing depends on them yet or because the constraint is deliberate. Issues that
were diagnosed **and fixed** live in [[Troubleshooting]].

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
