# ADR-0001 - IP addressing plan for VMnet10

## Status

Accepted

---

## Context

VMnet10 (`10.10.10.0/24`) is a host-only network with static addressing and no DHCP. Four
addresses were assigned ad hoc during the initial build: `.1` host adapter / gateway, `.2`
DNS, `.10` esxi01, `.15` vcenter01. Phase 2 adds two Linux VMs, and later stages add a
router, a Proxmox host, Windows Server / Active Directory, and range targets. Without a
documented plan, each new assignment is guesswork and the IP Index cannot be read at a
glance.

---

## Decision

Divide `10.10.10.0/24` into function-based bands:

| Range       | Purpose                                   | Assigned                                  |
| ----------- | ----------------------------------------- | ----------------------------------------- |
| .1 – .9     | Network infrastructure                    | `.1` gateway / host adapter, `.2` dnsmasqhost |
| .10 – .19   | Hypervisors and management plane          | `.10` esxi01, `.15` vcenter01             |
| .20 – .99   | Linux VMs and workloads                   | `.20` ansible01, `.21` rocky01 *(planned)* |
| .100 – .199 | Windows VMs and workloads *(reserved)*    | —                                         |
| .200 – .254 | Transient hosts, range targets, reserved  | —                                         |

Within a band, assign sequentially from the low end. `.0` and `.255` are reserved by the
subnet.

---

## Rationale

- Preserves every address already in use; no renumbering.
- Function-based bands keep the IP Index scannable and make a host's role guessable from
  its address.
- The Linux band is wide (80 addresses) because that matches the near-term direction
  (Ansible control/managed nodes, service VMs). Windows and transient bands are reserved
  now so later stages do not collide with earlier ones.
- Sequential-within-band keeps assignment trivial and predictable under static addressing.

---

## Consequences

Advantages

- New hosts get an address by rule, not by debate.
- The IP Index doubles as a per-function capacity view.

Disadvantages

- One band could fill while others sit empty (unlikely on a lab /24).
- The reserved bands are a guess at future needs and may be re-cut by a later ADR.

---

## Related

- [[IP Index]]
- [[Naming Convention]]
- [[VMnet10]]
