# Independent review — bounded baseline diagnosis specification

## Verdict: PASS

Reviewed specification SHA-256: `cea244fa4653eaf8274e1a923abd2b469284cd15fac254b48099a44a367fad55`.

The diagnosis is scientifically bounded and answers a useful narrow question: whether the weak held-out route performance coexists with fit on seen shortest-path DAG states, and how much of the observed gap is associated with held-out routine maps, broader state eligibility, and mixed-composition maps. It does not treat these observational contrasts as causal attribution.

Acceptance conditions for implementation and interpretation:

- The training and DAG-aligned validation fixed banks must use the same deterministic 32-state-per-map selection and equal-map weighting. Routine and challenge validation strata must remain separately reported; candidate pooling must not let maps with larger DAGs receive greater weight.
- The stored broad-bank comparator must be taken from the matching immutable checkpoint event (0, 1,000, 4,000, or 8,000) and labeled as a different eligibility distribution, not silently combined with either new bank.
- The update-8,000 training rollout summary must remain a training-only routine result over all 1,024 saved problems. It must not be presented as held-out performance, novelty, an 80/20 mixture, or an independent replication.
- Checkpoint validation must bind the actual checkpoint byte hash, declared update/mode/seed, original initial identity, frozen source/prepared/data identities, and owner manifest before any inference. Any mismatch, timeout, nonfinite score, malformed q, or output/ledger failure is a technical failure, not a scientific diagnosis.
- The output must preserve denominators and raw/per-map records so CE, KL, Brier, nonoptimal mass, state-property distributions, and rollout rates remain independently recomputable.

The literal open-grid fixture is correct: for row-major 12×12 indexing, start 0 and goal 25 have nonterminal shortest-DAG cells `{0,1,12,13,24}`, with start action probabilities east `1/3` and south `2/3` in N/E/S/W order. The duplicate, goal-exclusion, legality, normalization, deterministic-selection, and checkpoint-substitution tests are sufficient for this small additive implementation.

The 120-second ceiling and its 15/74/15/16 allocation are internally consistent with the inherited global debit. No training, test-set access, threshold change, or modification of completed study artifacts is authorized by this PASS.

Static review only; no compute or ledger charge.
