# Recovery - DNS Unavailable

What to do when [[infra01]]'s DNS stops answering. Hosts are referenced by name (ADR-0008), so a
DNS failure also stops name-based Ansible runs, chrony clients' access to their time source, and
vCenter's name checks.

---

## Symptoms

- Lab names fail to resolve; `dig vcenter01.rangelab.internal` times out or returns SERVFAIL.
- Ansible reports hosts unreachable by name.
- `chronyc sources` on clients shows `^?` for infra01.
- vCenter reports errors in VAMI or the vSphere Client.

If lab names resolve but external names do not, the fault is upstream at [[vyos01]]'s forwarder,
not infra01; see [[Troubleshooting]] (2026-09-17).

---

## Immediate workaround

Reach hosts by address ([[IP Index]]). For Ansible, supply each host's address for the run:

```
ansible-playbook site.yml -e 'ansible_host={{ lab_address }}'
```

---

## Diagnose

1. **Is infra01 up?** `ping 10.10.10.2`. No reply: check its power state in Workstation and use
   the console.
2. **Is dnsmasq running?** On infra01: `systemctl status dnsmasq`. If failed, read
   `journalctl -u dnsmasq` for the reason.
3. **Is the configuration valid?** On infra01: `dnsmasq --test`.
4. **Is it answering?** From another node: `dig @10.10.10.2 infra01.rangelab.internal`.

---

## Fix

Reconverge the DNS role by address, which restores the configuration from the repository and
restarts dnsmasq if it changes:

```
ansible-playbook site.yml --limit dns_servers --tags dns -e 'ansible_host={{ lab_address }}'
```

If the configuration was already correct and dnsmasq is simply stopped:
`sudo systemctl restart dnsmasq` on infra01.

---

## Verify

```
dig +short vcenter01.rangelab.internal
dig -x 10.10.10.15 +short
dig vcenter01.rangelab.internal AAAA
ansible all -m ping
```

Expected: `10.10.10.15`; `vcenter01.rangelab.internal.`; `NOERROR` with an empty answer; `pong`
from every node. vCenter depends on forward and reverse lookups; its services may take several
minutes to recover without intervention.

---

## Related

- [[infra01]]
- [[dnsmasq]]
- [[Operations]]
- [[Troubleshooting]]
