# ansible01

## Purpose

Ansible control node. Every other node in the lab is configured from here.

Like [[infra01]] it runs in Workstation rather than on [[esxi01]], so the tool that manages the
hypervisor's guests does not live inside the hypervisor.

---

## Status

**Running**; rebuilt 2026-09-17

---

## Operating System

Rocky Linux

### Version

10.2 (x86_64), Minimal Install, BIOS firmware

---

## Hostname

ansible01

## Domain

rangelab.internal

## FQDN

ansible01.rangelab.internal

---

## IP Address

[[10.10.10.20]]

Gateway `10.10.10.3` ([[vyos01]]); DNS `10.10.10.3` until [[infra01]] serves the lab zone.

---

## Hosted On

[[Precision7730]] (VMware Workstation)

---

## Network

[[VMnet10]]

---

## Management

SSH: `labadmin@10.10.10.20`

---

## Resources

### CPU

2 vCPU

### Memory

4 GB

### Storage

30 GB, thin

---

## Services

- [[Ansible]]; control node

---

## Toolchain

| Component | Version | Source |
| --------- | ------- | ------ |
| ansible-core | 2.21.4 | pip, in `/opt/ansible` |
| ansible-lint | 26.8.0 | pip, same environment |
| yamllint |; | pip, same environment |
| ansible.posix | 2.2.2 | `ansible-galaxy`, in `~labadmin/.ansible/collections` |
| Python | 3.12.13 | system |
| git |; | `dnf` |

Ansible lives in one virtual environment at `/opt/ansible`, holding ansible-core and the linters
together so the linter and the runtime are the same version by construction. Rocky's own
`ansible-core` package (2.16) is **not** installed; it was removed after the venv was proven, so
there is only one `ansible` on the node.

`/etc/profile.d/ansible.sh` puts `/opt/ansible/bin` on `PATH`. That covers login and interactive
shells but **not** cron, systemd units, or `ssh ansible01 '<command>'`; use the full
`/opt/ansible/bin/` path there.

Updates come from pip, not `dnf update`:
`sudo /opt/ansible/bin/pip install -U ansible-core ansible-lint`.

---

## Notes

2026-09-17:
	Installed from the Rocky 10.2 DVD with the [[Build-Sequence]] Stage 2 settings. Root account locked; `labadmin` is the administrator, password in `creds.md`.
	Playbooks are invoked as `labadmin`, which owns the working copy at `~labadmin/RangeLab`, the control-side Ed25519 key at `~labadmin/.ssh/id_ed25519`, and the installed collections. `ansible` is the account Ansible logs in to on managed nodes, created there by `bootstrap.yml`; see ADR-0002 (revised 2026-09-17) and [[Development-Workflow]].
	The control-side key has no passphrase so playbooks run unattended. It stays on this host and is excluded from the repo. Stage 3's bootstrap play installs the public key on every node.
	This is the canonical working copy of the repository; the copy on the Windows host is for reading and documentation. Only one holds uncommitted changes at a time.
	Not a clone of any other VM; the old lab's duplicate machine-id problem came from cloning.

---

## Related

- [[infra01]]
- [[vyos01]]
- [[managed01]]
- [[VMnet10]]
- [[Build-Sequence]]
- [[IP Index]]
