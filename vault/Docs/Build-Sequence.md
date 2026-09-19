
# Build Sequence

How to build Range Lab from nothing. Written during the 2026-09-16 rebuild, one stage at a time,
from what actually worked. Design and reasoning: [[Rebuild-Plan]]. The lab this replaced is
recorded in `vault/Attachments/as-built-2026-09-15/` and tagged `pre-rebuild`.

**Conventions in this document**

- Commands are shown exactly as typed. Output shown is the real output, trimmed.
- Commands use `~`, `$HOME`, or `$env:USERPROFILE` rather than any one account's paths, so they
  run unchanged for anyone. Recorded output uses `<user>` in place of a username.
- Every stage ends with checks. No stage begins until the previous stage's checks pass.
- Values (addresses, names, sizes) come from [[IP Index]] and [[Naming Convention]].
- Written for a rebuild from `main`: every file referenced already exists in the repository with
  the lab's values.

## Prerequisites

| Item | Value |
| ---- | ----- |
| Host | Windows 11 with VMware Workstation 26 |
| Networks | VMnet10 host-only `10.10.10.0/24` (host adapter `10.10.10.1`, no DHCP); VMnet8 NAT `192.168.132.0/24` (NAT gateway `192.168.132.2`, DHCP `.128–.254`) |
| Installer images | VyOS Stream 2026.02, Rocky Linux 10.2 boot ISO, VMware ESXi 9.1, VCSA 9.1 |
| Repository | This repo, cloned on the host |
| Firmware | BIOS on the Workstation guests; UEFI on esxi01 and everything nested inside it |
| Host DNS | VMnet10 adapter: DNS server `10.10.10.2`, no gateway. Lets the host resolve lab FQDNs from Stage 3 on |

Workstation greys out UEFI for these Linux guest profiles, so the Workstation guests are BIOS.
esxi01's ESXi profile forces EFI on its own; nothing is selected there either.

Rebuilding over an earlier lab on the same host leaves its SSH host keys behind, and SSH refuses
the new nodes with "REMOTE HOST IDENTIFICATION HAS CHANGED". Clear them in PowerShell:

```
Get-Content "$env:USERPROFILE\.ssh\known_hosts" | ForEach-Object { ($_ -split ' ')[0] } | Sort-Object -Unique | Where-Object { $_ -match '^10\.10\.10\.|\.rangelab\.' } | ForEach-Object { ssh-keygen -R $_ }
```

