# Homelab Infrastructure Automation Project Checklist

## Project goal

Extend the existing ESXi/vCenter and Rocky Linux DNS homelab into a small, documented infrastructure-automation environment. The finished project should provide honest, demonstrable experience with Linux, networking, DNS, SSH, Git, YAML, Ansible, basic scripting, and API interaction.

Target progression:

`ESXi/vCenter -> Rocky Linux VMs -> DNS -> Git repository -> Ansible control node -> automated configuration -> script/API exercise`

Do not add a technology to the resume merely because it was installed. Add it after it has been used, tested, troubleshot, and documented.

## Phase 0 — Preserve and document the current baseline

- [x] Record the ESXi host version, vCenter version, VM names, IP addresses, virtual switches, port groups, and VLANs in use.
- [x] Draw a simple logical network diagram showing the ESXi host, vCenter, Rocky Linux DNS VM, router/gateway, management network, and guest systems.
- [x] Document how vCenter depends on DNS and which forward and reverse records support the environment.
- [x] Save screenshots or command output showing successful forward lookup, reverse lookup, and vCenter access by hostname.
- [x] Create a short recovery note explaining how to restore lab access if DNS is unavailable.
- [x] Remove passwords, private keys, tokens, public IP addresses, and other secrets from anything intended for a public repository.

**Completion evidence:** A current diagram, sanitized configuration notes, successful DNS test results, and a brief recovery procedure.
See [[Phase 0 Screenshots]].
## Phase 1 — Build a Git-backed documentation repository

- [x] Create a repository named something like `virtualized-infrastructure-homelab`.
- [x] Add a `README.md` describing the project goal, architecture, hardware/software used, and current status.
- [x] Add directories for `docs/`, `diagrams/`, `ansible/`, and `scripts/`.
- [x] Add the sanitized topology diagram and baseline documentation.
- [x] Add a `.gitignore` that excludes private keys, credentials, environment files, logs, and temporary files.
- [ ] Practice `clone`, `status`, `add`, `commit`, `push`, `pull`, branch creation, merge, and viewing commit history.
- [x] Make several small, descriptive commits instead of one large initial upload.
- [x] Verify that a fresh clone contains no secrets and that its documentation renders correctly.

**Completion evidence:** A readable repository with meaningful commit history and no sensitive information.

## Phase 2 — Add Linux systems for automation practice

- [x] Deploy one Rocky Linux VM as an Ansible control node.
- [x] Deploy at least one separate Rocky Linux VM as a managed node.
- [x] Assign documented hostnames and IP addresses using the lab's existing addressing plan.
- [x] Add forward and reverse DNS records for the new systems.
- [x] Create a non-root administrative account and configure `sudo` appropriately.
- [x] Configure SSH key-based authentication from the control node to the managed node.
- [x] Confirm hostname resolution, ICMP connectivity, SSH access, time synchronization, and package repository access.
- [x] Record a troubleshooting log for at least one issue encountered and resolved.

**Completion evidence:** The control node can resolve and connect to the managed node by hostname using SSH keys.

## Phase 3 — Configure the managed node with Ansible

- [x] Install Ansible on the control node.
- [ ] Create a YAML inventory using DNS hostnames rather than hard-coded ad hoc commands.
- [ ] Run `ansible all -m ping` successfully against the managed node.
- [ ] Write a playbook that updates packages and installs a small set of utilities.
- [ ] Add tasks to create a user, deploy an SSH public key, configure a service, and copy a managed configuration file.
- [ ] Use handlers so services restart only when configuration changes.
- [ ] Use variables for values that may differ between hosts or environments.
- [ ] Run `ansible-lint` and correct reasonable findings.
- [ ] Run the playbook twice and verify that the second run reports no unnecessary changes.
- [ ] Intentionally introduce a safe configuration problem, diagnose it, fix the playbook, and document the result.

**Completion evidence:** A repeatable playbook, successful idempotency check, and documented troubleshooting example.

## Phase 4 — Add a small Bash or Python utility

