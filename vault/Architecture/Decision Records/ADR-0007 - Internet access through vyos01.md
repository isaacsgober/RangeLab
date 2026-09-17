# ADR-0007 - Internet access through vyos01

## Status

Accepted 2026-09-17. **Supersedes** [ADR-0003 - Local ISO package
repository](ADR-0003%20-%20Local%20ISO%20package%20repository.md) and **revises**
[ADR-0004 - Lab time source](ADR-0004%20-%20Lab%20time%20source.md).

---

## Context

The pre-rebuild lab had no route off [[VMnet10]]. That was never a security requirement — it was a
side effect of building on a host-only network with no gateway — but every node inherited it, and
the workarounds accumulated:

- **Packages.** With the Rocky mirrors unreachable, each node mounted the 10.2 DVD as a local
  repository (ADR-0003). The package set was frozen at GA, so the lab received no security updates,
  and anything not on the DVD — `ansible.posix`, `ansible-lint`, `yamllint` — had no install path.
  `site.yml` worked around the missing `authorized_key` module by managing the file by hand.
  A clone inherited the repo configuration without the `fstab` entry and silently had no package
  source for a day.
- **Time.** With no reachable NTP server, [[ansible01]] was made a stratum-10 root that invented
  its own time. When esxi01 was suspended, that clock froze and the lab split 3 h 49 m apart
  (ADR-0004). The eventual fix pointed the lab at Windows Time on [[Precision7730]], which worked
  but made the lab's correctness depend on a laptop's clock service being started.
- **Troubleshooting.** Tools that would have shortened several sessions — `bind-utils` for `dig`,
  an editor better than `vi` — could not be installed while diagnosing the thing that needed them.

The lab's own roadmap already called for a router (Stage 01), and `10.10.10.3` was reserved for it
in [ADR-0001](ADR-0001%20-%20IP%20addressing%20plan.md).

---

## Decision

[[vyos01]], a VyOS router, sits on both networks and gives the lab a controlled route out:

- `eth1` on VMnet10 at `10.10.10.3` is the default gateway for every lab node.
- `eth0` on VMnet8 at `192.168.132.3` reaches the internet through Workstation's NAT service.
- Source NAT translates `10.10.10.0/24` out of `eth0` with `masquerade`.
- A DNS forwarder on `10.10.10.3`, restricted with `allow-from`, sends non-lab queries to public
  resolvers. [[infra01]] answers the lab zone and forwards everything else here.
- Lab nodes use the normal Rocky repositories, and [[infra01]] takes its time from public NTP.
- The Rocky DVD becomes installation media only.

vyos01 carries **no firewall policy** at this stage; see Consequences.

---

## Rationale

- The air gap cost more than it bought. It was not protecting anything — the lab holds no sensitive
  data — while it blocked updates, tooling, and correct time.
- Reachable repositories mean nodes can be patched, which is the baseline expectation for any
  system, and makes the lab honest as a portfolio piece.
- A real upstream clock removes the invented stratum and the dependency on the host's Windows Time
  service. Time now comes from the internet rather than from an assertion.
- Egress through a router the lab owns is one place to see and later control what leaves, which is
  better than either no egress or egress through the host's NAT alone.
- The router was already planned and already had an address reserved. This brings a roadmap item
  forward rather than adding scope.

---

## Consequences

Advantages

- Security updates, `dnf` tooling, and collections install normally.
- Correct time from a real source, with no special-case configuration.
- One documented choke point for egress, and a natural place for firewall policy later.
- Retires the per-VM ISO mount, its `fstab` dependency, and the class of failure that came with it.

Disadvantages

- **The lab is no longer isolated.** A compromised lab node has outbound internet access. Accepted:
  there is no sensitive data here, source NAT permits no inbound connections, and vyos01's WAN side
  is Workstation's private network rather than the internet. A firewall policy on vyos01 is the
  deferred follow-up that closes this properly — tracked in [[Known-Issues]].
- Package versions are no longer frozen, so two nodes built weeks apart differ. Reproducibility
  moves from "identical DVD" to "versions recorded in the device notes".
- The lab depends on the host's connectivity and on the chosen public resolvers. The first
  consequence of that dependency was already felt: the recursor's timeout against a slow upstream
  produced SERVFAIL for every client, see [[Troubleshooting]] (2026-09-17).
- Traffic is translated twice, by vyos01 and again by Workstation. Fine for egress; it rules out
  reaching lab nodes from the host's LAN without deliberate port forwarding.
- One more node in the critical path: if vyos01 is down, the lab has no gateway and no DNS.

---

## Related

- [[vyos01]]
- [[infra01]]
- [[VMnet8]]
- [[VMnet10]]
- [ADR-0003 - Local ISO package repository](ADR-0003%20-%20Local%20ISO%20package%20repository.md)
- [ADR-0004 - Lab time source](ADR-0004%20-%20Lab%20time%20source.md)
- [[Rebuild-Plan]]
- [[Known-Issues]]
