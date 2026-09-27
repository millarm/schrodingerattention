# Terra static handoff — Block A wrapper

Implementation version (no imports, tests, model/data execution, or ledger
writes have been performed):

- `study.py`: `79d3114ee643dabb509b06037b86e1a743dc2ebaba5c3a1019b74302d3a4e5ba`
- `command.py`: `30574d71554ab10ab75b29dba01f41a4b7dca7274a15e292aa74651291495df0`
- `tests/test_update_efficiency.py`: `c3c44bd18fe2e1921ddd9e88df2a21580c662472439948462634a22b99fd6c34`
- plan/spec/decision: `d1e1443d0dffe1fbf0f90a120c8acbc03dd5555167f65b20e01a16c0d9f1bae5`,
  `9830d0ac638e9bd4b088589098bbe4a75054739775e0c8d00cb4ff82d7141acd`,
  `c97556f38de6f443cfdfb28486839599d11b65801cd1cdabe5e7375066c2f034`.

Implemented seam: COMPLETE prepare-owner metadata supplies the six input IDs;
the retained COMPLETE validation owner supplies only update-zero proper row
order/q evidence. The wrapper verifies those hashes, rebuilds only validation,
uses the unchanged loader/trainer/sampler/checkpoint/evaluators, scores the
fixed grid after training, records target flags and raw endpoint artifacts, and
implements sustained acquisition, censoring, grid-ratio and conservative
interval summaries. Resource stages are scoped and restored in `finally`.

Test mapping: pure target inclusivity/guards/nonfinite/stability/censoring/grid
and all-four ordering are in the first five tests. The next test composes actual
accepted two-update training, checkpoint restoration, both modes, evaluator,
serializer, owner finalization and one endpoint write; the last test covers a
timeout child cleanup surface.

The driver now delegates process-group/reap to the previously reviewed watchdog
helper and records an A-stage EOF charge on both failed and successful test
children. Static review must still determine whether its retained-helper import
and B fallback reconciliation meet the new study's exact authority contract.
This remains a static checkpoint, **not** a claim of implementation PASS or
authorization to execute tests/production.
