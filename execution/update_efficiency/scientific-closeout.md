# Two-pair update-count pilot: interpretation

2026-09-27. Astra interpretation. Exact independent review and acceptance are
recorded separately in `closeout-acceptance.md` when the closeout gate is met.
The cleanup repair passed review and tests; both frozen pairs completed all
16000 updates and13 scoring points. This report addresses update counts, not
wall-clock or computational superiority.

## Answer

8000 updates was too early to describe these runs as saturated: every owner
improved validation route quality Q between8000 and16000. However,16000 also
did not demonstrate the prespecified sustained Q or sampled training-CE plateau
for any owner. The plateau times remain right-censored, not observed at16000.

There is no stable update-saving factor across the primary common-quality
milestones. Under the prespecified one-percentage-point tolerance, Schrödinger
reached the nominal30% and38.198% milestones earlier in one seed and later in
the other. At the exact38.198% threshold it reached the milestone2000 updates
earlier in both seeds. This sensitivity matters; the exact threshold is a
reported sensitivity check, not a replacement for the primary tolerated result.

## Common-quality update counts

An entry gives acquisition update, with confirmation in parentheses. Acquisition
requires two consecutive scoring points above threshold; grid intervals and
conservative ratio bounds are in `runtime-evidence-006-two-pair-scientific-transcription.md`.
All listed acquisitions were confirmed, with no initial-pass anomalies.

| Q threshold | Seed | Softmax | Schrödinger | Schrödinger minus softmax |
| --- | ---: | ---: | ---: | ---: |
|29% (nominal30%, tolerated)|2201|2000 (2400)|3600 (4000)|+1600|
|29% (nominal30%, tolerated)|2202|3600 (4000)|2000 (2400)|−1600|
|37.198% (nominal38.198%, tolerated)|2201|6000 (8000)|8000 (10000)|+2000|
|37.198% (nominal38.198%, tolerated)|2202|12000 (14000)|10000 (12000)|−2000|
|30% exact|2201|2000 (2400)|3600 (4000)|+1600|
|30% exact|2202|3600 (4000)|3600 (4000)|0|
|38.198% exact|2201|10000 (12000)|8000 (10000)|−2000|
|38.198% exact|2202|12000 (14000)|10000 (12000)|−2000|

At exact38.198%, the grid ratios SA/SM are0.80 and0.8333:20% and16.7% fewer
updates at the observed acquisition points. Coarse grid bounds still reach1.0
for both seeds, so these counts do not establish a precise continuous crossing
ratio or full-policy equivalence. Opposite primary paired differences must not
be hidden behind their zero mean. No threshold was selected after results.

Acquisition diagnostics also matter:2202 softmax's12000-update acquisition of
both exact and tolerated38.198% has KL0.4147427nat, exceeding the prespecified
0.40nat fragility threshold. This flag qualifies the comparison; it does not
change the crossing threshold or erase that owner's acquisition. The explicit
acquisition Q/KL/Brier/challenge values and flags are in the transcription.

## Progress after8000 and the absence of a sustained plateau

| Seed / mode | Q8000 | Q16000 | Q gain, percentage points | Final Q gain-window G, percentage points | Final CE relative improvement |
| --- | ---: | ---: | ---: | ---: | ---: |
|2201 softmax|38.1608%|39.8551%|+1.6943|+0.6879|1.4894%|
|2201 Schrödinger|39.4889%|40.9001%|+1.4111|−0.1948|1.9015%|
|2202 softmax|36.5495%|38.8981%|+2.3486|+2.5618|2.1720%|
|2202 Schrödinger|36.8880%|41.5234%|+4.6354|+2.9188|2.1369%|

Mean Q gains8000→16000 were+2.0215pp softmax and+3.0233pp Schrödinger. The
required final-two-window Q low-gain rule was not met: only2201 Schrödinger's
last window qualifies, and it is a negative gain (stagnation/deterioration),
preceded by a1.2061pp gain window. Every final CE window still improved by
more than the0.5% low-gain threshold, and none had a qualifying earlier CE
window. No temporary confirmed plateau or sustained plateau was observed.
These are operational finite-horizon diagnostics, not proof of global learning
completion or a prediction of the eventual plateau update.

## Early divergence and quality tradeoffs

The requested15/30/45/60/75% points remain1200/2400/3600/4800/6000 updates,
fractions of the original8000 reference. All raw grid values are retained in
the transcription, including per-seed/equal-seed paired differences at all13
points. The requested early differences are:

| Reference fraction / updates | SA−SM Q,2201 (pp) | SA−SM Q,2202 (pp) | Mean (pp) |
| --- | ---: | ---: | ---: |
|15% /1200|+2.6497|+0.4264|+1.5381|
|30% /2400|−2.1973|+1.7383|−0.2295|
|45% /3600|+0.9391|+2.6188|+1.7790|
|60% /4800|+2.1224|−0.1839|+0.9692|
|75% /6000|−1.5576|−1.3623|−1.4600|

At4800 the positive mean Q gap is mixed: mean validation KL is worse for
Schrödinger by0.0340604nat, above the fixed0.02nat conflict margin. Mean gaps
also cross zero across early stages; one update-saving factor would hide this.

The fixed curvature contrast
`C = ΔQ(3600) − [ΔQ(1200)+ΔQ(6000)]/2`, in percentage points, is+0.3931 for
2201 and+3.0868 for2202, mean+1.7399pp. Both signs are positive and the mean
exceeds the prespecified1pp descriptive screen; the per-seed range is
[+0.3931,+3.0868]pp. The large difference between
seeds matters: this is evidence of nonconstant early paired curves in this
pilot, not statistical confirmation or a general training-law claim.

At16000, mean Q is39.3766% softmax versus41.2118% Schrödinger, a+1.8351pp gap.
The corresponding mean validation KL is worse for Schrödinger by0.020861nat,
exceeding the fixed0.02nat conflict margin. The final Q advantage is therefore
**mixed under the prespecified rule**. Mean validation KL also worsened from
8000 to16000 for both models (+0.04917nat softmax,+0.07769nat Schrödinger).
Continued sampled-training improvement and route-quality gains do not imply
better complete policies or better calibrated held-out distributions.

## Scope and resources

This is the frozen two-fresh-seed exploratory pilot, with shared initialization
and all16000 minibatch digests matched within each pair. Reused validation maps
limit generalization. Checkpoints/maps/rollouts are not independent training
replications; no p-value or population-level sample-efficiency conclusion follows.
More seeds or a longer horizon would require a new scientific/resource amendment.
Stop here; unused budget is not continuation authority.

Operational evidence and exact source/owner/ledger identities are in runtime
records003–006 and the independent review. All four owners completed, cleanup
was verified and reservations released. Production used1066.3934205418918/1800s;
new-study development used24.343377124750988/100s. Qualified global debit is
5855.153244667692/7200s, retaining the historical administrative uncertainty.
The current ledger EOF is
`ddfe5b2df043d940b1dcbf30ed367483abac1a5935863d123a1e9c6267229da2`.
