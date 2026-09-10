# RangeLab

Virtualized infrastructure homelab — built and documented as the work is actually done.
Nothing here is claimed until it's been used, tested, broken, fixed, and written up.

**Note:**
The [`vault/`](vault/) directory is an Obsidian vault — open that folder in Obsidian to
navigate it. `[[double-bracket]]` links inside the vault are internal note links used by
Obsidian, and render as plain text on GitHub.
## Two documents drive this project

- **[`vault/Docs/Project_Checklist.md`](vault/Docs/Project_Checklist.md)** — the current, active
  goalpost: Phase 0 through 6 (baseline docs, Git, Ansible, a scripted utility, a read-only
  API exercise, packaging for review).
- **[`vault/Docs/RangeLab.md`](vault/Docs/RangeLab.md)** — the longer-term roadmap and stage dashboard for where
  this lab goes after the current checklist is complete. Treat it as future direction, not
  current-sprint status.

## Architecture (current baseline)

```
Precision7730 (physical host, VMware Workstation)
├── esxi01 (nested ESXi)
│    ├── vcenter01 (VCSA)
│    ├── ansible01 (Rocky Linux — Ansible control node, lab NTP)
│    └── managed01 (Rocky Linux — Ansible managed node)
└── dnsmasqhost (Rocky Linux — DNS only)
```

- Network: `VMnet10`, host-only, `10.10.10.0/24`, static addressing, no DHCP
- Domain: `rangelab.local`

See [`vault/Network/Overview.canvas`](vault/Network/Overview.canvas) (Obsidian canvas) for the visual
topology, and [`vault/Architecture/`](vault/Architecture/) for the naming convention and IP index.

## Repository structure

- `vault/` — the Obsidian vault (open this folder in Obsidian):
  - `Architecture/` — naming convention, IP index, VM layout
  - `Devices/` — one note per physical/virtual host, its specs and management access
  - `Infrastructure/` — one note per service/platform (ESXi, vCenter, dnsmasq, datastores)
  - `Network/` — network definitions and the topology canvas
  - `IPs/` — per-address backlink stubs (Obsidian convention)
  - `Journal/` — dated working log of what was actually done each session
  - `Docs/` — the active checklist, recovery procedure, troubleshooting log, known issues
  - `Templates/` — Obsidian note templates used to keep entries consistent
  - `Attachments/` — evidence screenshots
- `Ansible/` — control-node inventory, variables, and playbook (Phase 3)
- `Scripts/` — the Python utility (Phase 4)

## Status

Current phase: 5 - read-only API exercise

| Phase | Description                         | Status            |
| ----- | ----------------------------------- | ----------------- |
| 0     | Baseline documentation              | Complete          |
| 1     | Git-backed documentation repository | Complete          |
| 2     | Ansible control + managed nodes     | Complete          |
| 3     | Ansible configuration               | One task deferred |
| 4     | Bash/Python utility                 | Complete          |
| 5     | Read-only API exercise              | In-Progress       |
| 6     | Packaging for review                |                   |

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
