# Independent training-wrapper review

**Accepted plan SHA-256:** `b58b88ae15712bca2b027ccb1ab3fc90bef4e9b2a5d94dc8dba43d61fbcb679e`

**Verdict: CHANGES REQUIRED (exact-version provenance only)**

The requested exact-version gate cannot pass because the frozen hashes supplied in the handoff do not match the files visible during review:

| Artifact | Supplied SHA-256 | Observed SHA-256 |
|---|---|---|
| `execution/seed_replication/train.py` | `9d7f757f700ce6cd9df81f94026b1bb6d1b0017ac0b74c707ae02d10d2e933b7` | `15e67019ac27ef24d2a138e09209db0360270b157f56f99bb3ba652729f7cd5b` |
| `tests/test_seed_replication_train.py` | not supplied in the review request | `22028b20347aaa1ee7099ca95d736fee6f1b8416ea2a4b327dd6d1397a25b362` |

Freeze the intended files and issue one exact handoff containing the current wrapper hash, test hash, commands hash, all eight decision hashes, test command/result/count, and charged failed/successful test records. No training may launch from an unreviewed byte version.

## Static assessment of the observed wrapper

No scientific or authorization defect was found in the observed bytes. They:

- fail closed outside seeds 1702–1705, modes softmax/Schrödinger, and 8000 updates;
- validate the plan, accepted config, prepared data, manifest, resource table, seed and mode through each immutable decision;
- prove the original stage/global/carry contract before installing the approved resource-only table;
- call the accepted paired-model, optimizer, sampler, scheduled-training, probes and owner seams with seed-specific shared initialization, no resume, and unchanged frozen scientific configuration;
- persist the wrapper hash/argv, decision hash, input identities, resource-table hash, shared-initial digest and accepted runtime provenance;
- require the durable owned attempt to finish `COMPLETE` before printing success.

The eight commands implement the frozen alternating order and use distinct owner names and decisions. The observed decision hashes are:

- 1702 softmax `f4210f6e5618294bd830fb26ffdaf0c48219e156e93e9a5bd9690795436b7463`
- 1702 Schrödinger `632cadbca8dd173e2d4fd4b039528d2f11ad78f72e14572f617e1bc4e6d57c5d`
- 1703 Schrödinger `34346a063ba07f9fdd0a7a8824c54bf7a72dd76fa77a72f3e70584e2a9f5fc20`
- 1703 softmax `bdf5b54c4cb6b1c69f98513798d582d8c964f045c3273e8e5e64c7d0dbe2ca5e`
- 1704 softmax `7c5239fb03b88947b81469c4aa55eb94ce1d14a550a93ac603d4841a2bbc8955`
- 1704 Schrödinger `4388420025393090978bae2ba7d110fc3169b17cee6d8cf6d5539c554c96fb51`
- 1705 Schrödinger `4add136f6ab35e3d005d60f376077aad4ef7ed011f5895ec6c53a789cf5a80fc`
- 1705 softmax `4e284daeb04d7c8a593701e3d9bccd7fdc4607181ab909bff9b5dd9ff81ae310`

Once the exact-version record is corrected, only a hash/record closure review is required; the accepted observed logic need not be redesigned. No tests, training, or inference were run in this review.
