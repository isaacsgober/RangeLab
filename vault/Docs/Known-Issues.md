# Known Issues & Limitations

Open problems and accepted limitations - things that are not bugs to fix right now, either
because nothing depends on them yet or because the constraint is deliberate. Issues that
were diagnosed **and fixed** live in [[Troubleshooting]].

*Rebuilt 2026-09-17 for the new lab. Three entries were removed because the rebuild ended the
conditions behind them: Windows Time dispersion (the host is no longer the lab's time source), no
offline path for Ansible content (the lab now reaches the internet through [[vyos01]]), and the old
vCenter's evaluation expiry (that appliance no longer exists). Git history has the originals.*

---

## Suspending esxi01 will cost its nested VMs time on resume

**Status:** accepted, and not yet re-testable - [[esxi01]] is rebuilt in Stage 4.

Suspending the hypervisor freezes the clocks of the VMs inside it, which after the rebuild means
[[vcenter01]] and [[managed01]]. On resume each is behind by however long the suspend lasted, and
chrony and ntpd will not trust their source again until the pre-suspend samples age out. Measured
on the old lab after a 5.5-minute suspend, recovery took roughly 6.5 to 15 minutes depending on the
node. A shutdown and boot avoids it entirely.

[[infra01]] and [[ansible01]] are no longer affected: both run directly in Workstation, which is
part of why the layout changed.

---

## infra01 is a single point of failure for names, time, and management

**Status:** accepted, by decision (ADR-0008).

[[infra01]] serves DNS and NTP, and Ansible reaches every node by name through that DNS. If
dnsmasq fails, name resolution, chrony clients, and name-based Ansible runs fail together.
Recovery: `ansible-playbook site.yml -e 'ansible_host={{ lab_address }}'` connects by address for
that run and reconverges the DNS role.

---

## vyos01 has no firewall policy

**Status:** accepted for now; deferred by decision.

vyos01 routes and source-NATs but filters nothing. Its WAN side sits on Workstation's private NAT
network rather than the internet, and nothing outside can open a connection inward through source
NAT, so the exposure is limited. A policy is a follow-up item - see [[Rebuild-Plan]].

---

## Ansible on ansible01 is outside package management

**Status:** accepted, by decision.

`ansible-core` and the linters are installed with pip into `/opt/ansible` so that the runtime and
ansible-lint share one version. Rocky ships `ansible-core` 2.16, five releases behind. The cost is
that `dnf update` does not patch Ansible; refreshing it is
`sudo /opt/ansible/bin/pip install -U ansible-core ansible-lint`, and remembering to do it is
manual. See [[ansible01]].

---

## Evaluation licenses

**Status:** open; both dates recorded below.

ESXi and vCenter are deployed on fresh 90-day evaluations. Each expiry goes in the device note when
the node is built.

| Product | Expires |
| ------- | ------- |
| ESXi on [[esxi01]] | 2026-12-16 |
| vCenter on [[vcenter01]] | 2026-12-17 |
