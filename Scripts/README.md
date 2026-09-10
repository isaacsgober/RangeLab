# RangeLab Scripts

Helper scripts for the lab. Standard-library Python only — nothing to install to run them.

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
python healthcheck.py ansible01.rangelab.local managed01.rangelab.local

# vCenter web UI, one-second timeout
python healthcheck.py vcenter01.rangelab.local -p 443 -t 1
```

### Sample output

Checking port 443 (management web UI) across three hosts:

```
==================================================================
CHECK CONNECTIVITY:
------------------------------------------------------------------
vcenter01.rangelab.local | 10.10.10.15 | Port 443 is open
ansible01.rangelab.local | 10.10.10.20 | Port 443 is closed (timeout)
bogus.rangelab.local | could not be resolved
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
