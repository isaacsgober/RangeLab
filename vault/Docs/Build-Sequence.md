
# Build Sequence

How to build Range Lab from nothing. Written during the 2026-09-16 rebuild, one stage at a time,
from what actually worked. Design and reasoning: [[Rebuild-Plan]]. The lab this replaced is
recorded in `vault/Attachments/as-built-2026-09-15/` and tagged `pre-rebuild`.

**Conventions in this document**

- Commands are shown exactly as typed. Output shown is the real output, trimmed.
- Every stage ends with checks. Don't start the next stage until they pass.
- Values (addresses, names, sizes) come from [[IP Index]] and [[Naming Convention]].

## What you need before starting

| Item | Value |
| ---- | ----- |
| Host | Windows 11 with VMware Workstation 26 |
| Networks | VMnet10 host-only `10.10.10.0/24` (host adapter `10.10.10.1`, no DHCP); VMnet8 NAT `192.168.132.0/24` (NAT gateway `192.168.132.2`, DHCP `.128–.254`) |
| Installer images | VyOS Stream 2026.02, Rocky Linux 10.2 DVD, VMware ESXi 9.1, VCSA 9.1 |
| Repository | This repo, cloned on the host |
| Firmware | BIOS on the Workstation guests; UEFI on esxi01 and everything nested inside it |

Workstation greys out UEFI for these Linux guest profiles, so the Workstation guests are BIOS.
esxi01's ESXi profile forces EFI on its own; nothing is selected there either.

---

# Stage 1 — vyos01, the lab router

vyos01 is the lab's gateway. It gives every other node a route to the internet, and it forwards
DNS queries that infra01 can't answer itself. It has to exist first: every later node is installed
with `10.10.10.3` as its default gateway.

## 1.1 Create the VM

In Workstation: **File → New Virtual Machine → Custom**.

| Setting           | Value                                  | Why                                                                           |
| ----------------- | -------------------------------------- | ----------------------------------------------------------------------------- |
| Guest OS          | Linux → Debian 12.x 64-bit             | VyOS 1.5 is built on Debian 12                                                |
| Name              | `vyos01`                               | [[Naming Convention]]                                                         |
| Location          | `Documents\Virtual Machines\vyos01`    | One folder per VM                                                             |
| Firmware          | BIOS                                   | The only option Workstation offers for this guest profile                     |
| Processors        | 1                                      | Routing this lab needs almost nothing                                         |
| Memory            | 4096 MB                                | VyOS 1.5's documented minimum                                                 |
| Network adapter 1 | Custom → **VMnet8**, `e1000`           | The outside (WAN) interface                                                   |
| Network adapter 2 | Custom → **VMnet10**, `e1000`          | The lab (LAN) interface; add it in VM Settings after creation                 |
| Disk              | 20 GB, single file, SCSI (LSI Logic)   | Minimum is 10 GB; thin, so it costs under 1 GB in practice                    |
| CD/DVD            | VyOS Stream ISO, connected at power on | Install media                                                                 |

Then, with the VM powered off, add one line to `vyos01.vmx`:

```
rtc.diffFromUTC = "0"
```

Workstation sets a VM's virtual hardware clock to the host's *local* time by default. Linux expects
that clock to be UTC, so without this line the guest boots hours off. This is what made
dnsmasqhost boot five hours in the past in the old lab.

**Adapter order matters.** Adapter 1 becomes `eth0` and adapter 2 becomes `eth1`. Check it after
first boot (1.3) before trusting it.

## 1.2 Install VyOS

Boot the VM from the ISO. It comes up as a live system. The banner calling the image a technology
preview is expected on a stream release.

```
login: vyos
password: vyos
```

```
install image
```

Answer the prompts: continue, auto partitioning, the virtual disk, default sizes, a new password
for the `vyos` user, and the default boot console. When it finishes:

```
poweroff
```

In VM Settings → CD/DVD, clear **Connect at power on** and disconnect the ISO, then power the VM
back on.

## 1.3 Check which interface is which

```
show interfaces
```

Compare the MAC addresses with VM Settings → Network Adapter → Advanced. `eth0` must be the
VMnet8 adapter and `eth1` the VMnet10 adapter. If they're swapped, swap the addresses in 1.4.

## 1.4 Configure

```
configure
```

Identity:

```
set system host-name vyos01
set system domain-name rangelab.internal
```

Interfaces:

```
set interfaces ethernet eth0 address 192.168.132.3/24
set interfaces ethernet eth0 description 'WAN - VMnet8 (Workstation NAT)'
set interfaces ethernet eth1 address 10.10.10.3/24
set interfaces ethernet eth1 description 'LAN - VMnet10'
```

