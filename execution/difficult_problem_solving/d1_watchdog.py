"""D1-only external deadline and durable accounting. No model imports."""
from __future__ import annotations
import argparse
import fcntl
import hashlib
import json
import math
import os
import re
from pathlib import Path
import signal
import subprocess
import tempfile
import time
import uuid
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[1]
ROOT = WORKSPACE / 'execution/model_training_comparison'
LEDGER = ROOT / 'ledger.jsonl'
OWNER = 'difficult-d1-repair-001'
PREFIX_SHA = '770d3490766d0ec2e40a796ee8f896b4f1fbc3e7647c00d145cf4010dfc7d7c0'
ADMIN_ID = 'd1-recovery-administrative-uncertainty-20260920-160627'
PLAN_SHA = '370650b044b51eab8c331b54718e0af85be9dfa75758bab695e23cc4312d2a31'
CAPS = {'A': 1000., 'B': 3500., 'C': 0., 'D': 1400.}
CARRY = 923.003597253
RECOVERY = 'd1-minimal-repair'
FINALIZATION_ALLOWANCE = 1.0  # Prospective, disclosed; included in the same envelope.
SMOKE = 'tests/test_difficult_problem_solving_d1.py::test_actual_evaluator_counter_and_common_uniform_warm_cache'
SUITE = 'tests/test_difficult_problem_solving_d1.py'
REVIEW_PATHS = {'static': HERE / 'd1-repair-static-review.md',
                'implementation': HERE / 'd1-repair-implementation-review.md'}

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def utc():
    return datetime.now(timezone.utc).isoformat()

def fsync_directory(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)

def durable(path, value):
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(json.dumps(value, sort_keys=True, allow_nan=False).encode())
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        fsync_directory(path.parent)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def file_hashes():
    return {name: digest(path) for name, path in {
        'd1': HERE / 'd1.py', 'test': WORKSPACE / SUITE,
        'watchdog': HERE / 'd1_watchdog.py'}.items()}

def authority_hashes():
    names = ('d1-minimal-repair-plan.md', 'd1-recovery-approval.md',
             'd1-astra-approval.md', 'd1-minimal-repair-plan-review.md')
    result = {name: digest(HERE / name) for name in names}
    if result[names[0]] != PLAN_SHA:
        raise RuntimeError('frozen plan changed')
    return result

def verify_ledger(path):
    raw = Path(path).read_bytes()
    lines = raw.splitlines(keepends=True)
    if not raw.endswith(b'\n') or len(lines) < 144:
        raise RuntimeError('ledger truncated or missing addendum')
    if hashlib.sha256(b''.join(lines[:143])).hexdigest() != PREFIX_SHA:
        raise RuntimeError('frozen historical prefix changed')
    rows = [json.loads(line) for line in lines]
    ids, totals, carries = set(), dict.fromkeys(CAPS, 0.), []
    for row in rows:
        ident, charge = row.get('entry_id'), row.get('charged_seconds')
        if not isinstance(ident, str) or ident in ids:
            raise RuntimeError('duplicate/missing ledger UUID')
        ids.add(ident)
        if isinstance(charge, bool) or not isinstance(charge, (int, float)) or not math.isfinite(charge) or charge < 0:
            raise RuntimeError('nonfinite/negative charge')
        if row.get('kind') == 'inherited_budget':
            carries.append(row)
        elif row.get('stage') in totals:
            totals[row['stage']] += charge
        else:
            raise RuntimeError('invalid ledger stage')
    if len(carries) != 1 or carries[0].get('carried_budget_debit_seconds') != CARRY or carries[0]['charged_seconds'] != 0:
        raise RuntimeError('exact single carry required')
    admin = rows[143]
    if (admin.get('entry_id'), admin.get('kind'), admin.get('stage'), admin.get('charged_seconds')) != (ADMIN_ID, 'administrative_uncertainty_debit', 'A', 300.):
        raise RuntimeError('approved administrative addendum mismatch')
    return rows, {**totals, 'global': CARRY + sum(totals.values())}

