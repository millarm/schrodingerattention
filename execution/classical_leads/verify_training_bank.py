"""Check regenerated proposal-14 training data against recorded provenance.

``route_policy_data.load_training`` checks the training file's byte hash,
which includes an irreproducible elapsed-time field. This loads the
regenerated file (and the byte-identical regenerated inventory), builds the
training bank exactly as ``route_policy_experiment`` does, and compares its
``selected_hash`` with the value recorded by every committed route-policy run.

Usage: python execution/classical_leads/verify_training_bank.py REGEN_DIR
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from schrodinger import route_policy_data as data  # noqa: E402
from schrodinger import route_policy_experiment as experiment  # noqa: E402

RECORDED = "8879d863f1780a40821f518f9ec42bfc9cdd73d203cd872104c1acde52572618"


def load_regenerated_training(regen: Path):
    original = data._read_checked

    def read(name, digest):
        if name == "inventory.json":
            raw = (regen / name).read_bytes()
            if hashlib.sha256(raw).hexdigest() != digest:
                raise ValueError("regenerated inventory does not match manifest")
            return json.loads(raw)
        if name == "proposal-14-training.json":
            return json.loads((regen / name).read_bytes())
        return original(name, digest)

    data._read_checked = read
    try:
        return data.load_training()
    finally:
        data._read_checked = original


def main() -> None:
    training = load_regenerated_training(Path(sys.argv[1]))
    selected = experiment.bank_payload(experiment.training_bank(training.states))["selected_hash"]
    print(f"states {len(training.states)} problems {len(training.problems)}")
    print(f"selected_hash {selected} matches recorded: {selected == RECORDED}")
    sys.exit(0 if selected == RECORDED else 1)


if __name__ == "__main__":
    main()