`192.168.132.3` is static and deliberately below Workstation's DHCP range (`.128–.254`), so the
router's address can never move.

Route out and a resolver for the router itself:

```
set protocols static route 0.0.0.0/0 next-hop 192.168.132.2
set system name-server 1.1.1.1
```

`192.168.132.2` is Workstation's NAT service, the gateway off VMnet8. It also runs a DNS proxy on
the same address, but the lab does not use it — see the DNS forwarding note below.

Source NAT, so lab addresses can reach the internet:

```
set nat source rule 100 description 'Lab to internet'
set nat source rule 100 outbound-interface name eth0
set nat source rule 100 source address 10.10.10.0/24
set nat source rule 100 translation address masquerade
```

Traffic leaving `eth0` from `10.10.10.0/24` gets rewritten to the router's own WAN address.
`masquerade` means "use whatever address is on the outgoing interface".

DNS forwarding, for infra01 to send non-lab queries to:

```
set service dns forwarding listen-address 10.10.10.3
set service dns forwarding allow-from 10.10.10.0/24
set service dns forwarding name-server 1.1.1.1
set service dns forwarding name-server 1.0.0.1
```

`allow-from` keeps this from being an open resolver. `listen-address` keeps it off the WAN side.

**Do not forward to `192.168.132.2` here.** It is too slow for the recursor's 1500 ms timeout and
every client gets SERVFAIL — see [[Troubleshooting]] (2026-09-17).

Management access:

```
set service ssh listen-address 10.10.10.3
```

Review, activate, and persist:

```
compare
commit
save
```

`compare` shows what you're about to change. `commit` makes it live. `save` writes it to
`/config/config.boot` so it survives a reboot — commit alone does not.

The saved configuration will contain more than the commands above — NTP, syslog, console,
offload, `hw-id`, `commit-revisions`. Those are VyOS defaults, not lab decisions.

## 1.5 Checks

```
show interfaces
show ip route
ping 192.168.132.2 count 3
ping 1.1.1.1 count 3
ping vyos.net count 3
show nat source rules
dig @10.10.10.3 rockylinux.org
```

Expected: both interfaces up with the addresses above; a default route via `192.168.132.2`; all
three pings succeed; one NAT rule listed; and the `dig` returns `status: NOERROR` in tens of
milliseconds.

The `dig` is not optional: the pings only prove the router resolves for itself, and the forwarding
service is what clients use.

**Result, 2026-09-16:** all three pings replied, including `vyos.net` — which also proves the
adapter order was right, since the replies came back through `eth0`. **2026-09-17:**
`dig @10.10.10.3` returned NOERROR in 32 ms after the forwarder was pointed at public resolvers.

From the Windows host, confirm management access:

```
ssh vyos@10.10.10.3
```

## 1.6 Record it

```
show configuration commands
```

Save that output to [[vyos01.config]] (`vault/Network/vyos01.config.md`), with the hash on the
`set system login user vyos authentication encrypted-password` line replaced by a placeholder —
keeping the line shows the account exists without publishing its hash.

Then write the device note, [[vyos01]], from the same output.

**Not configured yet:** vyos01 has no firewall policy. Its WAN side sits on Workstation's private
NAT network, so it isn't exposed to the internet directly. Tracked as a follow-up.

---

# Stage 2 — infra01 and ansible01

Two Rocky Linux VMs, installed from the DVD. infra01 will serve DNS and NTP to the lab; ansible01
is the control node that configures everything from here on. Neither is configured by hand beyond
what the installer asks: Stage 3 does the rest with Ansible.

Install infra01 first, then ansible01. Both are Workstation guests, so neither depends on esxi01.

## 2.1 Create the VMs

**File → New Virtual Machine → Custom**, with the same choices as vyos01 except:

| Setting | infra01 | ansible01 |
| ------- | ------- | --------- |
| Guest OS | Linux → Rocky Linux 64-bit | Linux → Rocky Linux 64-bit |
| Firmware | BIOS | BIOS |
| Processors | 1 | 2 |
| Memory | 2048 MB | 4096 MB |
| Disk | 20 GB, single file | 30 GB, single file |
| Network adapter | Custom → **VMnet10** | Custom → **VMnet10** |
| CD/DVD | `Rocky-10.2-x86_64-dvd1.iso`, connected at power on | same |

With each VM powered off, add to its `.vmx`:

```
rtc.diffFromUTC = "0"
```

## 2.2 Rocky installer settings

Identical for both machines except the highlighted rows.