The pattern matches the earlier lab's network, `^10\.10\.10\.` (its address without the host
octet), and a unique part of its domain, `\.rangelab\.`. Replace either if that lab used different
values; dots are escaped with `\`.

---

# Stage 1 - vyos01, the lab router

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
the same address, but the lab does not use it; see the DNS forwarding note below.

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
every client gets SERVFAIL; see [[Troubleshooting]] (2026-09-17).

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

`compare` shows the pending change. `commit` makes it live. `save` writes it to
`/config/config.boot` so it survives a reboot; commit alone does not.

The saved configuration will contain more than the commands above: NTP, syslog, console,
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

The `dig` tests the forwarder clients use; the pings only prove the router resolves for itself.

**Verified 2026-09-17:** all checks pass; `dig @10.10.10.3` returns NOERROR in 32 ms.

From the Windows host, confirm management access:

```
ssh vyos@10.10.10.3
```

## 1.6 Compare with the repository

```
show configuration commands
```

The output should match [[vyos01.config]], apart from the `hw-id` MAC addresses and the password
hash.

---

# Stage 2 - infra01 and ansible01

Two Rocky Linux VMs, installed from the boot ISO, which pulls packages from the Rocky mirrors
through vyos01. infra01 will serve DNS and NTP to the lab; ansible01
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
| CD/DVD | `Rocky-10.2-x86_64-boot.iso`, connected at power on | same |

With each VM powered off, add to its `.vmx`:

```
rtc.diffFromUTC = "0"
```

## 2.2 Rocky installer settings

Identical for both machines except the highlighted rows. Configure Network & Host Name first;
Installation Source reaches the mirrors only once the network is up.

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
| Installation Source             | Closest mirror, no proxy                                                            |
| Root Account                    | **Lock root account**                                                               |
| User Creation                   | `labadmin`, "Make this user administrator" checked, password recorded in `creds.md` |

Begin installation, then reboot and disconnect the ISO.

DNS points at vyos01 until Stage 3 moves every node to infra01.

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

As `labadmin`:

```
sudo dnf -y install git
sudo python3 -m venv /opt/ansible
sudo /opt/ansible/bin/pip install --upgrade pip
sudo /opt/ansible/bin/pip install ansible-core ansible-lint yamllint
echo 'export PATH=/opt/ansible/bin:$PATH' | sudo tee /etc/profile.d/ansible.sh
ssh-keygen -t ed25519 -N '' -C 'labadmin@ansible01' -f ~/.ssh/id_ed25519
git clone https://github.com/isaacsgober/RangeLab.git ~/RangeLab
```

Log out and back in so the `PATH` change applies, then install the collection the playbooks use for
SSH keys and firewalld:

```
ansible-galaxy collection install ansible.posix
```

- Ansible comes from pip rather than Rocky's 2.16 package, in one environment with ansible-lint so
  both use the same core. `dnf update` does not update it.
- Playbooks run as `labadmin`. `ansible` is the account Ansible logs in to on managed nodes, and
  Stage 3 creates it on every node, this one included (ADR-0002).
- The key has no passphrase so playbooks run unattended; it never leaves this host.

## 2.5 Checks

```
which ansible-playbook
ansible --version | head -1
ansible-lint --version
ansible-galaxy collection list | grep posix
```

Expected: `/opt/ansible/bin/ansible-playbook`; **the same ansible-core version from `ansible` and
`ansible-lint`**; `ansible.posix` listed.

**Verified 2026-09-17:** ansible-core 2.21.4, ansible-lint 26.8.0 on the same core,
ansible.posix 2.2.2.

---

# Stage 3 - Ansible: bootstrap and converge

Turns infra01 and ansible01 into managed nodes and configures time and DNS. Everything runs from
`~/RangeLab/Ansible` on ansible01, as `labadmin`. The inventory, variables, and roles are already in
the repository; their layout is in `Ansible/README.md`.

The inventory names every node by FQDN and keeps its address in `lab_address` (ADR-0008).
`dns_extra_records` lists the nodes Ansible does not manage, so their records exist from the first
converge, before those nodes are built.

## 3.1 Bootstrap

No lab name resolves yet, so the first two runs connect by address. Accept each host key first;
Ansible cannot answer SSH's prompt:

```
ssh labadmin@10.10.10.2 exit
ssh labadmin@10.10.10.20 exit
ansible-playbook bootstrap.yml -e 'ansible_user=labadmin ansible_host={{ lab_address }}' -k -K
```

Creates the `ansible` service account, authorises ansible01's key, and installs the sudoers
drop-in (ADR-0002). Use `-e`, not `-u`: command-line options lose to inventory variables, extra
vars win. Expect `changed=3` per node.

## 3.2 First converge

```
ansible-playbook site.yml -e 'ansible_host={{ lab_address }}'
```

| Role | Result |
| ---- | ------ |
| `common` | Base utilities, persistent journal; `--tags update` runs a package update |
| `ntp` | chrony: infra01 syncs from the public pool and serves the lab; every other node syncs from infra01 |
| `dns` | dnsmasq on infra01 with records generated from the inventory; every node resolves through it |

Names resolve from here on. Accept each host key again by name, since SSH records keys per name:

```
ssh ansible@infra01.rangelab.internal exit
ssh ansible@ansible01.rangelab.internal exit
```

Later runs need no flags. If DNS fails, `-e 'ansible_host={{ lab_address }}'` restores
connectivity for a run.

## 3.3 Checks

```
ansible all -m ping
ansible-playbook site.yml
ansible all -m command -a 'chronyc sources'
ansible ntp_servers -b -m command -a 'chronyc clients'
ansible all -m command -a 'dig +short vcenter01.rangelab.internal'
ansible all -m command -a 'dig +short rockylinux.org'
ansible all -m command -a 'dig infra01.rangelab.internal AAAA'
```

Expected: `pong` from both nodes; the second run reports `changed=0` with no handlers; every node
`^*` on its time source, with ansible01 listed as an infra01 client; lab, extra-record, and external
names resolving; the AAAA query returning `NOERROR` with an empty answer, not `NXDOMAIN`.

**Verified 2026-09-18:** both nodes at `changed=0`; infra01 at stratum 3, ansible01 at 4; all names
resolving; AAAA returning NODATA.

`getent hosts` on infra01 for its own name returns a link-local IPv6 address. That is
`nss-myhostname`, not DNS; see [[Troubleshooting]] (2026-09-18).

## 3.4 Adding a node

For a Rocky node installed after this stage, such as managed01 in Stage 6. A node new to the lab
first needs an entry under `all.hosts` in the inventory, with its `lab_address`; a rebuild from
`main` already has one.

Publish the node's DNS record, then bootstrap and converge it by name:

```
ansible-playbook site.yml --limit dns_servers --tags dns
ssh labadmin@<fqdn> exit
ansible-playbook bootstrap.yml -e ansible_user=labadmin -k -K --limit <fqdn>
ansible-playbook site.yml
```

`--limit` restricts which hosts run tasks, not which hosts the inventory holds, so the DNS server
generates the new node's record even though nothing runs on the new node. Limiting by the
`dns_servers` group keeps the command independent of which host serves DNS.

Expected: `ansible all -m ping` answers from every node, and a second `site.yml` run reports
`changed=0`.

---

# Stage 4 - esxi01, the nested hypervisor

esxi01 is a VMware ESXi 9.1 host running inside Workstation. It hosts vcenter01 and managed01 and
nothing else; the services the lab depends on stay outside it (ADR-0006). ESXi is configured by
hand in the DCUI and over SSH, not by Ansible.

## 4.1 Create the VM

**File → New Virtual Machine → Custom**.

| Setting | Value | Why |
| ------- | ----- | --- |
| Guest OS | VMware ESX → VMware ESXi 9 | The profile forces EFI; no firmware choice is offered |
| Name | `esxi01` | [[Naming Convention]] |
| Processors | 1 socket, 6 cores | Room for vcenter01 (`small`, 4 vCPU) and managed01 |
| Memory | 64 GB | vcenter01 `small` needs 21 GB |
| Disk 1 | 128 GB, single file, PVSCSI | Boot device |
| Disk 2 | 400 GB, single file, same controller | Datastore; add in VM Settings after the wizard, which creates only one disk |
| Network adapter | Custom → **VMnet10**, `vmxnet3` | Management network |
| CD/DVD | `VMware-VMvisor-Installer-9.1.0.0200.25557999.x86_64.iso` | Install media |

Processors → **Virtualize Intel VT-x/EPT or AMD-V/RVI** must be checked (`vhv.enable = "TRUE"`).
The ESXi profile checks it by default; without it nothing can run inside esxi01. Then, powered off,
add to `esxi01.vmx`:

```
rtc.diffFromUTC = "0"
```

## 4.2 Install

Boot from the ISO, install to the 128 GB disk, set the root password (recorded in `creds.md`), and
reboot. Clear **Connect at power on** for the CD/DVD afterwards.

The 128 GB boot disk produces **no local datastore**. ESXi 9 claims about 138 GB for system media
and only creates a VMFS datastore on the boot disk above roughly 142 GB. That is expected; disk 2
becomes the datastore in 4.4.

## 4.3 Management network (DCUI)

**Configure Management Network:**

| Setting | Value |
| ------- | ----- |
| IPv4 | Static, `10.10.10.10`, `255.255.255.0`, gateway `10.10.10.3` |
| DNS servers | `10.10.10.2` |
| Hostname | `esxi01.rangelab.internal` |
| Custom DNS suffixes | `rangelab.internal` |

The DNS server stays an address; everything else refers to hosts by name (ADR-0008). Apply and
restart the management network when prompted.

**Troubleshooting Options → Enable SSH.** NTP in 4.4 is set over SSH. SSH enabled here does not
survive a reboot; it stays on demand, ESXi's default, and is re-enabled when needed.

**Test Management Network**, adding `1.1.1.1` as an extra address to ping. It pings the gateway,
the DNS server, and the extra address, and resolves the host's own name, which infra01 has served
since Stage 3.

## 4.4 NTP and storage

Over SSH as root:

```
esxcli system ntp set --server=infra01.rangelab.internal --enabled=true
esxcli system ntp get
```

`--enabled=true` starts `ntpd` and sets it to start with the host.

In the Host Client (`https://esxi01.rangelab.internal`): **Storage → New datastore**, VMFS 6, on the
400 GB disk, named `datastore01-01` ([[Naming Convention]]: first datastore on host 01).

