# Naming Convention
## Hosts
Lowercase, no spaces, underscores, or hyphens.  
Form: `<identifier><NN>` 

`<identifier>`: Whatever most clearly distinguishes the host: its OS (`ubuntu01`, `kali01`), platform (`esxi01`, `vyos01`), or role (`dc01`, `vcenter01`).
`<NN>`: Should be two-digit, zero-padded, beginning at `01`.

---
## Networks
Virtual networks will retain the name assigned by hypervisor. (`VMNet10`)

---
## Datastores
Lowercase.  
Form: `datastore<HH>-<NN>`

`<HH>`: The `<NN>` of the host the datastore resides on.  
`<NN>`: Two-digit, zero-padded, beginning at `01`, enumerated per host.

Example: `datastore01-02` is the second datastore on `esxi01`.