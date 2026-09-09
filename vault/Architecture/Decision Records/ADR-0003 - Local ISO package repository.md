# ADR-0003 - Local ISO package repository

## Status

Accepted

---

## Context

The lab is fully offline. [[VMnet10]] has no route off the subnet and [[dnsmasq]] has no
upstream forwarder, so the Rocky Linux mirrors neither resolve nor route. A Minimal install
of Rocky 10.2 lacks common tools (`bind-utils`, `git`, an editor beyond `vi`) and the
dependencies needed to install `ansible-core`. Building [[ansible01]] and [[managed01]] —
and adding tools during troubleshooting — requires a package source.

This was hit during the 2026-09-06 build: `dnf` on a fresh node failed against the stock
repos, and `nslookup` / `nano` could not be installed to diagnose it. See Journal/[[2026-09-06]].

---

## Decision

Build a local `dnf` repository from the Rocky 10.2 DVD ISO.

- The ISO is attached to each VM's virtual CD/DVD drive and mounted read-only at
  `/mnt/rocky-iso`.
- `/etc/yum.repos.d/local-iso.repo` defines `local-baseos` and `local-appstream` with
  `baseurl=file:///mnt/rocky-iso/BaseOS` and `.../AppStream`.
- The stock `baseos`, `appstream`, and `extras` repos are disabled.
- `gpgcheck=1`, verifying against the Rocky 10 key already shipped at
  `/etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-10` — not a key read off the ISO.
- Persistence: an `/etc/fstab` entry (`/dev/sr0` → `/mnt/rocky-iso`, `iso9660`, `ro,nofail`)
  mounts the ISO at boot. `nofail` keeps the node bootable if the ISO is ever detached.

---

## Rationale

- It is the only package source currently available in this isolated lab.
- Pins every node to one known package set (the 10.2 GA DVD) - reproducible.
- `file://` with `gpgcheck=1` keeps signature verification without any network.
- The DVD carries BaseOS + AppStream, which covers the Minimal-install gaps and
  `ansible-core`.

---

## Consequences

Advantages

- Nodes build and take package changes with no internet access.
- Identical package versions across all current and future nodes.
- Package signature verification is preserved.

Disadvantages

- No security updates. The repo is frozen at 10.2 GA. Acceptable because the lab is
  isolated.
- Smaller than the online repos — no EPEL, no `ansible-lint`, nothing released after GA.
  Phase 3+ tooling that is not on the DVD needs a separate plan (offline mirror or a
  controlled one-time sync).
- The ISO attachment is per-VM and manual — a freshly created VM needs the image connected
  in the hypervisor before its repo works.
- The mount is not automatic. Without the `/etc/fstab` entry the repo is dead after every
  reboot. The [[managed01]] clone inherited the repo config and a connected ISO but no
  fstab entry, so it silently had no package source until 2026-09-07.
- Consumes the virtual optical drive (`/dev/sr0`).

---

## Related

- [[ansible01]]
- [[managed01]]
- [[dnsmasq]]
- [[Troubleshooting]]
- [[2026-09-06]]
