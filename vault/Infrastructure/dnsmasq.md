# dnsmasq

## Purpose

DNS for Range Lab: authoritative for `rangelab.internal` and `10.10.10.in-addr.arpa`, forwarding
everything else to [[vyos01]].

---

## Host

[[infra01]]

## IP

[[10.10.10.2]]

---

## Ports

53/TCP, 53/UDP. Opened in firewalld as the `dns` service by the `dns` role.

---

## Configuration

`/etc/dnsmasq.conf`, generated in full by the `dns` role from
`Ansible/roles/dns/templates/dnsmasq.conf.j2`. The file carries a header saying so; local edits are
replaced on the next converge.

| Directive | Effect |
| --------- | ------ |
| `listen-address` | The lab address and loopback only |
| `bind-dynamic` | Bind interfaces as they appear, so dnsmasq does not fail when it starts before the interface is up |
| `local=/rangelab.internal/`, `local=/10.10.10.in-addr.arpa/` | Authoritative for both zones: never forwarded, unknown names answered NXDOMAIN |
| `no-resolv` | Ignore `/etc/resolv.conf` when choosing upstreams. Required, because that file points every node, including this one, at dnsmasq |
| `server=10.10.10.3` | Single upstream: [[vyos01]]'s forwarder |
| `domain-needed`, `bogus-priv` | Unqualified names and private reverse lookups are not sent upstream |
| `no-hosts` | `/etc/hosts` is not served; generated records are the only source |

---

## How records are defined

One `host-record=<fqdn>,<address>` line per host, generated from the Ansible inventory. A single
line creates both the A record and the PTR, and makes the name exist for every query type, so a
query for a type it does not have returns NOERROR with no answer rather than NXDOMAIN.

Two sources feed the generation:

- **Managed nodes** come from `groups['all']` and each host's `lab_address`. Adding a node to the
  inventory gives it DNS on the next converge.
- **Unmanaged hosts** come from `dns_extra_records` in `group_vars/all.yml`. [[vyos01]] is there
  now; esxi01, vcenter01, and managed01 join as they are built, until they are managed nodes.

There is no list of records in this document on purpose. The inventory is the source; a copy here
would drift, which is what happened before the rebuild.

**Do not use `address=/<name>/<ip>`.** It is a domain rule that answers only A queries, and since
dnsmasq 2.86 other types fall through to the next rule. With `local=` present that means NXDOMAIN
for AAAA. See [[Troubleshooting]] (2026-09-15).

---

## Dependencies

- [[infra01]] running `dnsmasq`
- [[vyos01]] reachable at `10.10.10.3` for anything outside the lab zone

---

## Notes

Clients reach this service because the `dns` role writes `/etc/resolv.conf` and stops
NetworkManager from managing it. See [[Build-Sequence]] Stage 3.

`dnsmasq --test` validates a configuration file without starting the service.

Ansible reaches every node by name through this service (ADR-0008), so a dnsmasq fault also stops
name-based management. `ansible-playbook site.yml -e 'ansible_host={{ lab_address }}'` connects by
address for that run and restores it.

On [[infra01]] itself, `getent hosts` for its own name answers from `nss-myhostname` rather than
from DNS. See [[Troubleshooting]] (2026-09-18).

---

## Related

- [[infra01]]
- [[vyos01]]
- [[VMnet10]]
- [[Build-Sequence]]
- [[IP Index]]
