# ADR-0006 - Infrastructure services outside the hypervisor

## Status

Accepted 2026-09-17.

---

## Context

In the pre-rebuild lab, [[ansible01]] ran as a guest of [[esxi01]] while serving two roles that
everything else depended on: Ansible control node and lab NTP server. [[dnsmasqhost]] served DNS
from VMware Workstation, beside esxi01 rather than inside it. The split was accidental - each node
was placed wherever was convenient at the time it was built.

The cost showed up on 2026-09-15, documented in
[ADR-0004](ADR-0004%20-%20Lab%20time%20source.md). Suspending esxi01 freezes every VM nested inside
it, so suspending the hypervisor stopped the lab's clock source; upon resume the lab had split into
two groups 3 h 49 m apart. The same placement had two further consequences that were nearly hit:
the control node that manages the hypervisor lived inside that hypervisor, so an ESXi or vCenter
failure would take the management tooling with it, and DNS and time - services with identical
availability requirements - sat on opposite sides of the nesting boundary for no reason.

Precision7730 has 12 threads and 128 GB of RAM. Running three small VMs directly in Workstation
costs about 10 of 12 threads and 74 of 128 GB in total across the whole lab, so capacity was never
the constraint.

---

## Decision

Services the rest of the lab depends on run **outside** esxi01, as VMware Workstation guests:

| Node | Role |
|---|---|
| [[vyos01]] | Gateway, source NAT, DNS forwarding |
| [[infra01]] | DNS (dnsmasq) and NTP (chrony) for `10.10.10.0/24` |
| [[ansible01]] | Ansible control node |

[[esxi01]] hosts only what is meant to be managed: [[vcenter01]] and [[managed01]].

DNS and NTP are consolidated onto infra01, which replaces dnsmasqhost.

---

## Rationale

- A lab node should not depend on the hypervisor for the gateway, the name it resolves, or the time
  it keeps. Those three are now beneath esxi01 in the dependency order, not inside it.
- The control node should sit outside the thing it controls. esxi01 can be rebuilt, suspended, or
  broken on purpose - which a range lab should be able to do - without losing Ansible.
- It keeps the nested environment as the subject under test rather than part of the test harness.
- Consolidating DNS and NTP onto one node reflects that they have the same availability
  requirement, and removes a machine whose placement had no rationale.

---

## Consequences

Advantages

- Lab DNS, time, and routing survive esxi01 being down, suspended, or rebuilt.
- esxi01 becomes expendable, which is the point of a range.
- One fewer service node, and a clear dependency order for start-up and shutdown:
  vyos01 → infra01 → ansible01 → esxi01, reversed to stop.

Disadvantages

- Three VMs to manage in Workstation rather than one, each needing its own start and stop.
- Host RAM is committed to lab infrastructure whether or not esxi01 is running.
- vcenter01 and managed01 still freeze when esxi01 is suspended - see [[Known-Issues]]. This ADR
  limits the blast radius rather than removing it.
- Two management surfaces: Workstation for the infrastructure nodes, vSphere for the nested ones.

---

## Related

- [[vyos01]]
- [[infra01]]
- [[ansible01]]
- [[esxi01]]
- [ADR-0004 - Lab time source](ADR-0004%20-%20Lab%20time%20source.md)
- [[Rebuild-Plan]]
- [[Known-Issues]]
