# ADR-0005 - Lab domain name

## Status

Accepted 2026-09-17. Replaces the undocumented use of `rangelab.local` in the pre-rebuild lab.

---

## Context

The first lab used `rangelab.local`, chosen in Phase 1 without a decision record. `.local` is not
a free-for-all suffix: RFC 6762 reserves it for multicast DNS, and resolvers act on that. On Linux,
`systemd-resolved` routes `.local` lookups to mDNS rather than to a configured DNS server; macOS
and any host running Avahi behave the same way. A unicast DNS server answering `.local` names works
only as long as nothing in the path takes the reservation seriously.

Nothing in the old lab broke because of it — `dnsmasq` answered and the nodes had
`resolved` configured simply enough not to interfere. But the rebuild adds nodes with resolvers we
do not control, and the AD stage later adds a client population where mDNS behaviour matters.
A rebuild is the cheap moment to change a domain name; after Kerberos and certificates exist, it is
not cheap at all.

Options considered:

| Option | Assessment |
|---|---|
| Keep `rangelab.local` | Free, but stays in conflict with RFC 6762 and depends on resolvers ignoring the reservation |
| `rangelab.internal` | ICANN reserved `.internal` in 2024 for private use; it will never be delegated in the public DNS |
| A real owned domain, e.g. `lab.<something-i-own>` | Correct for public trust and publicly issued certificates; costs money, registration upkeep, and split-horizon DNS |
| `home.arpa` (RFC 8375) | Reserved and safe, but scoped to home networks and not namable per-lab |

---

## Decision

The lab domain is **`rangelab.internal`**.

Every node's FQDN is `<hostname>.rangelab.internal`. [[infra01]] is authoritative for
`rangelab.internal` and for `10.10.10.in-addr.arpa`.

---

## Rationale

- `.internal` is reserved for exactly this use, so there is no collision risk with a name someone
  else may register, and no chance of a future public delegation changing resolution underneath the
  lab.
- Unlike `.local`, no protocol special-cases it. A unicast DNS server is the only thing that
  answers, which is what the lab actually runs.
- No registration, renewal, or ownership to maintain, which a portfolio lab should not need.
- The lab's certificates come from VMCA and are trusted manually regardless of domain, so losing
  the ability to obtain publicly issued certificates costs nothing here.

---

## Consequences

Advantages

- Name resolution behaves the same on every client, with no mDNS ambiguity.
- The namespace is guaranteed private; no external dependency at all.
- Reads clearly in documentation as an internal-only name.

Disadvantages

- No public certificate authority will issue for `.internal`, so TLS is private-CA only. Accepted:
  that was already true.
- Every document, playbook, and configuration referencing `rangelab.local` has to be rewritten.
  This is why it happens during a rebuild rather than in place.
- Split-horizon DNS - the same name resolving differently inside and outside - is impossible,
  which rules out one technique if the lab ever grows a public presence. Accepted: There are no plans to do this.

---

## Related

- [[infra01]]
- [[Naming Convention]]
- [[IP Index]]
- [[Rebuild-Plan]]
- [[Build-Sequence]]
