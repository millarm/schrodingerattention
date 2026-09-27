# A3 profile 001 independent runtime audit

**Verdict: PASS.**

Reviewed immutable production artifacts:

- profile result `e2073da106b4ad32e0dd5f9ded915dbd7ee60fe737a24e6d87abb7ada2f0bafb`
- profile output manifest `af6c7b796b1c6723dcd531a97b827075a0bfd61613378dc30267c653b48db635`
- profile attempt `70b79da90183d56824254b0a975dc265cfdba00089781e7e1141f6e1bf18df46`
- prepared artifact `10e5f96a98b4dcb944cf81b65eb43eb4ed5a8c8211bf9d1f55af2f0bc4814e49`
- profile decision `8cb2e46771f5c0f04a590cb31e6d97d0e53611408dca086936170f6e6b71a007`
- reviewed derived forecast `1a18425b010721afe8444156e36567a815b5193f725c23fbade3111714879823`

The output manifests were independently checked against every retained file's
SHA256 and byte count with no mismatch.  The profile is bound to accepted runner
source `10cfc1a9...`, the frozen plan/config, prepared artifact, pool manifest and
complete input/source/governing inventories.  The command, executable, runtime,
thread settings and RSS are recorded.  Prepare session 34159 and profile session
12385 were each launched once and reached explicit exit 0; both canonical attempt
records are COMPLETE and the lock is absent.  Profiling weights are seed 1699
only and no test-model inference occurred.

The retained profile establishes both 70,540-parameter models, fixed order
softmax then Schrodinger, five warmups plus twenty measured updates/model, six
maps/96 validation problems, 64 training and 128 validation probe states, all
five evaluation/control operations, checkpoints, traces and direct finalization
timing.  Exclusive phases total `12.901783541892655` seconds within end-to-end
`12.907836832979228`.  Numerical maxima are Hermiticity `0`, unitarity
`4.76837158203125e-7`, and probability-row error
`3.5762786865234375e-7`, all safely below the frozen runtime abort thresholds.

The original automated bound `3231.807160494587` seconds is preserved.  Its
conditional candidate component `2553.8047955953516` charges each of 77 future
decoding candidates as a complete five-operation endpoint and is therefore a
known conservative unit mismatch, not an omitted-work estimate.

The reviewed prospective bound corrects only that resource unit.  It uses the
maximum observed T1 K32 rate `0.013818565124893212` seconds/problem plus maximum
proper-bank rate `0.00018377734340901952` seconds/problem across both models and
all families.  Every one of the same 77 candidates is charged for both operations
over all 512 physical validation problems with the unchanged 1.5 factor and no
cache discount:

`1.5 * (0.013818565124893212 + 0.00018377734340901952) * 512 * 77`

`= 828.0425242055207` seconds.

All other costs remain `678.0023648992355` seconds, including training,
384/128 validation work for both models and seven scheduled/equal-time endpoints,
22 checkpoint writes, complete SA probes, traces, serialization, setup, ledger,
120-second audit and 30-second finalization reserves.  The independently
recomputed total is therefore `1506.0448891047563` seconds, matching the derived
artifact exactly and remaining below B2000.  Candidate counts still include both
quality searches, both fixed curves, softmax entropy matching and SA dt0 T1 plus
quality rematching; no scientific work, seed, K, threshold or endpoint is removed.

The ledger was independently recomputed before this review entry: 68 unique IDs,
A `410.4018179169711` and global `1333.405415169971` seconds.  The read-only hash,
ledger and arithmetic audit consumed `1.0` second and was appended once as UUID
`FC1F6A44-4506-448A-8C4A-5AD7C748B8D8`, giving A
`411.4018179169711`, global `1334.405415169971`, and remaining A/global
`288.5981820830289 / 5865.594584830029` seconds.

The derived `1506.0448891047563`-second forecast is accepted as the prospective
resource gate for the unchanged seed1701 pair to 1,000 updates, in order softmax
then Schrodinger, under B2000.  Launch still requires the exact decision record
binding both fresh commands; later continuation, seeds1702–1705, main, operating-
point and test gates remain conditional and unauthorized by this review.
