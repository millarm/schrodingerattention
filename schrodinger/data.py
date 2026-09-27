"""Deterministic keyed-retrieval data under the frozen experiment contract."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from itertools import combinations
from typing import Iterable

import numpy as np

CLS, XOR, COPY, SEP = 0, 1, 2, 3
KEY_OFFSET, FACT_OFFSET = 4, 16
VOCAB_SIZE = 40
KEY_COUNT = 12


@dataclass(frozen=True)
class Batch:
    tokens: np.ndarray
    labels: np.ndarray
    operations: np.ndarray
    pairs: np.ndarray

    def digest(self) -> str:
        h = hashlib.sha256()
        for value in (self.tokens, self.labels, self.operations, self.pairs):
            h.update(np.ascontiguousarray(value).tobytes())
        return h.hexdigest()


def fact_token(key: int, value: int) -> int:
    return FACT_OFFSET + 2 * key + value


def heldout_pair(a: int, b: int) -> bool:
    return (min(a, b) + max(a, b)) % 5 == 0


def eligible_pairs(heldout: bool) -> list[tuple[int, int]]:
    return [pair for pair in combinations(range(KEY_COUNT), 2) if heldout_pair(*pair) == heldout]


def _sample_example(rng: np.random.Generator, operation: int, label: int, distractors: int, heldout: bool) -> tuple[np.ndarray, tuple[int, int]]:
    a, b = eligible_pairs(heldout)[rng.integers(len(eligible_pairs(heldout)))]
    if rng.integers(2):
        a, b = b, a
    value_a = int(rng.integers(2)) if operation == XOR else label
    value_b = value_a ^ label if operation == XOR else int(rng.integers(2))
    keys = [a, b]
    available = [key for key in range(KEY_COUNT) if key not in keys]
    extras = rng.choice(available, size=distractors, replace=False).tolist()
    facts = [(a, value_a), (b, value_b)] + [(key, int(rng.integers(2))) for key in extras]
    rng.shuffle(facts)
    tokens = np.array([CLS, operation, KEY_OFFSET + a, KEY_OFFSET + b, SEP] + [fact_token(*fact) for fact in facts], dtype=np.int64)
    return tokens, (a, b)


def make_batch(seed: int | np.random.SeedSequence | np.random.Generator, count: int, distractors: int, heldout: bool, *, require_balanced: bool = True, blacklist: set[bytes] | None = None) -> Batch:
    if count % 4 or count <= 0:
        raise ValueError("count must be positive and divisible by four for operation/label balance")
    rng = seed if isinstance(seed, np.random.Generator) else np.random.default_rng(seed)
    rows: list[np.ndarray] = []
    labels: list[int] = []
    operations: list[int] = []
    pairs: list[tuple[int, int]] = []
    per_cell = count // 4
    for operation in (XOR, COPY):
        for label in (0, 1):
            accepted = 0
            while accepted < per_cell:
                row, pair = _sample_example(rng, operation, label, distractors, heldout)
                if blacklist is None or row.tobytes() not in blacklist:
                    rows.append(row); labels.append(label); operations.append(operation); pairs.append(pair); accepted += 1
    order = rng.permutation(count)
    batch = Batch(np.stack(rows)[order], np.array(labels, dtype=np.int64)[order], np.array(operations, dtype=np.int64)[order], np.array(pairs, dtype=np.int64)[order])
    validate_batch(batch, distractors, heldout, balanced=require_balanced)
    return batch


def training_batch(seed: int, update_index: int, batch_size: int = 64, blacklist: set[bytes] | None = None) -> Batch:
    """Paired stream binding: PCG64(SeedSequence([100000 + seed, update]))."""
    rng = np.random.default_rng(np.random.SeedSequence([100000 + seed, update_index]))
    distractors = int(rng.choice([2, 3, 4]))
    return make_batch(rng, batch_size, distractors, False, blacklist=blacklist)


def validate_batch(batch: Batch, distractors: int, heldout: bool, *, balanced: bool = True) -> None:
    expected_length = 7 + distractors
    if batch.tokens.ndim != 2 or batch.tokens.shape[1] != expected_length:
        raise AssertionError("fixed sequence length/fact count violation")
    if batch.tokens.shape[0] != batch.labels.size or batch.labels.shape != batch.operations.shape:
        raise AssertionError("metadata dimensions disagree")
    for row, label, operation, pair in zip(batch.tokens, batch.labels, batch.operations, batch.pairs, strict=True):
        a, b = int(row[2] - KEY_OFFSET), int(row[3] - KEY_OFFSET)
        if a == b or {a, b} != set(pair.tolist()) or heldout_pair(a, b) != heldout:
            raise AssertionError("pair exclusion/order violation")
        facts = row[5:]
        keys = [(int(token) - FACT_OFFSET) // 2 for token in facts]
        values = [(int(token) - FACT_OFFSET) % 2 for token in facts]
        if len(keys) != len(set(keys)) or set((a, b)) - set(keys):
            raise AssertionError("facts are not unique/complete")
        value_a, value_b = values[keys.index(a)], values[keys.index(b)]
        expected = value_a ^ value_b if operation == XOR else value_a
        if int(label) != expected:
            raise AssertionError("label mismatch")
    if balanced:
        for operation in (XOR, COPY):
            counts = [int(((batch.operations == operation) & (batch.labels == label)).sum()) for label in (0, 1)]
            if counts[0] != counts[1]:
                raise AssertionError("label balance violation")


def evaluation_sets(seed: int = 1729, count_per_operation: int | None = None) -> dict[str, Batch]:
    """Fixed, balanced evaluation collections; caller records their digests."""
    if count_per_operation is not None and count_per_operation % 2:
        raise ValueError("per-operation count must be even")
    definitions = {
        "validation_seen_d4": (seed, 4, False, 256 if count_per_operation is None else count_per_operation),
        "test_seen_d4": (2718, 4, False, 512 if count_per_operation is None else count_per_operation),
        "test_heldout_d4": (2719, 4, True, 512 if count_per_operation is None else count_per_operation),
        "test_seen_d8": (2720, 8, False, 512 if count_per_operation is None else count_per_operation),
        "test_heldout_d8": (2721, 8, True, 512 if count_per_operation is None else count_per_operation),
    }
    hashes: set[bytes] = set()
    result: dict[str, Batch] = {}
    for name, (value_seed, distractors, heldout, per_operation) in definitions.items():
        rng = np.random.default_rng(value_seed)
        rows: list[np.ndarray] = []; labels: list[int] = []; operations: list[int] = []; pairs: list[tuple[int, int]] = []
        blocks = max(1, (per_operation * 2) // 64)
        per_cell = per_operation // 2
        for block in range(blocks):
          block_start = len(rows)
          for operation in (XOR, COPY):
            for label in (0, 1):
                for _ in range(16 if per_operation * 2 >= 64 else per_cell):
                  while True:
                    row, pair = _sample_example(rng, operation, label, distractors, heldout)
                    item = row.tobytes()
                    if item not in hashes:
                        hashes.add(item); rows.append(row); labels.append(label); operations.append(operation); pairs.append(pair)
                        break
          block_order = rng.permutation(len(rows) - block_start)
          block_rows, block_labels, block_operations, block_pairs = rows[block_start:], labels[block_start:], operations[block_start:], pairs[block_start:]
          rows[block_start:] = [block_rows[index] for index in block_order]
          labels[block_start:] = [block_labels[index] for index in block_order]
          operations[block_start:] = [block_operations[index] for index in block_order]
          pairs[block_start:] = [block_pairs[index] for index in block_order]
        batch = Batch(np.stack(rows), np.array(labels, dtype=np.int64), np.array(operations, dtype=np.int64), np.array(pairs, dtype=np.int64))
        validate_batch(batch, distractors, heldout)
        result[name] = batch
    return result