def expected_argv(kind, decision_path):
    python = str(WORKSPACE / '.venv/bin/python')
    if kind in ('smoke', 'suite'):
        return [python, '-m', 'pytest', '-q', SMOKE if kind == 'smoke' else SUITE]
    return [python, '-m', 'execution.difficult_problem_solving.d1',
            '--production-decision', str(Path(decision_path).resolve())]

def verify_review(record, hashes, phase):
    path = Path(record['path']).resolve()
    if path != REVIEW_PATHS[phase].resolve() or record.get('phase') != phase or digest(path) != record.get('sha256'):
        raise RuntimeError('review identity/phase mismatch')
    text = path.read_text()
    declarations = re.findall(r'^D1_REVIEW_VERDICT:\s*(.*?)\s*$', text, re.MULTILINE)
    other_verdicts = re.findall(r'^\s*#+\s*Verdict:\s*(.*?)\s*$', text, re.MULTILINE | re.IGNORECASE)
    if (declarations != ['PASS'] or any(v != 'PASS' for v in other_verdicts) or
            record.get('verdict') != 'PASS' or any(value not in text for value in hashes.values())):
        raise RuntimeError('review must bind exact three hashes and PASS')

def validate_decision(path, *, expected_kind=None):
    path = Path(path).resolve()
    decision = json.loads(path.read_text())
    kind, seconds = decision.get('kind'), decision.get('seconds')
    if kind not in ('smoke', 'suite', 'production') or (expected_kind and kind != expected_kind):
        raise RuntimeError('wrong decision kind')
    allowed = {'smoke': (10.,), 'suite': (30., 60.), 'production': (300.,)}
    if seconds not in allowed[kind] or decision.get('approved') is not True:
        raise RuntimeError('unapproved envelope')
    hashes = file_hashes()
    if decision.get('hashes') != hashes or decision.get('authorities') != authority_hashes():
        raise RuntimeError('code/authority identity changed')
    if decision.get('cwd') != str(WORKSPACE) or Path.cwd().resolve() != WORKSPACE:
        raise RuntimeError('exact workspace required')
    if decision.get('argv') != expected_argv(kind, path) or decision.get('owner') != OWNER:
        raise RuntimeError('exact approved argv/owner required')
    if decision.get('ledger') != str(LEDGER) or decision.get('ledger_sha256') != digest(LEDGER):
        raise RuntimeError('decision must bind current ledger EOF')
    verify_review(decision['review'], hashes, 'implementation' if kind == 'production' else 'static')
    if seconds == 60.:
        concurrence = decision.get('sol_concurrence', {})
        value = json.loads(Path(concurrence['path']).read_text())
        if digest(concurrence['path']) != concurrence.get('sha256') or value != {
                'approved': True, 'seconds': 60., 'hashes': hashes, 'argv': decision['argv']}:
            raise RuntimeError('exact Sol 60-second concurrence required')
    verify_ledger(LEDGER)
    return decision

def group_gone(pgid):
    try:
        os.killpg(pgid, 0)
        return False
    except ProcessLookupError:
        return True

