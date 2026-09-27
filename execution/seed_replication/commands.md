# Frozen serial command order

All commands await exact wrapper review PASS. One owned process at a time;
record full result/session and poll explicit exit before the next launch.

1. `.venv/bin/python -m execution.seed_replication.train --seed 1702 --mode softmax --decision execution/seed_replication/decisions/1702-softmax.json`

2. `.venv/bin/python -m execution.seed_replication.train --seed 1702 --mode schrodinger --decision execution/seed_replication/decisions/1702-schrodinger.json`

3. `.venv/bin/python -m execution.seed_replication.train --seed 1703 --mode schrodinger --decision execution/seed_replication/decisions/1703-schrodinger.json`

4. `.venv/bin/python -m execution.seed_replication.train --seed 1703 --mode softmax --decision execution/seed_replication/decisions/1703-softmax.json`

5. `.venv/bin/python -m execution.seed_replication.train --seed 1704 --mode softmax --decision execution/seed_replication/decisions/1704-softmax.json`

6. `.venv/bin/python -m execution.seed_replication.train --seed 1704 --mode schrodinger --decision execution/seed_replication/decisions/1704-schrodinger.json`

7. `.venv/bin/python -m execution.seed_replication.train --seed 1705 --mode schrodinger --decision execution/seed_replication/decisions/1705-schrodinger.json`

8. `.venv/bin/python -m execution.seed_replication.train --seed 1705 --mode softmax --decision execution/seed_replication/decisions/1705-softmax.json`

