# As-built capture — 2026-09-15

The lab exactly as it stood before the rebuild, captured over SSH and the vCenter API on
2026-09-15. `main` at the same point is tagged `pre-rebuild`.

This is the "before" record for [[Rebuild-Plan]]: it preserves what the hand-built lab actually
looked like, so the rebuild can be compared against it and nothing gets lost by accident.

**Sanitized.** No passwords, password hashes, private keys, or tokens. SSH keys appear only as
fingerprints. The one line matching a password search is the `ansible` sudoers rule
(`NOPASSWD: ALL`), which is by design and already documented in ADR-0002.

## Files

| File | Contents |
| ---- | -------- |
| `dnsmasqhost.txt` | Network, resolver, dnsmasq config, chrony, repos, fstab, firewalld, sshd, users, sudoers, key fingerprints, enabled units |
| `ansible01.txt` | Same, plus the Ansible version |
| `managed01.txt` | Same |
| `esxi01.txt` | Version, hostname, network, DNS, NTP, services, vSwitch, storage, VMs, autostart, license, certificate, accounts |
| `vcenter01.txt` | Photon version, network, resolver files, embedded dnsmasq, ntp.conf and peers, service states, disk, root password aging, faillock |
| `vcenter01-api.txt` | REST API: hosts, VMs, datastores, datacenter, appliance version, NTP, DNS, timesync mode |
| `precision7730.txt` | Windows host, Workstation version, VMware adapters, NAT and DHCP settings, Windows Time, firewall rules, and every Workstation VM's hardware |

## Headline state at capture

| Item | Value |
| ---- | ----- |
| Domain | `rangelab.local` |
| DNS | dnsmasq on dnsmasqhost 10.10.10.2: `bind-dynamic`, `local=` for both zones, one `host-record` per host (the 2026-09-15 ISA-6 fix) |
| Time | Precision7730 (Windows Time) → ansible01 and dnsmasqhost; managed01, vcenter01, esxi01 → ansible01. `makestep 1.0 -1` on all chrony nodes |
| Packages | Local DVD ISO repos only (`local-baseos`, `local-appstream`), mounted from `/dev/sr0` via fstab |
| Ansible | ansible-core 2.16.16 on ansible01, Python 3.12.13 |
| esxi01 | ESXi 9.1.0.0200.25557999, 12 vCPU / 32 GB, datastore01-01 13.75 GB and datastore01-02 224 GB, certificate CN `esxi01.rangelab.local` issued by VMCA, evaluation expires 2026-11-01 |
| vcenter01 | VCSA 9.1.0.0200 build 25573614 on Photon 5.0, 6 vCPU / 16 GB, timesync mode NTP from ansible01, DNS 10.10.10.2, evaluation expires 2026-11-07 |
| vCenter inventory | Datacenter `Datacenter01`; esxi01 CONNECTED; VMs vcenter01, ansible01, managed01 |
| Autostart | VM 7 (ansible01) → VM 8 (managed01) → VM 6 (vcenter01), stop action guest shutdown |
| Host | 127.8 GB RAM, 6 cores / 12 threads, Workstation 26.0.0, VMnet10 host-only 10.10.10.0/24, VMnet8 NAT 192.168.132.0/24 |

## Things the vault didn't record before this capture

- The vSphere datacenter is named `Datacenter01`, which doesn't follow [[Naming Convention]].
- esxi01's VM folder on the host is `ESXi_9`, and its CD drive still points at an ISO path under
  OneDrive rather than the Deployment folder.
- managed01's VM files on the datastore are still named `ansible01.*`, left over from the clone.
- dnsmasqhost boots BIOS while esxi01 boots UEFI.

## Related

- [[Rebuild-Plan]]
- [[Troubleshooting]]
- [[Known-Issues]]
