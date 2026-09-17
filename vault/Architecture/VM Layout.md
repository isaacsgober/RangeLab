

> **Pre-rebuild content.** Describes the lab as built before 2026-09-16, including the
> `rangelab.local` domain. Rewritten when Stage 4 of [[Build-Sequence]] rebuilds it.

```mermaid
graph TD
    Host["Precision7730 (Host)"]

    Host -.-> VMNet["VMnet10"]
    Host --> ESXi["esxi01"]
    Host --> DNS["dnsmasqhost"]

    ESXi -.-> VMNet
    DNS -.-> VMNet

    ESXi --> VC["vcenter01"]
    ESXi --> ANS["ansible01"]
    ESXi --> MAN["managed01"]
    VC -.-> VMNet
    ANS -.-> VMNet
    MAN -.-> VMNet

```
