# ADR-0002 - Dedicated service account for Ansible automation

## Revisions:

2026-09-07:
	Granted the `ansible` account passwordless sudo (`NOPASSWD: ALL`) via
	`/etc/sudoers.d/ansible` on all nodes, so playbook runs need no interactive
	become password. Tradeoff recorded under Consequences.

## Status

Accepted

---

## Context

Phase 2 introduces an Ansible control node (`ansible01`) and a managed node
(`managed01`), with additional managed nodes likely in later stages. Ansible connects
to managed hosts over SSH as a specific user, defined in the inventory.

During the initial build of `ansible01`, the interactive administrative account was
created with the same name as the host (`ansible01`). Realized that continuing that pattern 
would give every managed node a differently-named administrative account, requiring
per-host `ansible_user` overrides in the inventory and separate SSH key distribution
for each.

---

## Decision

Create a dedicated, non-interactive service account named `ansible` on the control
node and every managed node, added to the `wheel` group for sudo access. Ansible
connects as this account exclusively.

Existing per-host administrative accounts remain for interactive console and SSH
login. They are not used for automation.

`dnsmasqhost` is not currently an Ansible managed node. The `ansible` admin account has been created there in advance so the environment remains uniform.

---

## Rationale

- A single `ansible_user` value applies to all hosts, keeping the inventory free of
  per-host connection overrides.
- SSH public key distribution targets one known path (`/home/ansible/.ssh/authorized_keys`)
  on every node.
- Separating the automation account from human accounts makes it clear in logs and
  audit output which actions were performed by automation.
- Matches common practice in managed environments, where automation runs under a
  dedicated service identity rather than a person's account.

---

## Consequences

Advantages

- Inventory stays simple as node count grows.
- Automation activity is distinguishable from interactive administration.
- Adding a managed node requires creating one known account rather than deciding on a
  name.

Disadvantages

- An additional account exists on every host, which is one more thing to create,
  document, and eventually harden.
- The account holds passwordless sudo (see Revisions), so possession of its SSH
  private key is equivalent to unrestricted root on every node. This is the standard
  posture for an automation service account and is acceptable here because the key
  never leaves `ansible01` and the lab is isolated, but it concentrates risk in one
  credential and must be kept out of the repository. Rejected alternatives:
  `--ask-become-pass` (breaks unattended) and vaulting the become password
  (adds ceremony without improving security appreciably).

---

## Related

- [[ansible01]]
- [[managed01]]
- [[Naming Convention]]