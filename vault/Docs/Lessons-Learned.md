# Lessons Learned

What worked, what failed, and what comes next, drawn from the hand-built lab and its ground-up
rebuild in September 2026. Details live in [[Troubleshooting]], the ADRs, and [[Rebuild-Plan]].

---

## What worked

- **Rebuilding instead of patching.** The first lab reached Phase 6 carrying workarounds difficult to fully explain. It was a dirty pass, used to gain familiarity with the infrastructure. Rebuilding from nothing, one stage at a time with checks at the end of each,
  produced a lab that came back from a cold shutdown with no intervention.
- **Deriving configuration from one source.** The inventory declares each node once; DNS records,
  the DNS server, and the time server all derive from it. Adding managed01 took one inventory entry
  and a converge.
- **Recording decisions as they were made.** Eight ADRs capture why the lab is shaped the way it
  is, including the decisions that were later reversed (ADR-0003, ADR-0008).
- **Checks that test what clients use.** The most useful checks asked the question a client would
  ask: `dig @10.10.10.3` against the forwarder, AAAA queries for the NODATA case, and ping through
  Ansible rather than only ICMP.
- **Keeping lab services outside the hypervisor.** With DNS, time, and the control node beside
  esxi01 instead of inside it, the hypervisor can be rebuilt or broken without taking them down
  (ADR-0006).
- **Letting the platform do its job.** vCenter replaced esxi01's installer certificate on its own
  when the host was added by FQDN. The manual regeneration the first lab needed was never necessary.

---

## What failed, and why

- **An accidental air gap.** The first lab had no route out because it was built on a host-only
  network, not because anything required isolation. Every workaround followed from it: a frozen
  DVD repository, no linter, an invented clock (ADR-0007).
- **DNS rules that answered only half the question.** `address=` rules answered A queries and
  returned NXDOMAIN for AAAA, which vCenter cached as "this host does not exist." It surfaced as a
  vCenter add-host failure and was chased for an extended period of time as a certificate problem first (ISA-6).
- **A time server inside the hypervisor.** Suspending esxi01 froze the lab's only clock, and the lab
  split 3 h 49 m apart (ADR-0004).
- **Cloning VMs.** managed01 was cloned from ansible01 and inherited its machine-id and a package
  source without its mount.
- **Checks that passed for the wrong reason.** vyos01's `ping vyos.net` proved the router resolved
  for itself while its forwarder returned SERVFAIL to every client. `getent hosts` on infra01
  reported a link-local address that had nothing to do with DNS.
- **Configuration the platform overwrites.** Hand edits to `resolved.conf` on vCenter and to
  `/etc/resolv.conf` under NetworkManager looked applied and were silently replaced.
- **Two versions of one tool.** pip installed a second ansible-core as a linter dependency, so ansible-lint
  checked playbooks against a version of ansible-core the node did not run.
- **Settings carried forward without review.** `tags: always` from the first playbook made it into the common role, making
  `--tags dns` run both roles until it was noticed.

---

## What would be improved next

- **Prove the document.** Rebuild once more following [[Build-Sequence]] with no deviations, then
  have someone else follow the README (ISA-15).
- **Filter traffic at vyos01.** It routes and translates but filters nothing; the firewall policy
  is the next security step, written with Ansible's `vyos.vyos` collection (ISA-16).
- **Lint in CI, configured deliberately.** Ansible and Python checks on every push, with the
  dependencies, Python version, and pass threshold chosen rather than taken from a template.
- **Trust the VMCA root in the scripts** instead of disabling certificate verification.
- **Measure operations.** Record real start and stop times; [[Operations]] currently gives the
  configured limits.
- **Provision, not only configure.** Creating the VMs themselves from a specification, toward the
  roadmap's goal of building a range from a description.

---

## Related

- [[Troubleshooting]]
- [[Rebuild-Plan]]
- [[Build-Sequence]]
- [[Known-Issues]]
