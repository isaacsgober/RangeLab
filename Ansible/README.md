# RangeLab Ansible

Phase 3 control setup — configuration management for the two Rocky nodes.

## Layout

```
Ansible/
├── ansible.cfg               points at inventory/hosts.yml
├── inventory/hosts.yml       management_nodes (ansible01), managed_nodes (managed01)
├── group_vars/
│   ├── all.yml               base_packages
│   └── management_nodes.yml  base_packages override (adds sysstat)
├── files/                    labadmin.pub, journald-rangelab.conf
└── site.yml                  the playbook
```

## Running

On **ansible01**, as the **`ansible`** account, from `~ansible/Ansible`.  `ansible` has the outbound key, passwordless sudo, and the `known_hosts` entries.

```bash
ssh ansible@ansible01.rangelab.local
cd ~/Ansible
ansible-playbook site.yml --syntax-check
ansible-playbook site.yml --check          # dry run
ansible-playbook site.yml                  # apply
ansible-playbook site.yml --tags update    # update packages
```

`--tags update` runs the gated full `dnf update`; does effectively nothing with the offline DVD repo, kept for future update path. Default runs skip it.

## Getting files onto ansible01

Authored on the Windows host, copied over. Wipe the old copy first to
avoid stale files and scp nesting.

```powershell
ssh ansible@ansible01.rangelab.local "rm -rf /home/ansible/Ansible"
scp -r "C:\Users\isaac\Documents\RangeLab\Ansible" ansible@ansible01.rangelab.local:/home/ansible/
```

## What site.yml does
Ensures:
- `base_packages` (from `group_vars`)
- `labadmin` admin account: user in `wheel`, `.ssh/` dir, authorized key from `files/labadmin.pub`
- journald drop-in: persistent storage, 750M cap; `file` tasks for the config dir and
  `/var/log/journal`; handlers restart then flush journald on change
- `dnf update` (gated; see `--tags update`)

## Manual steps — not automated

- **`sudo passwd labadmin`** on each node. Ansible does not set the password (no hash in the
  repo). Record it in `creds.md`.
- **Clone generalization** — before adding a cloned VM to the inventory, give it its own:
  hostname, IP, SSH host keys (`rm /etc/ssh/ssh_host_*` then `ssh-keygen -A`),
  `/etc/machine-id` (`rm /etc/machine-id && systemd-machine-id-setup`). See
  `../Docs/Troubleshooting.md`, 2026-09-08.

## Known gaps

- **`ansible-lint`, `yamllint`, `ansible.posix`** — not on the Rocky DVD, no offline install
  path yet. `authorized_key` (from `ansible.posix`) was worked around with `file` + `copy`;
  lint (checklist L59) is deferred until this is solved.
- **Line endings** — playbook and config files must be LF. `.gitattributes` (`eol=lf`)
  enforces it for tracked files; an untracked file `scp`'d with CRLF will break. See
  `../Docs/Troubleshooting.md`, 2026-09-08.
