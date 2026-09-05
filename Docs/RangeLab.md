# Range Lab

## Objective

Build an enterprise-grade cyber range that develops practical skills in virtualization, networking, Linux administration, Windows Server, Active Directory, automation with Ansible, infrastructure-as-code, and adversary emulation.

The goal is to progress through each stage while continuously expanding the same lab rather than rebuilding from scratch, resulting in a single, deeply developed project that demonstrates real-world infrastructure engineering skills. 


## Project Principles

- Build once and iterate.
- Understand every component before adding another.
- Document major decisions.

---

## Stage 01 — Substrate

- [x] Build a lab host and install ESXi
	- [x] Deploy vCenter Server
- [x] Add a **[Proxmox VE](https://www.proxmox.com/)** host
- [ ] Deploy a [VyOS](https://vyos.io/) router
	- [ ] Segment both labs into VLANs (vSphere port group and Proxmox Linux bridge)

**Deliverable**
Two hand-built labs with real VLAN segmentation and working inter-VLAN routing, which you can explain packet by packet — including what each hypervisor's virtual switch does at each hop, and where the two differ.

---

## Stage 02 — Automation

- [ ] Rebuild the Stage 01 lab as [Ansible](https://docs.ansible.com/) entirely
- [ ] Automate vCenter using Ansible — the `community.vmware` and `vmware.vmware_rest` collections. 
- [ ] Achieve idempotent deployments (Destroy it and re-run until the second run reports `changed=0`)
- [ ] Learn [Jinja2](https://jinja.palletsprojects.com/) — loops, filters, conditionals, and variable precedence

**Deliverable**
The lab, reproducible from an empty hypervisor with one command, and idempotent. "Run it twice, expect zero changes."

---

## Stage 03 — Depth & Capstone

- [ ] Build a vSphere Distributed Switch
	- [ ] Move the lab's networking to vSphere Distributed Switch
- [ ] Begin the capstone project
	- [ ] Deploy PXE boot for at least one node

**Deliverable**
The capstone range, in version control, with CI passing.

---

## Stage 04 — Polish & Credibility

- [ ] Windows Server & Active Directory automation
	- [ ]  automate a domain join
	- [ ]  automate a GPO
	- [ ]  automate a member server
- [ ] Write a custom Python Ansible module
- [ ] Deploy adversary emulation onto capstone
	- [Caldera](https://caldera.mitre.org/), [Atomic Red Team](https://atomicredteam.io/), [GHOSTS](https://github.com/cmu-sei/GHOSTS) for user simulation
- [ ] Deploy  [Security Onion](https://securityonionsolutions.com/) and simulate attacks
- [ ] Explore VMware NSX (if available)
- [ ] Contribute to a public Ansible collection
	- [ ] Get a merge request reviewed by a stranger

**Deliverable**
Public review history. A personal repo that shows you can write code; a merged upstream contribution with review comments on it  that shows you can work on a team (this is the harder thing to prove).

---

# Infrastructure

## Physical Host

- [[Precision7730]]

## Hypervisors

- [[esxi01]]
- [[vCenter]]
- [[Proxmox]] *(planned)*

## Networking

- [[VMnet10]]
- [[VyOS]] *(planned)*

## Storage

- [[datastore1]]
- [[datastore2]]

---

# Capstone Goal

By the end of the Range Lab, the environment should include:
- A **topology specification** in YAML or XML — hosts, networks, roles — as the single source of truth
- A generator that turns that spec into an **Ansible inventory**, so the topology is authored once and consumed everywhere
- Provisioning for four nodes: a **Windows domain controller**, a **Linux target**, a **router**, and an **attacker box**
- Real network segmentation between them, defined in the spec rather than clicked into a UI
- Target **vSphere** as the primary platform, with Proxmox as the place you prototype — and keep the topology spec platform-agnostic enough that the same spec can drive either
- **PXE boot** for at least one node, installed unattended
- Everything in Git, with CI running `yamllint`, [`ansible-lint`](https://ansible.readthedocs.io/projects/lint/), and a smoke test
- A `README` that explains the design decisions, not just the run commands
- Full teardown and rebuild from nothing, unattended, proven more than once

---

# Learning Journal

- [[2026-08-03]]
- [[2026-08-04]]

---

# Notes

This vault documents the complete lifecycle of the Range Lab, including infrastructure, configuration, automation, troubleshooting, and design decisions. The objective is to build a functioning lab, and to understand, reproduce, and explain every component of the environment and range infrastructure. 