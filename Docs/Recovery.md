# Recovery Procedure — DNS Unavailable

_What to do if the dnsmasq DNS server (dnsmasqhost) goes down or is unreachable._

## Symptoms

-

## Immediate workaround

- (e.g., temporary static `/etc/hosts` entries on affected systems)

## Root cause checklist

- [ ] Is the dnsmasqhost VM powered on?
- [ ] Is the dnsmasq service running? (`systemctl status dnsmasq`)
- [ ] Is the network path (VMnet10) intact?
- [ ] Any recent config changes to `/etc/dnsmasq.conf`?

## Fix and verify

1.
2.
3. Confirm forward + reverse lookups succeed again.