## 4.5 Certificate

The installer's self-signed certificate names `localhost.localdomain`. Leave it: when vCenter adds
the host in Stage 6, it accepts the certificate by thumbprint and replaces it with a VMCA-signed one
carrying the name used for the add. Add **by FQDN**; adding by IP puts an IP-only SAN in the
replacement.

**Verified 2026-09-18:** after the add, `rui.crt` shows `DNS:esxi01.rangelab.internal`, issued by
the VMCA root. No manual regeneration needed.

## 4.6 Checks

```
esxcli network ip interface ipv4 get
esxcli network ip dns server list
esxcli system ntp get
ntpq -p
esxcli storage filesystem list
```

Expected: `vmk0` at `10.10.10.10/24`; DNS server `10.10.10.2`; NTP enabled with
`infra01.rangelab.internal`; `ntpq -p` showing `*` against infra01 after a few minutes;
`datastore01-01` mounted, about 400 GB, VMFS 6, and no datastore on the boot disk.

**Verified 2026-09-18:** DCUI Test Management Network passed all four checks (gateway, DNS server,
`1.1.1.1`, own-name resolution); `ntpq -p` showing `*` on infra01; `datastore01-01` created on the
400 GB disk. Evaluation license expires 2026-12-16.

---

# Stage 5 - vcenter01

