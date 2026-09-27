# Bounded respecification after two Recovery A correction cycles

Sol07 verifies the intended source behavior but identifies one missing returned-
evidence assertion. Cause: prior test checked dispatch calls, while handoff prose
incorrectly claimed it checked the returned family record. No source/scientific
change is needed. Terra changes only the existing short-circuit test and writes
a literal assertion-location handoff; Sol inspects only this closure plus hashes.

For the parameter case training outcome OK and held-out outcome
SCIENTIFIC_HELDOUT_SUPPLY_FAILED, inspect out["evidence"][0]["stages"]. Assert
validation_routine has exactly two rows: first family IIIIIIII and result outcome
SCIENTIFIC_HELDOUT_SUPPLY_FAILED; second family LLLLLLLL and result exactly
{"outcome":"NOT_EVALUATED"}. Assert validation_mixed/test_routine/test_mixed
each has outcome NOT_EVALUATED, and calls equals ["IIIIIIII"] exactly.
These assertions must execute in that concrete parameter case, not dead code.

One focused pytest command<=60s, full result, unique EOF charge. Handoff02d
names exact assertion line locations/source/test hashes. Source must remain
4aa4779877781f2b0211397c3938185ad6ec5154040fecdef3d9f7eac7e84f08.
No fixture work, runner, extra tests or feature changes in this respecification.
If this single literal closure still fails, report that concrete blocker rather
than renewing the same open-ended correction request. Existing caps unchanged.
