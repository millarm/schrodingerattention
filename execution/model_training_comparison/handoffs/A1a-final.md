# A1a final adapter/test closure handoff

Status: ready for Sol exact review; this is not authorization for A2 or training.

## Frozen source hashes

- `schrodinger/route_policy.py`: `95cb7463693c7ac696d9034eaf16a155c0363f38e819cbe56c00408d49b170c4` (unchanged)
- `schrodinger/route_policy_data.py`: `676b8de313fb9c667497b307704b21f137ac55a18e1e19c81be399d3f02e4bb7`
- `tests/test_route_policy.py`: `80f4f337ab61442eee330e85cd474cb1f20b19abb9bfbeeba9b2241db9f5b623`
- `tests/test_route_policy_data.py`: `3afcae48e54fd685b48d494baec475cfbd42331a38d9b385c89c8088b7886a3f`

## Literal evidence mapping

- Adapter lines 63–70 retain/validate held-out `Mnovel`, routine zero and mixed
  challenge bounds, free/ranged endpoints and inventory tuple membership; lines
  75, 80–87 enforce homogeneous training families, duplicate states/problems,
  strictly sorted/unique support, and recomputed two-byte-length-prefixed SHA256.
- Adapter lines 93–109 require proposal 14, exact routine `I,L` and mixed `I4L4`
  wrapper sequences, wrapper/row family equality and outcome `OK`; wrong split
  wrappers therefore fail closed.
- `test_actual_saved_adapter_boundary_smoke`, data-test lines 23–35, asserts
  32,946 states, 1,024 train problems, 64 distinct maps (32 I/32 L), 63,517 support
  entries and exact hash; validation maps 12 I +12 L +8 mixed and test maps
  48 I +48 L +32 mixed (alongside total rows 512 and 2,048), with
  384+128 and 1,536+512 routine/mixed compositions, split identity disjointness,
  state sort order, frozen rows and retained/absent `Mnovel`.
- `test_saved_format_fixture_hash_decode_and_negative_boundaries`, lines 59–87,
  uses real loader/hash functions on saved-format bytes and asserts exact
  bytes/current/goal/q decode, stale artifact-hash failure, then manifest-resealed
  malformed state key, inventory pair mismatch, blocked/out-of-range endpoint,
  duplicate state/problem, support-hash, resealed duplicate/unsorted support,
  wrong proposal/wrapper/non-OK stage and invalid novelty failures. Data-test
  lines 13–18 separately prove a valid reversed key decodes
  exactly and an illegal-q swapped form fails.
- `test_matched_shapes_scalars_gradients_and_reload`, model-test lines 14–18,
  asserts legal probability sums, exactly-zero illegal probability, finite
  CE/Brier/KL and illegal-q rejection. Existing shared tensor/scalar/gradient
  and diagnostic-off coverage remains at lines 4–13 and 36–41.
- `test_dt_zero_and_diagnostics_off`, model-test lines 24–32, keeps length-13
  scale 0.1/1/3 dt0 same-tensor unscaled-softmax checks and asserts/prints nonzero
  dt=.11 Hermiticity, unitarity and row maxima.

Raw length-13 maxima from final run: Hermiticity `0.0`; unitarity
`4.76837158203125e-07`; probability-row `4.76837158203125e-07`; dt0 output
`3.5762786865234375e-07`; dt0 probability `1.7881393432617188e-07`.

## Counts and command accounting

The focused command was `.venv/bin/python -m pytest -q -s
tests/test_route_policy.py tests/test_route_policy_data.py`. The final direct-exit
attempt UUID `b2788c7c-58c2-47eb-88dc-e12b48a01426`, at
`2026-09-19T12:25:01Z`, exited 0 in `3.681863459` seconds (`7 passed in 3.58s`).
Its predecessor `ff32c973-938e-4739-9f13-14d9d7cb7c73` is charged once as a
3.756971042-second assertion-fixture failure; the earlier A1a 3.854197667-second
pass is also recorded. All were direct exits; no session was returned or relaunched.

The A1a-00 correction direct-exit UUID `8b819333-2592-411a-97d9-b692c3ea9495`,
at `2026-09-19T12:27:49Z`, exited 0 in `3.640174667` seconds (`7 passed in 3.54s`).
The append-only [stage ledger](../ledger.jsonl) is the reconciled prior ledger plus
all four A1a records. New A1a debit is `14.933206835` seconds; from the specified
starting A `24.720889377` / global `947.724486630`, current totals are A
`39.654096212` and global `962.657693465` seconds of 7,200.

## Completion checklist

- [x] Accepted model file hash preserved.
- [x] Literal saved counts, metadata and disjointness asserted.
- [x] Real saved-format loader/hash positive and negative fixture assertions added.
- [x] Support sorted/unique guard and resealed negative fixtures are present.
- [x] Literal per-family distinct map identities and proposal/non-OK negatives are present.
- [x] Legal/masked proper-loss and length-13 numerical evidence asserted and recorded.
- [x] Focused suite completes in under 20 seconds and every new attempt is charged.
- [ ] Sol exact review required before any A2 or training activity.