vcenter01 is the vCenter Server Appliance, deployed onto esxi01. It is an appliance: configured
through its installer, VAMI, and the vSphere Client, never by editing the Photon OS underneath, and
not managed by Ansible.

## 5.1 Pre-flight

The installer checks DNS. vcenter01's record has been served since Stage 3; confirm it from any
lab node:

```
dig +short vcenter01.rangelab.internal
dig -x 10.10.10.15 +short
dig vcenter01.rangelab.internal AAAA
```

Expected: `10.10.10.15`; `vcenter01.rangelab.internal.`; `NOERROR` with an empty answer.

## 5.2 Deploy the appliance (installer stage 1)

Run `vcsa-ui-installer\win32\installer.exe` from the VCSA 9.1 ISO on the Windows host, **Install**.

| Setting | Value |
| ------- | ----- |
| Target | `esxi01.rangelab.internal`, root |
| VM name | `vcenter01` |
| Deployment size | Small (4 vCPU, 21 GB) |
| Datastore | `datastore01-01`, thin disk mode |
| Network | VM Network |
| FQDN | `vcenter01.rangelab.internal` |
| IP | `10.10.10.15/24`, gateway `10.10.10.3` |
| DNS server | `10.10.10.2` |

Root password recorded in `creds.md`.

## 5.3 Configure the appliance (installer stage 2)

| Setting | Value |
| ------- | ----- |
| Time synchronization | NTP, `infra01.rangelab.internal` |
| SSH | Enabled |
| SSO domain | `vsphere.local` |
| Administrator | `administrator@vsphere.local`, password in `creds.md` |
| CEIP | On |

`vsphere.local` is vCenter's internal directory name, not a DNS name. It must never match an Active
Directory domain and cannot be renamed later.

## 5.4 Checks

From the Windows host, without credentials:

```
echo | openssl s_client -connect 10.10.10.15:443 -servername vcenter01.rangelab.internal 2>/dev/null | openssl x509 -noout -subject -issuer -ext subjectAltName
```

Expected: subject and SAN `vcenter01.rangelab.internal`, issued by the VMCA root (`DC=vsphere,
DC=local`). Then sign in to the vSphere Client at `https://vcenter01.rangelab.internal/ui` as
`administrator@vsphere.local`.

**Verified 2026-09-18:** vCenter Server 9.1.0.0200, build 25573614; machine certificate
`CN=vcenter01.rangelab.internal` with matching SAN, issued by VMCA, valid to 2028-09-18.
Evaluation license expires 2026-12-17.

---

# Stage 6 - vSphere configuration and managed01

Brings esxi01 under vCenter, sets the host's startup order, and builds managed01, the Rocky node
nested inside esxi01.

## 6.1 Datacenter and host

In the vSphere Client at `https://vcenter01.rangelab.internal/ui`:

1. **New Datacenter**: `rangelab`.
2. **Add Host**: `esxi01.rangelab.internal`, by FQDN, with the root credentials. Accept the
   certificate thumbprint, keep the evaluation license, and leave lockdown mode disabled.

vCenter replaces esxi01's installer certificate with a VMCA-signed one carrying the FQDN. Adding
by IP would put an IP-only SAN in that certificate.

