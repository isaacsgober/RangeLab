# VM Layout

Where each node runs and which networks it attaches to. Solid arrows mean "runs on"; dashed lines
are network attachments. Addresses are in [[IP Index]]; sizing is in each device note.

```mermaid
graph TD
    Host["Precision7730 (host)"]
    VMnet8["VMnet8 (NAT)"]
    VMnet10["VMnet10 (lab)"]

    Host --> VYOS["vyos01"]
    Host --> INFRA["infra01"]
    Host --> ANS["ansible01"]
    Host --> ESXI["esxi01"]
    ESXI --> VC["vcenter01"]
    ESXI --> MAN["managed01"]

    VYOS -.-> VMnet8
    VYOS -.-> VMnet10
    INFRA -.-> VMnet10
    ANS -.-> VMnet10
    ESXI -.-> VMnet10
    VC -.-> VMnet10
    MAN -.-> VMnet10
```

vyos01, infra01, and ansible01 run directly in Workstation so the lab's gateway, DNS, time, and
Ansible control node do not depend on esxi01 (ADR-0006). vcenter01 and managed01 reach VMnet10
through esxi01's [[VM Network]] port group.

---

## Related

- [[IP Index]]
- [[VMnet10]]
- [[VMnet8]]
- [[VM Network]]
- [[Rebuild-Plan]]
