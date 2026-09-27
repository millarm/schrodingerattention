# Sol clarification — driver correction semantics

**Status: consistent with `03-driver-closure.md`; no verdict change.**

Static clarification only. No implementation, imports, tests, subprocesses or
ledger operations were performed.

Two correction details are confirmed:

1. **Owner UUID discovery.** `OwnedAttempt` creates its entry UUID at begin, so
   the driver must not invent or require a pre-supplied owner UUID. Before launch,
   it binds the exact seed/mode/16000 output path and proves that owner output,
   terminal and prior fallback are absent. After launch/cleanup it resolves the
   actual UUID from durable `attempt.pending.json` and/or `attempt.json`, checks
   their mutual identity when both exist, and reconciles that UUID plus exact
   output/stage to one unique normal owner ledger row. A matching durable FAILED
   owner row is the accounted failure and receives no fallback. Only genuine
   absence of the resolved owner's charge permits one permanent, distinctly
   typed uncertain fallback; that fallback can never satisfy later owner-charge
   reconciliation or be promoted to success.

2. **No accounting clamp.** Reservation and a remaining-time deadline should
   prevent ordinary overrun, but recorded evidence must remain honest. Charge
   actual elapsed accountable time plus any explicit conservative
   finalization/uncertainty allowance; never clamp actual usage down to the
   reserved envelope. If the resulting charge exceeds an owner envelope or cap,
   retain the full charge and terminal evidence, mark the run/resource condition
   failed, and prohibit continuation or retry. The allowance must be included
   arithmetically in `charged_seconds`, not merely named in metadata.

These are narrow interpretations of findings 1–4 and do not weaken any other
required correction or literal branch-test requirement. The historical
`CHANGES REQUIRED` review remains controlling until a new exact version closes
all findings.

