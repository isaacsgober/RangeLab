# Development Workflow

How work on this repository is done. The lab itself is built from [[Build-Sequence]]; this file
covers the repository and the editing loop around it.

---

## Branches and commits

- One branch per stage group, merged to `main` by pull request once that stage's checks pass:
  `rebuild/plan`, `rebuild/network`, `rebuild/ansible`, `rebuild/vsphere`, `rebuild/verify`.
- Branch created before the stage starts, not after.
- Commit messages are one line, imperative, no body, no attribution trailers.
- Merged branches are deleted locally and on the remote. The pull requests and the merge commits
  in `git log --graph` are the record; stale branch refs are not.
- Pull requests name their Linear issue with `Closes ISA-N`. Linear's GitHub integration moves the
  issue on merge; GitHub's own closing keywords apply only to GitHub issues.
- Nothing is pushed before review.

---

## Where the work happens

The canonical working copy is `~labadmin/RangeLab` on [[ansible01]], because that is the copy
Ansible actually runs. Editing it directly means playbooks are linted and executed exactly as
written, with no transfer step between writing and testing.

Editing is done over SSH from the Windows host with VS Code's Remote-SSH extension: the editor runs
on the host, the files and the integrated terminal are on ansible01. Plain SSH with a terminal
editor works identically; the extension is convenience, not a dependency.

```
Host ansible01
    HostName 10.10.10.20
    User labadmin
    IdentityFile ~/.ssh/id_ed25519
```

Clone with the working branch named explicitly; a plain clone lands on `main`:

```
git clone -b <working-branch> https://github.com/isaacsgober/RangeLab.git ~/RangeLab
```

---

## One working copy at a time

A second checkout on the Windows host is fine for reading and for documentation work, but only one
copy may hold uncommitted changes. Work committed and pushed from one is pulled into the other
before editing resumes there.

Commits are not a transfer mechanism. Moving a file between machines by committing it untested
fills the history with placeholder commits, and the history is part of what this repository is for.

---

## Related

- [[Build-Sequence]]
- [[Rebuild-Plan]]
- [[ansible01]]