| Installer screen                | Setting                                                                             |
| ------------------------------- | ----------------------------------------------------------------------------------- |
| Language / Keyboard             | English (US)                                                                        |
| Time & Date                     | Region/City: **Etc / Coordinated Universal Time**                                   |
| Software Selection              | **Minimal Install**                                                                 |
| Installation Destination        | The virtual disk, automatic partitioning                                            |
| Network & Host Name → Host Name | **`infra01.rangelab.internal`** / **`ansible01.rangelab.internal`**                 |
| … → Configure → IPv4 Settings   | Method **Manual**                                                                   |
| … → Address                     | **`10.10.10.2`** / **`10.10.10.20`**, netmask `255.255.255.0`, gateway `10.10.10.3` |
| … → DNS servers                 | `10.10.10.3`                                                                        |
| … → Search domains              | `rangelab.internal`                                                                 |
| … → General                     | "Connect automatically with priority" checked                                       |
| Root Account                    | **Lock root account**                                                               |
| User Creation                   | `labadmin`, "Make this user administrator" checked, password recorded in `creds.md` |

Begin installation, then reboot and disconnect the ISO.

**Why DNS points at the router here:** infra01 isn't serving DNS yet — it's the machine being
installed. `10.10.10.3` forwards to the internet so `dnf` works immediately. Stage 3 switches both
nodes to infra01 once dnsmasq is running.

## 2.3 Checks after first boot

On each node, logged in as `labadmin`:

```
ip -br addr
ip route
timedatectl
getenforce
ping -c3 10.10.10.3
sudo dnf makecache
```

Expected: the static address; a default route via `10.10.10.3`; the clock in UTC with "RTC in local
TZ: no"; SELinux `Enforcing`; the gateway replies; and `dnf` reaches the Rocky mirrors.

## 2.4 Prepare ansible01 as the control node

Install git, then Ansible and the linters into one virtual environment:

```
sudo dnf -y install git
sudo python3 -m venv /opt/ansible
sudo /opt/ansible/bin/pip install --upgrade pip
sudo /opt/ansible/bin/pip install ansible-core ansible-lint yamllint
echo 'export PATH=/opt/ansible/bin:$PATH' | sudo tee /etc/profile.d/ansible.sh
```

Rocky ships `ansible-core` 2.16; pip installs the current release. Putting ansible-core and
ansible-lint in the same environment keeps the linter and the runtime on one version — install them
separately and the linter silently checks your work against a core you do not run.

Ansible here is pip-managed: `dnf update` will not touch it. Refresh it with
`sudo /opt/ansible/bin/pip install -U ansible-core ansible-lint`.

`PATH` from `/etc/profile.d` reaches login and interactive shells, but not cron, systemd units, or
`ssh host '<command>'`. Use the full `/opt/ansible/bin/` path in those.

Create the automation account (ADR-0002) and give it passwordless sudo:

```
sudo useradd --create-home --shell /bin/bash ansible
printf 'ansible ALL=(ALL) NOPASSWD: ALL\n' | sudo tee /etc/sudoers.d/ansible
sudo chmod 0440 /etc/sudoers.d/ansible
sudo visudo -c
```

`visudo -c` checks every sudoers file before you rely on it. A malformed drop-in can lock out sudo
entirely.

Generate the key this account will use to reach every other node:

```
sudo -u ansible ssh-keygen -t ed25519 -N '' -C 'ansible@ansible01' -f /home/ansible/.ssh/id_ed25519
sudo -u ansible cat /home/ansible/.ssh/id_ed25519.pub
```

It has no passphrase so playbooks can run unattended, and the private key never leaves this host —
the tradeoff recorded in ADR-0002. Keep the public key handy; Stage 3's bootstrap play installs it
on the other nodes.

Clone the repository (public, so no credentials):

```
sudo -u ansible git clone https://github.com/isaacsgober/RangeLab.git /home/ansible/RangeLab
```

Add the collection the playbooks need. Collections install per account, under
`~ansible/.ansible/collections`, independent of which ansible-core is in use:

```
sudo -u ansible -i ansible-galaxy collection install ansible.posix
```

## 2.5 Checks

```
which ansible-playbook
ansible --version | head -1
ansible-lint --version
sudo -u ansible -i ansible-galaxy collection list | grep posix
sudo -u ansible -i git -C /home/ansible/RangeLab log --oneline -1
```

Expected: `/opt/ansible/bin/ansible-playbook`; **the same ansible-core version from both `ansible`
and `ansible-lint`**; `ansible.posix` listed; the clone's latest commit matching GitHub.

`-i` runs the command in the `ansible` account's own login shell and home. Without it these fail
with `PermissionError: '.'`, because `sudo -u` keeps the current directory and homes are mode 700.

**Verified 2026-09-17:** ansible-core 2.21.4 (pip), ansible-lint 26.8.0 on the same core,
ansible.posix 2.2.2, Python 3.12.13, clone at `bc756a5`.

Record the installed versions in the device note — they pin what this build was tested with.
