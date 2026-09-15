# vcenter01

## Purpose

To host [[vCenter]]
To provide centralized management of VMware virtual machines/environment

---

## Status

**Running**

---

## Operating System

VMware vCenter Server Appliance
### Version

9.1

---

## Hostname

vcenter01

## Domain

rangelab.local

## FQDN 

vcenter01.rangelab.local

---
## IP Address

[[10.10.10.15]]

---

## Hosted On

[[esxi01]]

---

## Network

[[VMnet10]]

---
## Management

vSphere Client: https://vcenter01.rangelab.local (10.10.10.15)
VAMI: https://vcenter01.rangelab.local:5480

---
## Resources

### vCPU

6 vCPU

### Memory

16 GB

### Storage
#### Datastore
[[datastore01-02]]

---

## Services

VMware [[vCenter]]

---

## Notes

2026-08-04:
	Temporary gateway and DNS settings were used during deployment; lab does not yet contain a router or internal DNS server.

2026-09-15:
	Resized to 6 vCPU and 16 GB. At 2 vCPU the appliance was CPU-starved (15-minute load average 13.46).
	Now manages [[esxi01]].
	The appliance's embedded dnsmasq (`127.0.0.1`) briefly carried hand-edited `host-record` entries and `neg-ttl=10`, a workaround for the add-host failure. They were removed the same day once [[dnsmasqhost]] was fixed. `/etc/dnsmasq.conf` is stock again, and the workaround is kept as `/etc/dnsmasq.conf.workaround-rangelab`. See [[Troubleshooting]] (2026-09-15).
	The 2026-09-14 `DNS=10.10.10.2` / `Domains=rangelab.local` lines in `/etc/systemd/resolved.conf` were also removed (backup `/etc/systemd/resolved.conf.bak-rangelab`). DNS settings now come only from VAMI's network configuration.
	NTP: VAMI timesync mode NTP, server [[ansible01]] (set 2026-09-14, verified synced 2026-09-15). The appliance's `ntp.conf` includes `tinker panic 0`, so ntpd accepts large corrections.
	Starts last in [[esxi01]]'s autostart order and shuts down first, with a 600 s shutdown delay.

---

## Related

- [[esxi01]]
- [[vCenter]]
- [[datastore01-02]]
- [[VMnet10]]