## 6.2 Startup and shutdown order

esxi01 → Configure → **VM Startup/Shutdown** → Edit:

| Setting | Value |
| ------- | ----- |
| Automatically start and stop the virtual machines with the system | Checked |
| Default startup delay / shutdown delay | 120 s / 120 s |
| Continue if VMware Tools is started | Checked |
| Shutdown action | Guest shutdown |

| Order | VM | Startup | VMware Tools | Shutdown delay |
| ----- | -- | ------- | ------------ | -------------- |
| 1 | vcenter01 | Enabled | System default | 600 s |
| 2 | managed01 | Enabled | System default | 120 s |

vcenter01 starts first because it takes longest to become usable; DNS and time are already up
outside esxi01. It gets 600 seconds to shut down, since a guest cut off mid-shutdown is powered off,
and hard-stopping the appliance's database can corrupt vCenter. Guest shutdown requires VMware
Tools in each guest.

## 6.3 Create managed01

New Virtual Machine on esxi01:

| Setting | Value |
| ------- | ----- |
| Name | `managed01` |
| Storage | `datastore01-01`, thin; Storage DRS setting irrelevant with a single datastore |
| Guest OS | Linux → Red Hat Enterprise Linux 10 (64-bit) |
| CPU / memory | 2 vCPU / 2 GB |
| Disk | 30 GB, PVSCSI |
| Network | VM Network, `vmxnet3` |
| Firmware | EFI (the profile's default) |
| CD/DVD | `Rocky-10.2-x86_64-boot.iso`, uploaded to `datastore01-01` |

Install with the Stage 2.2 settings, except:

- Address `10.10.10.21`, hostname `managed01.rangelab.internal`.
- DNS `10.10.10.2`. infra01 exists by now, so the node points at its permanent DNS server from
  the start.

Minimal Install includes `open-vm-tools` on VMware, which the guest shutdown in 6.2 depends on.

## 6.4 Bring managed01 under Ansible

Add it as a node per 3.4. Its inventory entry already exists in `main`.

## 6.5 Checks

```
echo | openssl s_client -connect esxi01.rangelab.internal:443 2>/dev/null | openssl x509 -noout -subject -issuer -ext subjectAltName
ansible managed01.rangelab.internal -m command -a 'chronyc sources'
ansible managed01.rangelab.internal -m command -a 'rpm -q open-vm-tools'
ansible all -m ping
```

Expected: esxi01's certificate issued by the VMCA root with `DNS:esxi01.rangelab.internal`;
managed01 `^*` on infra01; `open-vm-tools` installed; `pong` from all three managed nodes.

**Verified 2026-09-18:** esxi01 certificate VMCA-issued with the FQDN SAN; managed01 on Rocky 10.2,
EFI, `vmxnet3`, synchronised to infra01 (stratum 4), resolving through `10.10.10.2`,
`open-vm-tools` 13.0.10; all three nodes converged to `changed=0`.

---

# Stage 7 - Verification

A cold shutdown and boot of the whole lab, then every earlier stage's checks in one pass.

## 7.1 Cold shutdown and boot

Shut down in the order in [[Operations]], leave everything off for at least 15 minutes so the
clocks have drift to correct, then boot in the order given there.

## 7.2 Checks

From ansible01, in `~/RangeLab/Ansible`:

```
python ../Scripts/healthcheck.py vyos01.rangelab.internal infra01.rangelab.internal ansible01.rangelab.internal vcenter01.rangelab.internal managed01.rangelab.internal
python ../Scripts/healthcheck.py -p 443 esxi01.rangelab.internal
ansible-playbook site.yml
ansible all -m command -a 'chronyc sources'
```

On esxi01, with SSH enabled for the check:

```
esxcli system ntp get
```

From the Windows host:

```
python Scripts\vcenter_inventory.py
```

Expected: every host reachable, with esxi01 checked on 443 since its SSH does not survive a reboot;
`changed=0` on every managed node; every chrony node `^*` on its source; `Time Synchronized: true`
on esxi01; vcenter01 and managed01 listed as `POWERED_ON`.

**Verified 2026-09-18:** all checks pass with no manual intervention. Names resolved at boot, so
dnsmasq came up under `bind-dynamic`; clocks were corrected after the time powered off; autostart
brought up both nested VMs; the vCenter API answered.
