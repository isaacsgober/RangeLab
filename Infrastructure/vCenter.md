
# vCenter

## Purpose

To provide centralized management of ESXi hosts and virtual infrastructure; it is the management plane.

---

## Host

[[vcenter01]]

---
## Ports

- 443/TCP — HTTPS; vSphere Client, vCenter Server API, and other vCenter services
- 80/TCP — HTTP; redirects to HTTPS
- 5480/TCP — HTTPS; vCenter Server Appliance Management Interface (VAMI)

---

## Configuration

- Deployment Type: VMware vCenter Server Appliance (VCSA) 
- Deployment Size: Tiny 
- Version: 9.1
---

## Dependencies

- [[esxi01]] 
- [[VMnet10]] 
- [[datastore01-02]] 
- [[dnsmasq]]
- NTP *(recommended)* ([[TO BE UPDATED]])

---
## Notes

The VMware vCenter Server Appliance (VCSA) is a preconfigured virtual appliance that contains vCenter and all of the software required to run vCenter.

---

## Related

- [[vcenter01]] 
- [[esxi01]] 
- [[ESXi]] 
- [[vSphere]] 
- [[VMnet10]] 
- [[datastore01-02]]