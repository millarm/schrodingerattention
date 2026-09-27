# Independent D0 correction review

**Implementation SHA-256:** `e8e995d511d5454011a02498b15f7a44378c245c17869f2c284c15ccc9d6c94e`  
**Tests SHA-256:** `31ddb075cc553c8039edb0d8ae6fe68c3b581c63c8e9ad8f91658a24222d7d05`  
**Handoff SHA-256:** `877268470bb7a2587d67019bf5432d38aa9cfe70d856b612af882f55130455fa`  
**Correction record SHA-256:** `98a85c8e1f19ddca43230181468f2b79551601acd86cc25ae750b39f9bbbe898`

**Verdict: CHANGES REQUIRED**

The correction materially improves the implementation: the production and test paths now share a real assembly function; raw rows retain full problem identities; exact 512/32×16 panels and complete seed/mode cells are checked; fixed bin keys include empty support; summaries retain seed and mode; challenge K32 cells require 16 exactly paired problem identities; paired outcomes/distributions and strict gate values are emitted; and spec/approval provenance is bound. The following residuals are requirements from `review-00.md` and the frozen spec, not optional extensions.

## Final required corrections

1. **Finish the comparison dimensions in summaries.** Geometry currently retains seed and mode but pools routine and challenge together. Split every geometry axis/bin by stratum → seed → mode, retaining support and nulls. The routine/challenge summaries expose model values but not the required per-seed SA−SM differences; emit those mechanically. Likewise, `paired_k32` exists only for the eight challenge maps. The spec requires K32 both/SM-only/SA-only/neither, gain/loss and per-map `c/32` distributions for every update/seed over the paired validation panel; retain routine-map cells too, while continuing to derive the gate only from challenge cells.

2. **Aggregate the prefix sensitivity and valid-count distributions.** Prefix metrics exist only inside raw problem rows. Add the same equal-map, update/seed/stratum/mode summaries for prefix pass, Q, distinct/K and distinct/M at all six K values, clearly labeled sensitivity. Retain an explicit valid-count (`c`, and where useful distinct `u`) distribution or histogram under all-problem and solved support, rather than forcing later reporting to reconstruct it from millions of raw rows. The existing bag summaries remain primary.

3. **Make exact family integrity literal.** `panel()` accepts any non-`IIIILLLL` family as routine. Require the accepted validation composition: eight `IIIILLLL`, twelve `IIIIIIII`, and twelve `LLLLLLLL` maps, each with 16 problems and internally constant family. A malformed or unknown routine family must be an integrity failure.

4. **Complete the promised integration and safety evidence.** `test_real_retained_event_interface_without_inference_or_test_loader` only loads the eight owner records; it never calls the retained event/route adapter and has no event/result/order mutation negative. Add those literal tests. Add the specified owned CLI seam test proving fixed stage D/name, the 56-second timer, durable terminal/manifest behavior, no success report on failure, and runtime guards preventing model/checkpoint/final-test calls. The composed fixture should assert actual unequal paired outcome counts/distributions, per-seed differences, both strata, fixed empty-bin nulls and the newly aggregated prefixes—not merely that a favorable all-SA challenge fixture passes.

The implementation should remove or stop relying on the obsolete earlier `summaries()` path so tests cannot accidentally validate a function production no longer uses. This is a clarity/regression measure within the existing file, not a new framework.

## Accounting and gate

The additional `4.8s` six-test run is properly charged at stage A; cumulative D0 development remains within 100 seconds. The strict scientific gate itself remains correctly implemented and unchanged. No production run is authorized until one exact final correction closes the residual items above.

No independent tests or compute were run for this static review.
