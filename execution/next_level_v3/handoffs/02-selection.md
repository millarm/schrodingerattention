# V3 Block 2 — pure support and lazy-selection handoff

Implemented solely in `schrodinger/productive_diversity_v3_data.py` with its
new test additions. `ProposalOracleCache` bounds pair/signature state per
proposal; `build_training_support` performs frozen family/map prefix selection,
route multiplicity verification, normalized shortest-DAG q construction, and
complete canonical nonempty suffix support hashing. `lazy_select_heldout` uses
the frozen split/family stream and shortlist order, rejects a map on a failed
length, and commits identity only after every length passes. It retains n,
family, canonical identity, map ID, endpoints, length, M and evaluation
Mnovel on rows; technical oracle/count defects raise `SelectionTechnicalError`.

The real bounded fixture contains valid eight-component n=12 I8, L8 and mixed
maps (components remain outside the selected lower-right path region), uses
actual inventory/enumeration/verification, and reduces only internal selected
map/length quotas to one per family and length. It proves a genuine routine
held-out success from complete training support and invokes the real partial
novel challenge predicate. It is not a production feasibility claim.

Focused command:

```
.venv/bin/python -m pytest -q tests/test_productive_diversity_v3_data.py
```

Final exit 0: `9 passed in 1.06s`; full wall 1.140695875s (ledger
`2b69a917-aae1-4116-8840-fe638b7c8450`). The preceding core regression run is
also preserved at 0.922747083s. No pool generation, runner, production data, or
model code ran.

- Module SHA-256: `922876c57e651457f97f0d702c0ac4646d326d14d84d0e87852c4a92119a3e17`
- Test SHA-256: `1979e6a72fb89c2882605b8aca2b093f303a0bf5b15aaa938c67c92800cc69ee`

Final focused verification also asserts that training is homogeneous-only (I8/L8,
not mixed), that an actual distance-one predecessor is present in the saved q
state map, and that the ranked first-proposal callback fires exactly once.
