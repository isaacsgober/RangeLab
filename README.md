# RangeLab

Virtualized infrastructure homelab, built and documented as the work is actually done.
Nothing here is claimed until it has been used, tested, broken, fixed, and written up.

**Note:** the notes in [`vault/`](vault/) are written for Obsidian. Open the repository root as the
vault; the topology canvas uses file paths relative to it. `[[double-bracket]]` links are internal
note links used by Obsidian, and render as plain text on GitHub.

## Two documents drive this project

- **[`vault/Docs/Project_Checklist.md`](vault/Docs/Project_Checklist.md)**: the active goalpost,
  Phase 0 through 6 (baseline docs, Git, Ansible, a scripted utility, a read-only API exercise,
  packaging for review).
- **[`vault/Docs/RangeLab.md`](vault/Docs/RangeLab.md)**: the longer-term roadmap for after the
  checklist is complete. Future direction, not current status.

The lab was rebuilt from nothing in September 2026 to remove the workarounds of the first build.
[`vault/Docs/Build-Sequence.md`](vault/Docs/Build-Sequence.md) rebuilds it from this repository;
[`vault/Docs/Rebuild-Plan.md`](vault/Docs/Rebuild-Plan.md) records why. The hand-built lab it
replaced is tagged `pre-rebuild`.

## Architecture

```
Precision7730 (physical host, VMware Workstation)
├── vyos01     VyOS: gateway, source NAT, DNS forwarding
├── infra01    Rocky Linux: DNS (dnsmasq), NTP (chrony)
├── ansible01  Rocky Linux: Ansible control node
└── esxi01     nested ESXi 9.1
     ├── vcenter01  vCenter Server Appliance 9.1
     └── managed01  Rocky Linux: Ansible-managed node
```

- Lab network: `VMnet10`, host-only, `10.10.10.0/24`, static addressing, gateway `10.10.10.3`
- Egress: outbound only, through vyos01 onto Workstation's NAT network; nothing inbound
- Domain: `rangelab.internal`; hosts are referenced by FQDN
- Lab services run outside esxi01, so DNS, time, and Ansible do not depend on the hypervisor

Decisions are recorded as ADRs in
[`vault/Architecture/Decision Records/`](vault/Architecture/Decision%20Records/). The visual topology
is [`vault/Network/Overview.canvas`](vault/Network/Overview.canvas) (Obsidian canvas).

## Repository structure

- `vault/`: the Obsidian vault
  - `Architecture/`: naming convention, IP index, VM layout, NTP hierarchy, decision records
  - `Devices/`: one note per host
  - `Infrastructure/`: one note per service or platform (vCenter, dnsmasq, chrony, datastores)
  - `Network/`: network definitions, the vyos01 configuration, and the topology canvas
  - `IPs/`: per-address backlink stubs (Obsidian convention)
  - `Journal/`: dated working log of each session
  - `Docs/`: build sequence, rebuild plan, checklist, troubleshooting log, known issues,
    development workflow
  - `Templates/`: Obsidian note templates
  - `Attachments/`: evidence, including the as-built capture of the pre-rebuild lab
- `Ansible/`: inventory, variables, bootstrap playbook, and the `common`, `ntp`, and `dns` roles
- `Scripts/`: Python utilities: a connectivity health check and a read-only vCenter VM inventory

## Status

Current phase: 6, packaging for review

| Phase | Description                         | Status      |
| ----- | ----------------------------------- | ----------- |
| 0     | Baseline documentation              | Complete    |
| 1     | Git-backed documentation repository | Complete    |
| 2     | Ansible control and managed nodes   | Complete    |
| 3     | Ansible configuration               | Complete    |
| 4     | Bash/Python utility                 | Complete    |
| 5     | Read-only API exercise              | Complete    |
| 6     | Packaging for review                | In progress |

## Hardware and software

- Host: Dell Precision 7730, VMware Workstation 26
- Router: VyOS Stream 2026.02
- Hypervisor: VMware ESXi 9.1 (nested) and vCenter Server Appliance 9.1
- Guest OS: Rocky Linux 10.2
- Automation: Ansible (ansible-core 2.21, ansible-lint)
- DNS and time: dnsmasq and chrony

## Security note

A home lab on a private virtual network. It reaches the internet outbound only, through vyos01's
source NAT, and accepts no inbound connections from outside. No production systems, real
organizational data, or public-facing services are involved. Secrets are excluded from version
control; see `.gitignore`.
