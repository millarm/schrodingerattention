import numpy as np

from schrodinger.data import COPY, XOR, evaluation_sets, heldout_pair, training_batch, validate_batch


def test_training_batches_are_deterministic_paired_and_valid():
    first = training_batch(11, 7); second = training_batch(11, 7)
    assert first.digest() == second.digest()
    assert np.array_equal(first.tokens, second.tokens)
    assert not np.array_equal(first.tokens, training_batch(11, 8).tokens)
    validate_batch(first, first.tokens.shape[1] - 7, False)
    assert {XOR, COPY} == set(first.operations.tolist())


def test_evaluation_sets_are_balanced_unique_and_split_clean():
    sets = evaluation_sets(1729, 8)
    seen = set()
    for name, batch in sets.items():
        heldout = "heldout" in name; distractors = 8 if "d8" in name else 4
        validate_batch(batch, distractors, heldout)
        assert batch.tokens.shape[0] == 16
        for row in batch.tokens:
            assert row.tobytes() not in seen
            seen.add(row.tobytes())
        for pair in batch.pairs:
            assert heldout_pair(*pair.tolist()) == heldout


def test_full_evaluation_counts_are_frozen():
    sets = evaluation_sets()
    assert sets["validation_seen_d4"].tokens.shape[0] == 512
    for name, batch in sets.items():
        if name != "validation_seen_d4":
            assert batch.tokens.shape[0] == 1024
            for start in range(0, batch.tokens.shape[0], 64):
                operations, labels = batch.operations[start:start + 64], batch.labels[start:start + 64]
                assert all(int(((operations == operation) & (labels == label)).sum()) == 16 for operation in (XOR, COPY) for label in (0, 1))


def test_all_protocol_seeds_are_paired_and_heldout_orientations_excluded():
    for seed in (11, 22, 33):
        assert training_batch(seed, 4).digest() == training_batch(seed, 4).digest()
        batch = training_batch(seed, 4)
        assert all(not heldout_pair(*pair.tolist()) for pair in batch.pairs)


def test_blacklist_forces_deterministic_replacement_without_balance_loss():
    original = training_batch(11, 9)
    blacklist = {original.tokens[0].tobytes()}
    replaced = training_batch(11, 9, blacklist=blacklist)
    assert all(row.tobytes() not in blacklist for row in replaced.tokens)
    validate_batch(replaced, replaced.tokens.shape[1] - 7, False)
