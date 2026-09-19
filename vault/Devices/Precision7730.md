# Precision7730

## Purpose

Physical host of all Range Lab virtual devices

---

## Status

**Running**

---

## Operating System
Windows 11 Pro for Workstations
### Version
26H1

---

## Hostname
P7730
## Domain
None; the host has no record in the lab zone
## FQDN
N/A

---

## Hosted On
N/A

---

## Network

VMnet10 host adapter:

IPv4: [[10.10.10.1]]
Mask: 255.255.255.0
Gateway: none, by design; host routing is unaffected by the lab
DNS: [[10.10.10.2]] ([[infra01]])

The adapter's DNS server is what lets the host resolve lab FQDNs, which ADR-0008 relies on for SSH,
the vSphere Client, and the Host Client from Windows. Lab names resolve only once infra01 serves DNS
(Stage 3).

---

## Management

Web Interface:

---

## Resources

### CPU

### Memory

---

## Storage

-

---

## Datastores

-

---

## Hosted Virtual Machines

-

---

## Notes

2026-09-15:
	The lab's time source. Windows Time is set to Automatic, syncs from `time.windows.com`, and serves NTP to [[VMnet10]]. See [[chrony]] and [ADR-0004](../Architecture/Decision%20Records/ADR-0004%20-%20Lab%20time%20source.md).
	Registry (`HKLM\SYSTEM\CurrentControlSet\Services\W32Time`): `TimeProviders\NtpServer\Enabled = 1`, `Config\AnnounceFlags = 5`, `Config\MinPollInterval = 6`, `Config\MaxPollInterval = 10`. `LocalClockDispersion` was also set to 0; it has no effect while Windows syncs from an upstream.
	Windows Firewall rule "NTP server (RangeLab VMnet10)": inbound UDP 123 from `10.10.10.0/24`.
	Accuracy: about 1 s fast of real time, checked against time.google.com and time.cloudflare.com.

---

## Related

-

Member of [[VMnet10]]:
IP: [[10.10.10.1]]
