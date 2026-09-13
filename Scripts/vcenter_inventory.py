"""
Authenticate to the vCenter REST API and report the VMs it manages.

Run directly: prompts for credentials, then prints the VM list.
login() and list_vms() are also written to be called from other scripts.
"""

import getpass

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

host = "vcenter01.rangelab.local"


def main():
    """
    Prompt for vCenter credentials, log in, fetch the list of VMs
    vCenter currently manages, and print it.
    """
    user = input("Enter vCenter username: ")
    password = getpass.getpass("Enter password: ")
    token = login(host, user, password)
    vms = list_vms(host, token)
    print(vms)


def login(host, user, password):
    """
    Authenticate to the vCenter REST API and start a session.

    Returns session token as a string on success. Exits the program on
    authentication failure or if host is unreachable.
    """
    try:
        response = requests.post(
            f"https://{host}/api/session",
            auth=(user, password),
            verify=False,
            timeout=5,
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.Timeout as e:
        print(f"Request to {host} timed out: {e}")
        raise SystemExit(1)  # Exit the program with an error code
    except requests.exceptions.ConnectionError as e:
        print(f"Could not reach host {host}: {e}")
        raise SystemExit(1)
    except requests.exceptions.HTTPError as e:  # Raised by raise_for_status
        print(f"HTTP error occurred: {e}")
        print(f"Details: {response.text}")
        raise SystemExit(1)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        raise SystemExit(1)
    else:
        return response.json()


def list_vms(host, token, timeout=5):
    """
    Fetch the list of VMs vCenter currently manages.

    Returns parsed JSON response as a list of VM dicts. Exits the program on
    authentication failure or if host is unreachable.
    """
    try:
        vm_response = requests.get(
            f"https://{host}/api/vcenter/vm",
            headers={"vmware-api-session-id": token},
            verify=False,
            timeout=timeout,
        )
        vm_response.raise_for_status()
    except requests.exceptions.Timeout as e:
        print(f"Request to {host} timed out: {e}")
        raise SystemExit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"Could not reach host {host}: {e}")
        raise SystemExit(1)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        print(f"Details: {vm_response.text}")
        raise SystemExit(1)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        raise SystemExit(1)
    else:
        return vm_response.json()


if __name__ == "__main__":
    main()
