# Recovery Procedure — DNS Unavailable

_What to do if the dnsmasq DNS server (dnsmasqhost) goes down or is unreachable._

## Symptoms

- vCenter VAMI errors
- unable to stand up new installs of vCenter
- unable to reach host web interfaces via FQDN URLs

## Immediate workaround
Access hosts by IP address rather than hostname (see [[IP Index]]). This allows administrative access, but does not restore vCenter operation; 
DNS must be functional for vCenter to properly operate; the only solution is to make DNS available again.
## Root cause checklist

- [ ] Is the dnsmasqhost VM powered on?
- [ ] Is the dnsmasq service running? (`systemctl status dnsmasq`)
- [ ] Is the network path (VMnet10) intact?
- [ ] Any recent config changes to `/etc/dnsmasq.conf`?

## Fix and verify

1. **Confirm reachability.** From another host: `ping 10.10.10.2`
    - No reply:
	    - the VM is down or the network path is broken. Check power state in Workstation and confirm VMnet10 is intact. Access the console directly if SSH is unavailable.
    - Reply:
	    - the host is up; continue.
2. **Check the service.** On dnsmasqhost: `systemctl status dnsmasq`
    - Running:
	    - skip to step 4.
    - Failed or stopped: 
	    - continue.
3. **Diagnose the failure.** Read the error in the status output or `journalctl -u dnsmasq`.
    - `unknown interface <name>` :
	    - the interface wasn't up when dnsmasq started. Confirm with `ip addr show ens160`. See Troubleshooting 2026-09-05.
    - Config errors :
	    - check and make necessary updates to `/etc/dnsmasq.conf` via 
	     `sudo nano /etc/dnsmasq.conf` (or `vi`)
    
4. **Restart dnsmasq:** `sudo systemctl restart dnsmasq`
5. **Verify resolution.** 
	From another host:
	```cmd
		nslookup vcenter01.rangelab.local 10.10.10.2
		nslookup 10.10.10.15 10.10.10.2
	```
	Both must succeed — vCenter depends on forward _and_ reverse.
	
6. **Check vCenter.** VAMI at `https://10.10.10.15:5480` and the vSphere Client at `https://10.10.10.15`. Services may recover unaided; allow several minutes before restarting anything.