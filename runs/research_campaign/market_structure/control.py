"""Small local controller for twenty reviewed market-structure hypotheses."""
import copy
import json
from pathlib import Path
import subprocess
import yaml

ROOT = Path('runs/research_campaign/market_structure')
BASE = Path('strategies/directions/market_structure.yaml')


def test(number, parent, change, hypothesis, expected, modify=None):
    if parent:
        original = json.loads((ROOT / 'phase_1' / f'round_{parent:02d}.json').read_text())
        spec = yaml.safe_load(Path(original['strategy_path']).read_text())
    else:
        original = None
        spec = yaml.safe_load(BASE.read_text())
    spec = copy.deepcopy(spec)
    spec['id'] = f'market_structure_p1_r{number:02d}'
    spec['hypothesis'] = hypothesis
    if modify:
        modify(spec)
    path = ROOT / 'strategies' / f'p1_r{number:02d}.yaml'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(spec, sort_keys=False))
    cmd = ['.venv/bin/python', 'scripts/research_round.py', '--family', 'market_structure', '--phase', '1', '--round', str(number), '--strategy', str(path), '--hypothesis', hypothesis, '--change', change, '--lesson', expected]
    if original:
        cmd += ['--parent', original['run_id']]
    process = subprocess.run(cmd, capture_output=True, text=True)
    if process.returncode:
        print(process.stdout, process.stderr)
        raise RuntimeError('Round failed')
    record = json.loads((ROOT / 'phase_1' / f'round_{number:02d}.json').read_text())
    log = ROOT / 'phase_1' / 'learning.md'
    if not log.exists():
        log.write_text('# Market structure phase one learning\n\nAll rounds use causal rolling range boundaries, all21 instruments and full hourly history, fixed execution and mandatory2% stop. No future pivots are inferred.\n')
    with log.open('a') as f:
        f.write(f'\n## Round {number}\n\nHypothesis: {hypothesis}\n\nChange: {change}\n\nExpected learning: {expected}\n\nObserved: {record["total_trades"]:,} trades; {len(record["passing_instruments"])}/21 pass; {len(record["positive_score_instruments"])}/21 positive. Ranking {record["ranking_key"]}. Run `{record["run_id"]}`; audit passed.\n\nPassing: {", ".join(record["passing_instruments"]) or "none"}.\n')
    print(json.dumps({'round': number, 'ranking': record['ranking_key'], 'trades': record['total_trades'], 'pass': record['passing_instruments'], 'positive_missing_months': record['positive_score_but_fails_monthly'], 'scores': {k: [round(v['annualized_trade_return_score'], 5), v['zero_entry_complete_months']] for k, v in record['per_instrument'].items()}}, indent=2))
    return record


def post(number, lesson):
    with (ROOT / 'phase_1' / 'learning.md').open('a') as f:
        f.write(f'\nPost-result lesson and next decision after round {number}: {lesson}\n')
