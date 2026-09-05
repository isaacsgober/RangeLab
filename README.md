# RangeLab

Virtualized infrastructure homelab — built and documented as the work is actually done.
Nothing here (or on a resume) is claimed until it's been used, tested, broken, fixed, and
written up.

## Two documents drive this project

- **[`Docs/Project_Checklist.md`](Docs/Project_Checklist.md)** — the current, active
  goalpost: Phase 0 through 6 (baseline docs, Git, Ansible, a scripted utility, a read-only
  API exercise, packaging for review).
- **[`Docs/RangeLab.md`](Docs/RangeLab.md)** — the longer-term roadmap and stage dashboard for where
  this lab goes after the current checklist is complete. Treat it as future direction, not
  current-sprint status.

## Architecture (current baseline)

```
Precision7730 (physical host, VMware Workstation)
├── esxi01 (nested ESXi)
│    ├── vcenter01 (VCSA)
│    └── [Ansible control / managed nodes — Phase 2, not yet built]
└── dnsmasqhost (Rocky Linux — DNS only)
```

- Network: `VMnet10`, host-only, `10.10.10.0/24`, static addressing, no DHCP
- Domain: `rangelab.local`

See [`Network/Overview.canvas`](Network/Overview.canvas) (Obsidian canvas) for the visual
topology, and [`Architecture/`](Architecture/) for the naming convention and IP index.

## Vault structure

- `Architecture/` — naming convention, IP index, VM layout
- `Devices/` — one note per physical/virtual host, its specs and management access
- `Infrastructure/` — one note per service/platform (ESXi, vCenter, dnsmasq, datastores)
- `Network/` — network definitions and the topology canvas
- `IPs/` — per-address backlink stubs (Obsidian convention)
- `Journal/` — dated working log of what was actually done each session
- `Docs/` — the active checklist, recovery procedure, troubleshooting log
- `Ansible/` — control-node inventory, variables, and playbooks (Phase 3)
- `Scripts/` — the Bash/Python utility (Phase 4)
- `Templates/` — Obsidian note templates used to keep entries consistent

## Status

Current phase: _(update as you go — see `Docs/Project_Checklist.md`)_

| Phase | Description                          | Status |
|-------|---------------------------------------|--------|
| 0     | Baseline documentation                |        |
| 1     | Git-backed documentation repository   |        |
| 2     | Ansible control + managed nodes       |        |
| 3     | Ansible configuration                 |        |
| 4     | Bash/Python utility                   |        |
| 5     | Read-only API exercise                |        |
| 6     | Packaging for review                  |        |

## Hardware / Software

- Host: Dell Precision 7730, VMware Workstation
- Hypervisor: VMware ESXi (nested) + vCenter Server Appliance
- Guest OS: Rocky Linux
- Automation: Ansible
- DNS: dnsmasq

## Security note

This is an isolated home lab on a host-only virtual network. No production systems, real
organizational data, or public-facing infrastructure are involved. All secrets are excluded
from version control — see `.gitignore`.
