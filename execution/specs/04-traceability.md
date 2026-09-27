# Block4 traceability-only correction

Sol independently matched all statistical conclusions, interpretation, and
figure. After formal review, Terra may edit summarize.py and summary outputs/
handoff only; no raw data or training change.

1. For each run, combine every validation checkpoint's recorded normal invariants
   with every normal final-condition invariants. Emit explicit run-wide H/U/row
   maxima and overall exact-model maxima, keeping final-only values separately
   labelled if retained. Expected audited overall values: H0,
   U=row1.1920928955078125e-6. These must be computed from inputs, not constants.
2. Add input SHA256s for all three equal-time JSONs embedded in summary, the
   corrected03-run-provenance.md and03-comparison.md audit, plus source/config/
   contract identities used. Inputhash inventory must cover all consumed evidence.

Regenerate summary JSON/CSV/MD/PNG, update current output/source hashes and exact
command in handoff. Verify calculated maxima and input hashes. <=15s compute,
no retraining. Sol reviews only corrections while retaining prior statistic/
figure checks. Do not leave either item partially implemented.
