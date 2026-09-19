# vyos01.config

The running configuration of [[vyos01]], exported on 2026-09-16 with `show configuration commands`.
Re-applying these lines in `configure` mode rebuilds the router exactly. The hash on the
`system login user vyos` line is redacted.
Not every line here was a lab decision: the `offload`, `hw-id`, `ntp`, `console`, `syslog`, and
`config-management` lines are VyOS's own defaults - see [[Build-Sequence]] 1.4.

```bash
set interfaces ethernet eth0 address '192.168.132.3/24'
set interfaces ethernet eth0 description 'WAN - VMnet8 (Workstation NAT)'
set interfaces ethernet eth0 hw-id '00:0c:29:5c:a9:f6'
set interfaces ethernet eth0 offload gro
set interfaces ethernet eth0 offload gso
set interfaces ethernet eth0 offload sg
set interfaces ethernet eth0 offload tso
set interfaces ethernet eth1 address '10.10.10.3/24'
set interfaces ethernet eth1 description 'LAN - VMnet10'
set interfaces ethernet eth1 hw-id '00:0c:29:5c:a9:00'
set interfaces ethernet eth1 offload gro
set interfaces ethernet eth1 offload gso
set interfaces ethernet eth1 offload sg
set interfaces ethernet eth1 offload tso
set interfaces loopback lo
set nat source rule 100 description 'Lab to internet'
set nat source rule 100 outbound-interface name 'eth0'
set nat source rule 100 source address '10.10.10.0/24'
set nat source rule 100 translation address 'masquerade'
set protocols static route 0.0.0.0/0 next-hop 192.168.132.2
set service dns forwarding allow-from '10.10.10.0/24'
set service dns forwarding listen-address '10.10.10.3'
set service dns forwarding name-server 1.0.0.1
set service dns forwarding name-server 1.1.1.1
set service ntp allow-client address '127.0.0.0/8'
set service ntp allow-client address '169.254.0.0/16'
set service ntp allow-client address '10.0.0.0/8'
set service ntp allow-client address '172.16.0.0/12'
set service ntp allow-client address '192.168.0.0/16'
set service ntp allow-client address '::1/128'
set service ntp allow-client address 'fe80::/10'
set service ntp allow-client address 'fc00::/7'
set service ntp server time1.vyos.net
set service ntp server time2.vyos.net
set service ntp server time3.vyos.net
set service ssh listen-address '10.10.10.3'
set system config-management commit-revisions '100'
set system console device ttyS0 speed '115200'
set system domain-name 'rangelab.internal'
set system host-name 'vyos01'
set system login user vyos authentication encrypted-password '<redacted>'
set system name-server '1.1.1.1'
set system option reboot-on-upgrade-failure '5'
set system syslog local facility all level 'info'
set system syslog local facility local7 level 'debug'
```
