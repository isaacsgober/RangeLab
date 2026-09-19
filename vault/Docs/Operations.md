# Operations

Starting, stopping, and routinely checking Range Lab. Build steps are in [[Build-Sequence]];
recovery from a DNS failure is in [[Recovery]].

---

## Start order

| Order | Node | Why this position |
| ----- | ---- | ----------------- |
| 1 | vyos01 | Gateway and DNS forwarding for everything after it |
| 2 | infra01 | DNS and time; every later node resolves and syncs through it |
| 3 | ansible01 | Control node |
| 4 | esxi01 | Autostart then starts vcenter01, followed by managed01 |

Autostart powers vcenter01 on as soon as esxi01 is up, but the vSphere Client accepts logins only
after the appliance's services finish starting. Nothing else waits on vCenter.

---

## Stop order

The reverse, always with Workstation's **Shut Down Guest**, never Power Off:

| Order | Node | Notes |
| ----- | ---- | ----- |
| 1 | esxi01 | Autostart shuts down managed01 (up to 120 s), then vcenter01 (up to 600 s), then the host |
| 2 | ansible01 | |
| 3 | infra01 | |
| 4 | vyos01 | |

Do not suspend esxi01; the VMs inside it lose time on resume. See [[Known-Issues]].

---

## Routine checks

From ansible01, in `~/RangeLab/Ansible`:

```
python ../Scripts/healthcheck.py vyos01.rangelab.internal infra01.rangelab.internal ansible01.rangelab.internal vcenter01.rangelab.internal managed01.rangelab.internal
python ../Scripts/healthcheck.py -p 443 esxi01.rangelab.internal
ansible-playbook site.yml
```

Every host reachable and `changed=0` means the lab matches the repository.

---

## Routine tasks

| Task | How |
| ---- | --- |
| Update packages on managed nodes | `ansible-playbook site.yml --tags update` |
| Update Ansible on ansible01 | `sudo /opt/ansible/bin/pip install -U ansible-core ansible-lint` |
| Add a Rocky node | [[Build-Sequence]] 3.4 |
| SSH to esxi01 | Enable in the DCUI (Troubleshooting Options) or the vSphere Client; off after every reboot |
| Check evaluation expiry | ESXi 2026-12-16, vCenter 2026-12-17; see [[Known-Issues]] |

---

## Related

- [[Build-Sequence]]
- [[Recovery]]
- [[Known-Issues]]
- [[VM Layout]]
