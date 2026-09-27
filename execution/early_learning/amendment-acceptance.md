# Amendment methodology acceptance

2026-09-27. Astra accepts Sol's PASS in reviews/02-amendment-methodology.md for
the exact documents and hashes named there. This authorizes the bounded Luna
implementation corrections and added arithmetic in spec-02-corrections-and-kl.md.
No runtime, training, 200k continuation or final-test access is authorized by
this acceptance. The fresh 1,800-second ceiling is unchanged and unspent.

The review's numerical clarification is binding: if exported p is zero on any
positive-q action, mark that checkpoint's conditional decomposition unavailable,
even if its total oracle-support mass is positive. Retain the original saved
KL and state identities; do not omit states or run extra inference. Add this
case to the analytic tests. Compare weighted 1−m against saved nonoptimal mass
as an independent validation, since defining B=KL+log(m) makes A+B closure
algebraic. No arbitrary small-positive-m cutoff is introduced: evaluate the
finite positive mass as written and report actual nonfinite/log failures.

Resolve the seven exact implementation findings in reviews/01-static.md and
freeze one corrected version for independent review. The already planned
10-second smoke and 60-second tiny suite remain the only next runtime checks,
after static PASS and Astra acceptance. Production still requires exact Sol
implementation PASS and a separate Astra acceptance artifact. Preserve all
earlier documents and the 200k hold.
