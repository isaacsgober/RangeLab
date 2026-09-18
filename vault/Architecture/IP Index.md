# IP Index

VMnet10 - `10.10.10.0/24`, host-only, static addressing, no DHCP.
Allocation policy: [[ADR-0001 - IP addressing plan]].

Since 2026-09-16 the network's default gateway is `.3` ([[vyos01]]), not `.1`. The host adapter
keeps `.1` but routes nothing - see [[VMnet10]].

*Rebuild in progress. Rows marked "held" are addresses reserved for nodes not yet rebuilt. `.2`
passed from dnsmasqhost to [[infra01]] in Stage 2.*

## Allocation ranges

| Range       | Purpose                                   |
| ----------- | ----------------------------------------- |
| .1 – .9     | Network infrastructure                    |
| .10 – .19   | Hypervisors and management plane          |
| .20 – .99   | Linux VMs and workloads                   |
| .100 – .199 | Windows VMs and workloads *(reserved)*    |
| .200 – .254 | Transient hosts, range targets, reserved  |

## Assignments

| Device                        | Address         | State                  |
| ----------------------------- | --------------- | ---------------------- |
| [[Precision7730]]             | [[10.10.10.1]]  | Host adapter           |
| [[infra01]]                   | [[10.10.10.2]]  | Built 2026-09-17       |
| [[vyos01]]                    | [[10.10.10.3]]  | Built 2026-09-16       |
|                               |                 |                        |
| [[esxi01]]                    | [[10.10.10.10]] | Built 2026-09-18       |
| [[vcenter01]]                 | [[10.10.10.15]] | Held - Stage 5         |
| [[ansible01]]                 | [[10.10.10.20]] | Built 2026-09-17       |
| [[managed01]]                 | [[10.10.10.21]] | Held - Stage 6         |

vyos01 also holds `192.168.132.3/24` on [[VMnet8]], outside this plan's scope.
