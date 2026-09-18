
# Build Sequence

How to build Range Lab from nothing. Written during the 2026-09-16 rebuild, one stage at a time,
from what actually worked. Design and reasoning: [[Rebuild-Plan]]. The lab this replaced is
recorded in `vault/Attachments/as-built-2026-09-15/` and tagged `pre-rebuild`.

**Conventions in this document**

- Commands are shown exactly as typed. Output shown is the real output, trimmed.
- Every stage ends with checks. No stage begins until the previous stage's checks pass.
- Values (addresses, names, sizes) come from [[IP Index]] and [[Naming Convention]].

## Prerequisites

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

The `dig` is not optional: the pings only prove the router resolves for itself, and the forwarding
service is what clients use.

**Result, 2026-09-16:** all three pings replied, including `vyos.net`, which also proves the
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
`set system login user vyos authentication encrypted-password` line replaced by a placeholder  - 
keeping the line shows the account exists without publishing its hash.

Then write the device note, [[vyos01]], from the same output.

**Not configured yet:** vyos01 has no firewall policy. Its WAN side sits on Workstation's private
NAT network, so it isn't exposed to the internet directly. Tracked as a follow-up.

---

# Stage 2 - infra01 and ansible01

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

**Why DNS points at the router here:** infra01 is not serving DNS yet; it is the machine being
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
ansible-lint in the same environment keeps the linter and the runtime on one version; installed
separately, the linter checks playbooks against a core the node does not run.

Ansible here is pip-managed, so `dnf update` will not touch it. Refresh it with
`sudo /opt/ansible/bin/pip install -U ansible-core ansible-lint`.

`PATH` from `/etc/profile.d` reaches login and interactive shells, but not cron, systemd units, or
`ssh host '<command>'`. Use the full `/opt/ansible/bin/` path in those.

**Playbooks run as `labadmin`, not as the `ansible` account.** `ansible` is the account Ansible
logs in to on managed nodes (ADR-0002); the account invoking `ansible-playbook` does not have to
carry that name. Running as labadmin keeps the working copy, the SSH key, and the collections in
one account that owns its own home, which removes every `sudo -u` and permission workaround from
routine use.

Generate the key Ansible presents to managed nodes:

```
ssh-keygen -t ed25519 -N '' -C 'labadmin@ansible01' -f ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
```

No passphrase, so playbooks run unattended; the private key stays on this host and out of the
repository. Stage 3's bootstrap play installs the public key on every node.

Clone the repository (public, so no credentials) and add the collection the playbooks need:

```
git clone -b <working-branch> https://github.com/isaacsgober/RangeLab.git ~/RangeLab
ansible-galaxy collection install ansible.posix
```

Collections install per account, under `~/.ansible/collections`, so this runs as the account that
runs playbooks. Name the branch explicitly; a plain clone lands on `main`.

The `ansible` service account is **not** created here. `bootstrap.yml` creates it on every node
including this one, so there is one mechanism rather than a hand-built exception.

## 2.5 Checks

As `labadmin`:

```
which ansible-playbook
ansible --version | head -1
ansible-lint --version
ansible-galaxy collection list | grep posix
git -C ~/RangeLab log --oneline -1
```

Expected: `/opt/ansible/bin/ansible-playbook`; **the same ansible-core version from both `ansible`
and `ansible-lint`**; `ansible.posix` listed; the clone's latest commit matching GitHub.

**Verified 2026-09-17:** ansible-core 2.21.4 (pip), ansible-lint 26.8.0 on the same core,
ansible.posix 2.2.2, Python 3.12.13, clone at `bc756a5`.

Record the installed versions in the device note; they pin what this build was tested with.

---

# Stage 3 - Ansible: bootstrap and the base roles

Stage 3 turns two installed machines into managed nodes, then configures time and DNS from the
repository. Everything here runs from `~labadmin/RangeLab/Ansible` on ansible01.

Layout produced by this stage:

```
Ansible/
├── ansible.cfg
├── bootstrap.yml
├── site.yml
├── inventory/hosts.yml
├── group_vars/all.yml
└── roles/{common,ntp,dns}/{tasks,handlers,templates,files}
```

## 3.1 Inventory and variables

Each host is declared once under `all.hosts` with its `ansible_host`, and groups below it carry
membership only. Groups are named for the service a member provides, so a node's role is declared
in exactly one place.

```yaml
all:
  vars:
    ansible_user: ansible
    ansible_python_interpreter: /usr/bin/python3
  hosts:
    ansible01.rangelab.internal:
      ansible_host: 10.10.10.20
    infra01.rangelab.internal:
      ansible_host: 10.10.10.2
  children:
    control:
      hosts:
        ansible01.rangelab.internal:
    dns_servers:
      hosts:
        infra01.rangelab.internal:
    ntp_servers:
      hosts:
        infra01.rangelab.internal:
```

`ansible_host` carries the address so nothing depends on DNS that does not exist yet.
`ansible_python_interpreter` is pinned because ansible01 has `/opt/ansible/bin` first on `PATH`;
without the pin, modules there run under the virtual environment's Python, which cannot import the
system `dnf` bindings.