def supervise(command, cwd, logs, deadline):
    """One real child group; grace is INSIDE the supplied total deadline."""
    child = None
    timed_out = False
    cleanup = False
    with (logs / 'stdout.txt').open('wb') as out, (logs / 'stderr.txt').open('wb') as err:
        try:
            child = subprocess.Popen(command, cwd=cwd, stdout=out, stderr=err, start_new_session=True)
            remaining = max(0., deadline - time.monotonic())
            grace = min(2., remaining * .2)
            try:
                child.wait(timeout=max(.001, remaining - grace))
            except subprocess.TimeoutExpired:
                timed_out = True
            if not group_gone(child.pid):
                try:
                    os.killpg(child.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                term_end = min(deadline, time.monotonic() + grace / 2)
                while time.monotonic() < term_end:
                    child.poll()
                    if group_gone(child.pid):
                        break
                    time.sleep(.01)
                if not group_gone(child.pid):
                    try:
                        os.killpg(child.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                while time.monotonic() < deadline:
                    child.poll()
                    if group_gone(child.pid):
                        break
                    time.sleep(.01)
            child.poll()
            cleanup = group_gone(child.pid) and child.returncode is not None
            if not cleanup:
                raise RuntimeError('process group cleanup not verified within envelope')
            return {'child_pid': child.pid, 'exit_code': child.returncode,
                    'timed_out': timed_out, 'cleanup_verified': True}
        finally:
            out.flush(); os.fsync(out.fileno())
            err.flush(); os.fsync(err.fileno())
            if child is not None and not cleanup:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                try:
                    child.wait(timeout=.2)
                except subprocess.TimeoutExpired:
                    pass

def append_once(ledger, row):
    rows, _ = verify_ledger(ledger)
    if any(old['entry_id'] == row['entry_id'] for old in rows):
        raise RuntimeError('duplicate command charge')
    with Path(ledger).open('ab') as handle:
        handle.write(json.dumps(row, sort_keys=True, allow_nan=False).encode() + b'\n')
        handle.flush(); os.fsync(handle.fileno())
    fsync_directory(Path(ledger).parent)

def validate_production_artifacts(output, attempt, manifest):
    """Stdlib-only terminal integrity check; does not load model/test payloads."""
    def bound(relative):
        path = output / relative
        if (Path(relative).is_absolute() or '..' in Path(relative).parts or
                not path.is_file() or manifest.get(relative, {}).get('sha256') != digest(path)):
            raise RuntimeError('production manifest mismatch: ' + relative)
        return json.loads(path.read_text())
    result, index, panel = bound('d1.json'), bound('cell-index.json'), bound('panel.json')
    bound('provenance.json')
    ids = {f'{s}-{m}-{t:g}' for s in (1702,1703,1704,1705)
           for m in ('sm','sa') for t in (.5,.75,1.,1.25,1.5)}
    entries = index.get('cells', [])
    if (result.get('status') not in ('COMPLETE','CONTROL_NO_GO') or index.get('status') != 'COMPLETE'
            or len(entries) != 40 or {x.get('cell_id') for x in entries} != ids
            or result.get('cells') != entries or len(panel.get('ordered_problem_ids', [])) != 512
            or index.get('panel_sha256') != digest(output/'panel.json')):
        raise RuntimeError('incomplete production result/index/panel')
    greedy = index.get('greedy', [])
    gids = {f'{s}-{m}'for s in (1702,1703,1704,1705)for m in ('sm','sa')}
    if len(greedy)!=8 or {x.get('greedy_id')for x in greedy}!=gids:
        raise RuntimeError('incomplete greedy index')
    for item in greedy:
        relative='greedy/'+item['greedy_id']+'.json';bound(relative)
        if item.get('sha256')!=digest(output/relative):raise RuntimeError('greedy index hash mismatch')
    bindings=index.get('bindings',{})
    if set(bindings)!={'1702','1703','1704','1705'}:raise RuntimeError('incomplete bindings')
    for seed,value in bindings.items():
        relative='binding-'+seed+'.json';bound(relative)
        if value!=digest(output/relative):raise RuntimeError('binding index hash mismatch')
    for item in entries:
        relative='cells/'+item['cell_id']+'.json';cell=bound(relative)
        if (item.get('status')!='COMPLETE' or item.get('sha256')!=digest(output/relative)
                or cell.get('panel_sha256')!=index['panel_sha256']
                or cell.get('binding_sha256')!=bindings.get(str(cell.get('seed')))
                or cell.get('greedy_id')!=f"{cell.get('seed')}-{cell.get('mode')}"
                or item['cell_id']!=f"{cell.get('seed')}-{cell.get('mode')}-{float(cell.get('temperature')):g}"):
            raise RuntimeError('cell index/reference mismatch')

def reconcile_production(rows, ledger, output, ident, charged, record_path, *, elapsed=None):
    related = [r for r in rows if r.get('stage') == 'D' and r.get('output') == str(output)]
    fallback = [r for r in related if r.get('kind') == 'watchdog_uncertain_fallback'
                or r.get('recovery') == RECOVERY or r.get('status') == 'UNCERTAIN_FAILURE']
    if fallback:
        return {'status':'PERMANENT_UNCERTAIN_FALLBACK','success':False,
                'entry_ids':[r['entry_id']for r in fallback]}
    owned = related
    if not owned:
        row = {'entry_id': ident, 'recorded_at_utc': utc(), 'kind': 'watchdog_uncertain_fallback',
               'stage': 'D', 'status': 'UNCERTAIN_FAILURE', 'charged_seconds': charged,
               'elapsed_seconds': elapsed, 'finalization_allowance_seconds': FINALIZATION_ALLOWANCE,
               'recovery': RECOVERY, 'output': str(output), 'watchdog_record': str(record_path)}
        append_once(ledger, row)
        return {'status': 'UNCERTAIN_FALLBACK', 'entry_id': ident, 'success': False}
    if len(owned) != 1:
        raise RuntimeError('ambiguous production owner charges')
    row = owned[0]
    if (row.get('kind')!='attempt_charge' or row.get('status')!='FINALIZATION_UNCERTAIN'
            or row.get('startup_allowance_seconds')!=2. or row.get('finalization_allowance_seconds')!=2.):
        raise RuntimeError('not an accepted OwnedAttempt charge')
    uuid.UUID(row['entry_id'])
    attempt_path, manifest_path = output / 'attempt.json', output / 'output-manifest.json'
    if not attempt_path.is_file() or not manifest_path.is_file():
        return {'status': 'OWNED_CHARGED_ARTIFACT_FAILURE', 'entry_id': row['entry_id'],
                'charged_seconds': row['charged_seconds'], 'success': False,
                'reason': 'owned ledger charge exists; terminal artifacts incomplete; no fallback debit'}
    attempt, manifest = json.loads(attempt_path.read_text()), json.loads(manifest_path.read_text())
    if manifest.get('attempt.json', {}).get('sha256') != digest(attempt_path):
        raise RuntimeError('terminal attempt manifest mismatch')
    for key in ('entry_id', 'stage', 'output', 'charged_seconds'):
        if attempt.get(key) != row.get(key):
            raise RuntimeError('owner/ledger ' + key + ' mismatch')
    if attempt.get('kind')!='attempt' or attempt.get('ledger_path')!=str(Path(ledger).resolve()):
        raise RuntimeError('terminal attempt identity mismatch')
    if attempt.get('status') == 'COMPLETE':
        validate_production_artifacts(output,attempt,manifest)
    return {'status': 'OWNED_RECONCILED', 'entry_id': row['entry_id'],
            'attempt_sha256': digest(attempt_path), 'charged_seconds': row['charged_seconds'],
            'success': attempt.get('status') == 'COMPLETE'}

def execute(decision_path, record_dir):
    started = time.monotonic()
    record_dir = Path(record_dir).resolve()
    record_dir.mkdir(parents=True, exist_ok=False)
    ident = str(uuid.uuid4())
    lock = Path(str(LEDGER) + '.watchdog.lock').open('a+')
    reservation = Path(str(LEDGER) + '.d1-reservation.json')
    result = {'id': ident, 'started_utc': utc(), 'decision_path': str(Path(decision_path).resolve())}
    reserved = False
    accounted = False
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if reservation.exists():
            raise RuntimeError('unresolved prior watchdog reservation; no relaunch')
        decision = validate_decision(decision_path)
        rows, totals = verify_ledger(LEDGER)
        seconds, kind = decision['seconds'], decision['kind']
        stage = 'D' if kind == 'production' else 'A'
        spent = sum(r['charged_seconds'] for r in rows if r.get('stage') == 'A' and r.get('recovery') == RECOVERY)
        if (stage == 'A' and spent + seconds > 120.) or totals[stage] + seconds > CAPS[stage] or totals['global'] + seconds > 7200.:
            raise RuntimeError('recovery/stage/global headroom exhausted')
        output = ROOT / OWNER
        if kind == 'production' and (output.exists() or (ROOT / 'experiment.lock').exists()):
            raise RuntimeError('production owner/lock is not unused')
        result.update({'decision': decision, 'decision_sha256': digest(decision_path),
                       'ledger_before_sha256': digest(LEDGER), 'envelope_seconds': seconds})
        durable(record_dir / 'start.json', result)
        durable(reservation, {'id': ident, 'record_dir': str(record_dir), 'stage': stage, 'reserved_seconds': seconds})
        reserved = True
        for name in ('stdout.txt', 'stderr.txt'):
            (record_dir / name).touch(exist_ok=False)
        try:
            result.update(supervise(decision['argv'], WORKSPACE, record_dir, started + seconds - FINALIZATION_ALLOWANCE))
        except BaseException as error:
            result.update({'error': repr(error), 'exit_code': None, 'cleanup_verified': False})
        result.update({'ended_utc': utc(), 'elapsed_seconds': time.monotonic() - started,
                       'stdout_sha256': digest(record_dir / 'stdout.txt'),
                       'stderr_sha256': digest(record_dir / 'stderr.txt')})
        result['finalization_allowance_seconds'] = FINALIZATION_ALLOWANCE
        result['charged_seconds'] = result['elapsed_seconds'] + FINALIZATION_ALLOWANCE
        result['overrun'] = result['charged_seconds'] > seconds
        durable(record_dir / 'terminal.json', result)
        rows, _ = verify_ledger(LEDGER)
        if stage == 'A':
            append_once(LEDGER, {'entry_id': ident, 'recorded_at_utc': utc(), 'kind': 'attempt_charge',
                'stage': 'A', 'charged_seconds': result['charged_seconds'], 'elapsed_seconds': result['elapsed_seconds'],
                'finalization_allowance_seconds': FINALIZATION_ALLOWANCE, 'recovery': RECOVERY,
                'status': 'COMPLETE' if result.get('exit_code') == 0 and not result.get('timed_out') else 'FAILED',
                'watchdog_record': str(record_dir), 'decision_sha256': result['decision_sha256']})
            result['accounting'] = {'status': 'APPENDED', 'entry_id': ident, 'success': True}
        else:
            result['accounting'] = reconcile_production(rows, LEDGER, output, ident, result['charged_seconds'], record_dir, elapsed=result['elapsed_seconds'])
        accounted = True
        result['actual_elapsed_after_accounting_seconds'] = time.monotonic() - started
        result['finalization_allowance_exceeded'] = result['actual_elapsed_after_accounting_seconds'] > result['charged_seconds']
        success = (result.get('exit_code') == 0 and result.get('cleanup_verified') and
                   not result.get('timed_out') and not result['overrun'] and not result['finalization_allowance_exceeded'] and result['accounting']['success'])
        result['status'] = 'COMPLETE' if success else 'STOP'
        durable(record_dir / 'result.json', result)
        if (accounted and result.get('cleanup_verified') and stage == 'A' and not result['overrun'] and not result['finalization_allowance_exceeded']) or success:
            reservation.unlink(); fsync_directory(reservation.parent)
        print(json.dumps(result, sort_keys=True))
        return 0 if success else 1
    except BaseException as error:
        result.update({'status': 'ACCOUNTING_STOP' if reserved and not accounted else 'PREFLIGHT_STOP',
                       'error': repr(error), 'ended_utc': utc(), 'elapsed_seconds': time.monotonic() - started})
        durable(record_dir / 'result.json', result)
        print(json.dumps(result, sort_keys=True))
        return 1
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--decision', required=True)
    parser.add_argument('--record-dir', required=True)
    args = parser.parse_args(argv)
    return execute(args.decision, args.record_dir)

if __name__ == '__main__':
    raise SystemExit(main())
