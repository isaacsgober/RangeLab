# RangeLab Ansible

Configuration management for the lab's Rocky nodes. Design and reasoning live in the vault:
[Build-Sequence](../vault/Docs/Build-Sequence.md) Stage 3 for how this was built,
[Development-Workflow](../vault/Docs/Development-Workflow.md) for how it is worked on.

## Layout

```
Ansible/
├── ansible.cfg               points at inventory/hosts.yml
├── bootstrap.yml             creates the ansible service account on a new node
├── site.yml                  applies common, ntp, dns
├── inventory/hosts.yml       hosts with addresses; groups named for services
├── group_vars/all.yml        base utilities and lab-wide values
└── roles/
    ├── common/               base packages, persistent journal
    ├── ntp/                  chrony: server on ntp_servers, client elsewhere
    └── dns/                  dnsmasq on dns_servers, resolver config everywhere
```

## Inventory

Each host is declared once with its address in `lab_address`; groups carry membership only.
Ansible connects by inventory name, the FQDN (ADR-0008). Group names
describe the service a member provides, so a node's role is declared in one place and roles derive
the rest:

```yaml
dns_server_host: "{{ groups['dns_servers'] | first }}"
ntp_server_host: "{{ groups['ntp_servers'] | first }}"
```

DNS records are generated from this inventory, so adding a node gives it records on the next
converge.

## Running

From `~/RangeLab/Ansible` on ansible01, as `labadmin`. Ansible connects to managed nodes as the
`ansible` service account using the key in `~labadmin/.ssh/id_ed25519`.

```bash
ansible-lint                               # whole project
ansible-playbook site.yml --check --diff   # dry run
ansible-playbook site.yml                  # apply
ansible-playbook site.yml --tags update    # opt-in package update
```

A converged run reports `changed=0` and fires no handlers.

## Bootstrapping a new node

A node with no `ansible` account is bootstrapped once, as `labadmin` with password authentication:

```bash
ssh labadmin@<address> exit                # accept the host key first
ansible-playbook bootstrap.yml -e 'ansible_user=labadmin ansible_host={{ lab_address }}' -k -K
```

If the node is not yet in DNS, converge it by address once; the `dns` role then publishes its
record:

```bash
ansible-playbook site.yml -e 'ansible_host={{ lab_address }}'
```

The same flag recovers management if DNS fails.

`-e` rather than `-u`: command-line values lose to inventory variables, extra vars win.

## Ansible on the control node

`ansible-core` and the linters are installed with pip into `/opt/ansible`, which keeps the runtime
and `ansible-lint` on one version. `dnf update` does not touch them:

```bash
sudo /opt/ansible/bin/pip install -U ansible-core ansible-lint
```
