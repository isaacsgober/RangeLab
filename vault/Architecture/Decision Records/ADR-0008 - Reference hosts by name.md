# ADR-0008 - Reference hosts by name

## Status

Accepted 2026-09-18. Reverses the address-first reasoning recorded in the Stage 3 build, the
[[chrony]] note, and [[NTP Hierarchy]] before this date.

---

## Context

Stage 3 was built address-first: the inventory carried each host's address in `ansible_host`, and
chrony clients pointed at `10.10.10.2`, so that neither Ansible nor time depended on DNS. The
argument was that infra01 serves DNS, and connecting to it by a name it serves means a broken
dnsmasq locks out the machine needed to fix it.

That argument protects against a narrow case. infra01 serves both DNS and NTP; if it is down, both
are gone whichever way clients refer to it. The address-first design only helps when infra01 is up
and dnsmasq alone is broken, and that state is recoverable in one command. Against that, addresses
scattered through configuration are what a readdressing has to chase, and they read worse than
names.

---

## Decision

Refer to hosts by FQDN everywhere a name can work. Use an address only where DNS is needed to find
DNS:

| Keeps an address | Why |
| ---------------- | --- |
| `nameserver` in `/etc/resolv.conf` | The resolver cannot use DNS to locate the DNS server |
| dnsmasq `listen-address` and `server=` | A name server binds to and forwards to addresses |
| `host-record` lines | They are the name-to-address data itself |
| ESXi's DNS server setting | Same reason as `resolv.conf` |

Everything else uses names: Ansible connects by inventory name, chrony clients use
`infra01.rangelab.internal`, and ESXi's NTP server is `infra01.rangelab.internal`.

In the inventory, each host's address lives in `lab_address`, a plain variable, rather than
`ansible_host`, which would override the connection target.

---

## Rationale

- Configuration reads as intent: `server infra01.rangelab.internal` says what it means.
- Readdressing a node changes one inventory value and the DNS record generated from it.
- The failure it trades for is recoverable: supplying the address for one run restores
  connectivity.

---

## Consequences

Advantages

- One source of addresses, the inventory; everything else follows the name.
- Service configuration no longer carries lab addresses except where it must.

Disadvantages

- **DNS is on the critical path for time and for Ansible.** A dnsmasq fault now also stops chrony
  clients reaching their source and stops Ansible connecting by name. Recovery:
  `ansible-playbook site.yml -e 'ansible_host={{ lab_address }}'`, which connects each host by its
  own address for that run.
- **A rebuild from zero needs addresses for the first converge**, since no lab name resolves
  until the `dns` role has run. The same `-e` form covers it.
- SSH host keys are recorded per name, so every node's key has to be accepted by FQDN as well as
  by any address used earlier.

---

## Related

- [[infra01]]
- [[dnsmasq]]
- [[chrony]]
- [[NTP Hierarchy]]
- [[Build-Sequence]]
- [ADR-0006](ADR-0006%20-%20Infrastructure%20services%20outside%20the%20hypervisor.md)