- [ ] Choose one bounded task, such as checking DNS resolution, testing TCP ports, reporting VM reachability, or validating required services.
- [ ] Implement the utility in Bash or Python with clear comments and readable output.
- [ ] Accept hostnames or settings through command-line arguments or a configuration file rather than embedding them throughout the code.
- [ ] Handle common failures such as an unresolved hostname, refused connection, timeout, or missing dependency.
- [ ] Test both successful and unsuccessful cases.
- [ ] Add usage instructions and sample sanitized output to the repository.

**Completion evidence:** A reusable script with documented inputs, outputs, error handling, and test cases.

## Phase 5 — Exercise an API

- [ ] Choose a safe read-only API, preferably the vCenter REST API if available in the lab.
- [ ] Use `curl` first to authenticate and request a small piece of inventory data, such as VM names or power state.
- [ ] Store credentials outside the script or repository using an environment file excluded by `.gitignore`, a credential store, or interactive input.
- [ ] Repeat the read-only request in Python if Phase 4 used Python or as a separate small exercise.
- [ ] Handle authentication failure and unreachable-service errors.
- [ ] Document the endpoint, request purpose, response fields used, and security precautions without publishing credentials.

**Completion evidence:** A sanitized example showing successful read-only API interaction and safe credential handling.

## Phase 6 — Package the project for review

- [ ] Update the architecture diagram to include the control and managed nodes.
- [ ] Write a concise build sequence that another person could follow.
- [ ] Add a `Troubleshooting.md` covering at least DNS, SSH, and one Ansible issue.
- [ ] Add a `Lessons-Learned.md` describing what worked, what failed, and what would be improved next.
- [ ] Verify all commands and playbooks from a clean repository clone.
- [ ] Check the repository again for secrets, personal data, internal domain names, and unsafe screenshots.
- [ ] Ask another person to follow the README and identify unclear steps.
- [ ] Tag a first completed release, such as `v1.0`.

**Completion evidence:** A reviewer can understand the architecture, reproduce the core configuration, and see proof that the automation was tested.

## Optional extension — Safe security fundamentals

- [ ] Apply basic Rocky Linux hardening appropriate for a lab, such as least-privilege accounts, SSH settings, firewall rules, and timely updates.
- [ ] Automate the selected settings with Ansible.
- [ ] Verify that required services still function after the changes.
- [ ] Document why each control was chosen and how it was tested.
- [ ] Keep all security testing confined to systems owned by and explicitly designated for the lab.

This extension supports a claim of introductory system-hardening practice. It does not establish operational cybersecurity, red-team, blue-team, incident-response, or penetration-testing experience.

## Resume update gate

Only after the relevant phases are complete, consider adding:

- **Development Tools:** Git, GitHub or GitLab, Visual Studio Code
- **Automation:** Introductory Ansible, YAML, Bash or Python
- **Infrastructure:** SSH, Linux package and service management, DNS administration
- **APIs:** Basic REST API interaction with `curl` or Python

Possible project bullets after the work is completed and verified:

- Extended a VMware ESXi/vCenter homelab with Rocky Linux control and managed nodes, DNS-based hostname resolution, and SSH key authentication.
- Created a Git-tracked Ansible inventory and idempotent playbook to configure Linux users, packages, services, SSH access, and managed configuration files.
- Developed a small Bash or Python validation utility and used a read-only REST API to retrieve virtual machine inventory data.
- Documented architecture, build procedures, troubleshooting steps, and lessons learned in a sanitized technical repository.

Use only the bullets that precisely describe completed work. Replace generic phrases with measured details when available, such as number of VMs managed, number of playbook tasks, or specific services configured.

## Final review checklist

- [ ] Every resume claim can be demonstrated live or explained step by step.
- [ ] No production or enterprise administration is implied by homelab-only work.
- [ ] No certification is presented as earned before the exam is passed.
- [ ] No passwords, keys, tokens, or sensitive network information appear in the repository.
- [ ] The project has a clear problem, architecture, implementation, test evidence, and lessons learned.
- [ ] The candidate can explain one failure and the troubleshooting process used to resolve it.
