"""
Check DNS resolution and TCP port reachability for a list of hosts.

Usage: python healthcheck.py hosts [hosts ...] [-p PORT] [-t TIMEOUT]
"""

import argparse
import shutil
import socket
import sys

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
GRAY = "\033[90m"
RESET = "\033[0m"


def check_host(host, port, timeout):
    """
    Resolve host, then attempt TCP connection to the specified port.

    Returns (ok, message), where `ok` is a bool True if the connection
    was successful, False otherwise, and `message` is a string describing
    the result, preformatted, ready to print, with ANSI color codes.
    """
    try:
        ip = socket.gethostbyname(host)
        conn = socket.create_connection((ip, port), timeout=timeout)
        conn.close()
        return (
            True,
            f"{GREEN}{host} | {ip} | Port {port} is open{RESET}",
        )
    # Exceptions are ordered from specific to general, as
    # they are all OSError subclasses
    # This ensures that the most specific error message is returned.
    except ConnectionRefusedError:
        return (
            False,
            f"{YELLOW}{host} | {ip} | Port {port} is closed (connection refused){RESET}",
        )
    except TimeoutError:
        return (
            False,
            f"{YELLOW}{host} | {ip} | Port {port} is closed (timeout){RESET}",
        )
    except socket.gaierror:
        return (False, f"{RED}{host} | could not be resolved{RESET}")
    except OSError as e:
        return (False, f"{RED}{host} | {ip} | OS error: {e}{RESET}")


def main():
    """
    Parse CLI arguments, check each host, print results,
    exit with code 1 if any host failed.
    """
    parser = argparse.ArgumentParser(
        description="Check DNS resolution "
        "and TCP port reachability for a list of hosts."
    )
    parser.add_argument(
        "hosts", nargs="+", help="Hostname(s) or IP address(es) to check."
    )
    parser.add_argument(
        "-p", "--port", type=int, default=22, help="TCP port to check (default: 22)."
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=3.0,
        help="Timeout in seconds for each connection attempt (default: 3.0).",
    )
    args = parser.parse_args()

    width = shutil.get_terminal_size(fallback=(100, 24)).columns
    divider_row = GRAY + "-" * width + RESET
    double_divider_row = GRAY + "=" * width + RESET

    print(double_divider_row + CYAN + "\nCHECK CONNECTIVITY:\n" + RESET + divider_row)
    failed = False
    n_passed = 0
    n_failed = 0
    for host in args.hosts:
        ok, message = check_host(host, args.port, args.timeout)
        print(message)
        if ok:
            n_passed = n_passed + 1
        if not ok:
            n_failed = n_failed + 1
            failed = True
    if n_passed != 1:
        word_pass = "passes"
    else:
        word_pass = "pass"
    if n_failed != 1:
        word_fail = "fails"
    else:
        word_fail = "fail"

    print(
        divider_row
        + CYAN
        + f"\nCONNECTIVITY CHECK COMPLETE: {GREEN}{n_passed} {word_pass}{RESET}, "
        f"{RED}{n_failed} {word_fail}{RESET}\n" + RESET + double_divider_row
    )

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