`group_vars/all.yml` derives service addresses from the inventory rather than repeating them:

```yaml
dns_server_host: "{{ groups['dns_servers'] | first }}"
ntp_server_host: "{{ groups['ntp_servers'] | first }}"
lab_network: 10.10.10.0/24
lab_domain: rangelab.internal
dns_upstream: 10.10.10.3
dns_extra_records:
  vyos01.rangelab.internal: 10.10.10.3
```

`dns_extra_records` covers hosts Ansible does not manage; managed hosts come from the inventory.

## 3.2 Bootstrap

`bootstrap.yml` creates the `ansible` service account, authorises the control node's public key,
and installs the sudoers drop-in (ADR-0002). It runs once per node, as `labadmin` with password
authentication, because the key it installs does not exist on the targets yet.

Accept each host key first. SSH refuses unknown hosts non-interactively, and Ansible cannot answer
the prompt:

```
ssh labadmin@10.10.10.2 exit
ssh labadmin@10.10.10.20 exit
```

```
ansible-playbook bootstrap.yml -e ansible_user=labadmin -k -K
```

**Use `-e`, not `-u`.** Command-line values such as `-u` sit at the bottom of Ansible's variable
precedence and lose to `ansible_user` from the inventory. Extra vars win outright.

Expect `changed=3` per node on the first run. Then, with no flags at all:

```
ansible all -m ping
```

`pong` from both nodes proves the account, the key, and the inventory together.

## 3.3 The roles

`site.yml` applies them in order; role order in the list is execution order.

```yaml
---
- name: Configure all nodes
  hosts: all
  become: true
  roles:
    - common
    - ntp
    - dns
```

**common** installs the base utilities and makes the journal persistent. A package-update task is
tagged `never, update`, so it runs only with `--tags update`.

**ntp** installs chrony, templates `/etc/chrony.conf`, runs `chronyd`, and opens 123/UDP on the
time server. One template serves both sides and branches on group membership:

```jinja
{% if 'ntp_servers' in group_names %}
pool 2.rocky.pool.ntp.org iburst
allow {{ lab_network }}
{% else %}
server {{ hostvars[ntp_server_host].ansible_host }} iburst
{% endif %}
```

The client line uses `hostvars[...]` rather than a name, so time does not depend on DNS.

**dns** has server tasks gated on `dns_servers` membership and client tasks that run everywhere,
the DNS server included, since it resolves through itself. Client tasks come last: under the
default `linear` strategy every host finishes a task before any host starts the next, so dnsmasq is
serving before anything is pointed at it.

Server side, `/etc/dnsmasq.conf` is templated whole. Records are generated from the inventory:

```jinja
{% for host in groups['all'] %}
host-record={{ host }},{{ hostvars[host].ansible_host }}
{% endfor %}
```

`host-record` creates the A and the PTR together and makes the name exist for every query type. The
pre-rebuild lab used `address=` rules, which answer only A and let other types fall through to
NXDOMAIN; see [[Troubleshooting]] (2026-09-15).

`no-resolv` is required. Without it dnsmasq takes its upstreams from `/etc/resolv.conf`, which the
client tasks point at dnsmasq itself. `bind-dynamic` rather than `bind-interfaces`: the first binds
interfaces as they appear, the second binds at startup and fails if dnsmasq starts before the
interface is up, which is a cold-boot race.

Client side, two files: a NetworkManager drop-in at `/etc/NetworkManager/conf.d/90-dns-none.conf`
containing `dns=none`, and `/etc/resolv.conf`. NetworkManager owns that file by default and
overwrites anything written there, so it has to be told to stop before the resolver is set.

## 3.4 Checks

```
ansible-playbook site.yml
ansible all -m command -a 'chronyc sources'
ansible ntp_servers -b -m command -a 'chronyc clients'
ansible all -m command -a 'getent hosts vyos01.rangelab.internal'
ansible all -m command -a 'dig +short rockylinux.org'
ansible all -m command -a 'dig infra01.rangelab.internal AAAA'
ansible dns_servers -b -m command -a 'NetworkManager --print-config'
```

Expected: a second run reports `changed=0` with no handlers firing; every node `^*` on its source,
with clients one stratum below the server; the server listing its clients; lab and external names
resolving; the AAAA query returning `NOERROR` with an empty answer section rather than `NXDOMAIN`;
and `dns=none` present in the merged NetworkManager configuration.

**Verified 2026-09-18:** both nodes converged to `changed=0`; ansible01 synchronised to `10.10.10.2`
at stratum 3 and listed as a client on infra01; lab, extra-record, and external names all resolving;
AAAA returning NODATA.

On the DNS server, `getent hosts <its own FQDN>` returns a link-local IPv6 address rather than its
lab address. That is `nss-myhostname` answering for the machine's own name after DNS returns NODATA
for the AAAA query, not a DNS fault; `getent ahostsv4` returns the correct address. See
[[Troubleshooting]] (2026-09-18).
