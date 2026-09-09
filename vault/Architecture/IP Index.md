# IP Index

VMnet10 — `10.10.10.0/24`, host-only, static addressing, no DHCP.
Allocation policy: [[ADR-0001 - IP addressing plan]].

## Allocation ranges

| Range       | Purpose                                   |
| ----------- | ----------------------------------------- |
| .1 – .9     | Network infrastructure                    |
| .10 – .19   | Hypervisors and management plane          |
| .20 – .99   | Linux VMs and workloads                   |
| .100 – .199 | Windows VMs and workloads *(reserved)*    |
| .200 – .254 | Transient hosts, range targets, reserved  |

## Assignments

| Device            | Address         |
| ----------------- | --------------- |
| [[Precision7730]] | [[10.10.10.1]]  |
| [[dnsmasqhost]]   | [[10.10.10.2]]  |
|                   |                 |
| [[esxi01]]        | [[10.10.10.10]] |
| [[vcenter01]]     | [[10.10.10.15]] |
| [[ansible01]]     | [[10.10.10.20]] |
| [[managed01]]     | [[10.10.10.21]] |

## Planned

| Device | Address    | Phase |
| ------ | ---------- | ----- |
| vyos01 | 10.10.10.3 | 2     |
