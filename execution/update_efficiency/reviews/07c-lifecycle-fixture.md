# Sol descendant-lifecycle fixture review

**Verdict: PASS for one normal-scope 30-second full-suite attempt.**

Static review only; I did not import project code, execute tests or subprocesses,
load artifacts, or write the ledger.

## Exact inventory

- lifecycle specification `e9443c18b26c96ed8e3a5c466b0257cf1128fcfc31e3112a55bd499d0b162f1c`
- handoff `632ae77021280fe81cc5a48d189c2f4abce18e11cc0c44bb291ee4c38fed0756`
- tests `5fb793d5794836462d0b145cc0d613ef4c0c3b3f29ac28ec1c30cdd75e2378c6`
- unchanged study `a62a37248421660f94edce139a7e9ca471890bab8c0ba4463edd8ffb6c396204`
- unchanged driver `3adda02c82b2eb6a059d890b967950c6718e7406e64dd99fdcfe2dab47f38b4f`
- unchanged watchdog `2b3fed56e07da5a33c122afa10e9cc5b77df0df77ec492db0bfaf4887708a8c8`

## Proof-preserving findings

Only the descendant lifecycle test changes. The unchanged watchdog launches a
real parent in a new session; that parent launches a real same-group child. Both
write fsynced private readiness/identity evidence. The parent installs its TERM
handler before launching and before declaring readiness, and it declares ready
only after observing the child's durable readiness.

The unchanged watchdog receives a two-second total deadline. On real group TERM,
the child takes the default `-15` exit; the parent observes its TERM flag, waits
for and reaps that exact child, durably records PID/return code/reason, and exits
zero. Both processes also have finite defensive lifetimes.

Assertions require distinct real PIDs, parent-as-PGID, child membership and
parent identity, exact reaped child and `-15`, handler-path reason, parent exit
zero, real watchdog timeout and cleanup verification, plus the unchanged
accepted `group_gone` probe after return. There is no mocked signal/probe,
invented cleanup evidence, EPERM-as-success rule, skip, or post-return polling.

This directly removes the prior 50 ms launch/reaping race while preserving the
required descendant-cleanup proof. Review 07b's historical uncertainty remains:
if this one attempt again cannot prove cleanup, execution stops as a capability
blocker with no waiver or further retry.

This PASS authorizes exactly one normal-tool-scope, externally bounded 30-second
full-suite attempt under the existing stage-A launch authority. It does not
authorize production.
