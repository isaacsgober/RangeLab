# RangeLab Scripts

Helper scripts for the lab. See each script's own requirements below — some are
standard-library only, some need a `pip install`.

## healthcheck.py

Checks a list of hosts for DNS resolution and TCP port reachability. For each host it
resolves the name, opens a connection to a port (default 22), and prints the result.
Exit status is non-zero if any host fails, so the script can gate a shell command or a
later automation step.

### Requirements

- Python 3.10+ (uses only `argparse`, `socket`, `shutil`, `sys`)
- A network path to the targets — run it from the Windows host or any lab node

### Usage

```
python healthcheck.py [-p PORT] [-t TIMEOUT] host [host ...]
```

| Argument | Default | Meaning |
|----------|---------|---------|
| `host [host ...]` | — | One or more hostnames or IPs to check (required) |
| `-p`, `--port` | `22` | TCP port to test |
| `-t`, `--timeout` | `3.0` | Per-connection timeout, in seconds |
| `-h`, `--help` | — | Show usage and exit |

Arguments are separated by spaces, not commas.

### Examples

```
# SSH reachability for the two Rocky nodes
python healthcheck.py ansible01.rangelab.internal managed01.rangelab.internal

# vCenter web UI, one-second timeout
python healthcheck.py vcenter01.rangelab.internal -p 443 -t 1
```

### Sample output

Checking port 443 (management web UI) across three hosts:

```
==================================================================
CHECK CONNECTIVITY:
------------------------------------------------------------------
vcenter01.rangelab.internal | 10.10.10.15 | Port 443 is open
ansible01.rangelab.internal | 10.10.10.20 | Port 443 is closed (timeout)
bogus.rangelab.internal | could not be resolved
------------------------------------------------------------------
CONNECTIVITY CHECK COMPLETE: 1 pass, 2 fails
==================================================================
```

In a terminal the result lines are colored:

| Color  | Interpretation                        |
| ------ | ------------------------------------- |
| Green  | open                                  |
| Yellow | resolved but port closed or timed out |
| Red    | a DNS failure or other error          |

### Exit codes

| Code | Meaning                   |
| ---- | ------------------------- |
| `0`  | Every host passed         |
| `1`  | At least one host failed  |
| `2`  | Invalid/missing arguments |

### Failure handling

| Situation | Reported as |
|-----------|-------------|
| Name does not resolve | `could not be resolved` |
| Port closed | `Port N is closed (connection refused)` |
| No response before timeout | `Port N is closed (timeout)` |
| Other socket / OS error | `OS error: <detail>` |

### Testing

Exercised against live lab hosts and loopback, covering the success path and each
failure mode:

- open port — `ansible01`, `managed01` on 22
- DNS failure — a deliberately bogus name
- refused connection — `127.0.0.1` on a closed port
- timeout — port 443 on an SSH-only node
- other OS error — `--timeout 0`
- invalid arguments — non-integer `--port`, missing hosts

Exit codes all confirmed: `0` (all pass), `1` (a check failed), `2` (argparse rejects
bad arguments).

### Known limitations

- `--port` and `--timeout` are not range-checked (`--timeout 0` and out-of-range ports
  produce a generic error rather than a clean rejection).
- Color codes are emitted even when output is piped or redirected.
- All hosts to be tested must be passed on the command line; tedious for a large list.

These limitations are tracked for a follow-up revision.

## vcenter_inventory.py

Authenticates to the vCenter REST API and lists the VMs it currently manages. Meant to
be run directly - it prompts for credentials interactively - or imported: `login()` and
`list_vms()` are written to be called from other scripts.

### Requirements

- Python 3.10+
- `requests` (`pip install requests`) — not standard library
- A network path to vcenter01 and a vCenter SSO account (e.g. `administrator@vsphere.local`)

### Endpoints used

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/session` | Authenticate (HTTP Basic Auth), returns a session token |
| `GET` | `/api/vcenter/vm` | List VMs, using the token in a `vmware-api-session-id` header |

### Response fields used

Each VM entry (when any exist) carries `vm` (unique ID), `name`, and `power_state`
(`POWERED_ON` / `POWERED_OFF`).

### Usage

```
python vcenter_inventory.py
```

No arguments - prompts for username and password at runtime.

### Sample output

```
Enter vCenter username: administrator@vsphere.local
Enter password: 
[{'memory_size_MiB': 21504, 'vm': 'vm-14', 'name': 'vcenter01', 'power_state': 'POWERED_ON', 'cpu_count': 4}]
```

The VM list comes from `/api/vcenter/vm` and includes vcenter01 itself,
since it runs on esxi01, which vCenter now manages.

### Exit codes

| Code | Meaning |
|------|---------|
| `0`  | Login and VM list both succeeded |
| `1`  | Any request failed (see below) |

### Failure handling

| Situation | Reported as |
|-----------|-------------|
| Host unreachable / DNS failure | `Could not reach host <host>: <detail>` |
| Request timed out | `Request to <host> timed out: <detail>` |
| Bad credentials or other HTTP error | `HTTP error occurred: <status> ...` + `Details: <body>` |
| Any other request failure | `An error occurred: <detail>` |

### Security precautions

- Credentials are entered interactively (`getpass`/`input`) at runtime - never hardcoded,
  never written to disk, never in the repo.
- The self-signed lab certificate is accepted (`verify=False`). Acceptable only because
  this is a closed, host-only lab network talking to a system we control.
- The session token is a short-lived bearer credential; the script never logs or persists one.
- A wrong username and a wrong password both return the identical `UNAUTHENTICATED`
  error. This is deliberate vCenter SSO behavior that prevents an attacker from discovering
  valid usernames from the error message alone.

### Testing

- `login`: correct credentials (success), wrong password, wrong username (same error as
  wrong password), a near-zero timeout, and a nonexistent
  hostname. All five produced the expected respective message.
- `list_vms` : success (`200`, `[]`) and a deliberately bad URL path (`404`); proved the
  error handling checks the actual VM-list response, not a stale response from the login step.
- Exit code `1` fires from every failure branch (`raise SystemExit(1)`); `0` on normal
  completion.

### Known limitations

- Every failure calls `raise SystemExit(1)`, ending the whole process. Fine for a
  standalone script; would need to change to `return`/a plain exception if a future
  reuse case wants to skip one failure and keep going (e.g. looping over several vCenters).
- `host` is hardcoded (`vcenter01.rangelab.internal`) — no command-line arguments.

These limitations are tracked for a follow-up revision.
