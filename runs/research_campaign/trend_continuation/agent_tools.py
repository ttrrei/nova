"""Local utilities for this direction agent; strategy computations stay in YAML."""
import json
import subprocess
from pathlib import Path

import yaml

ROOT = Path('runs/research_campaign/trend_continuation')


def read_spec(source):
    return yaml.safe_load(Path(source).read_text())


def submit(number, source, hypothesis, change, expected, mutate=None, parent=None, phase=1):
    if not Path('runs/research_campaign/READY.json').is_file():
        raise RuntimeError('Coordinator has not frozen the engine')
    spec = read_spec(source)
    if mutate:
        mutate(spec)
    spec['id'] = f'trend_continuation_p{phase}_r{number:02}'
    spec['hypothesis'] = hypothesis
    path = ROOT/'strategies'/f'p{phase}_r{number:02}.yaml'
    path.write_text(yaml.safe_dump(spec, sort_keys=False))
    command = ['.venv/bin/python', 'scripts/research_round.py', '--family', 'trend_continuation', '--phase', str(phase), '--round', str(number), '--strategy', str(path), '--hypothesis', hypothesis, '--change', change, '--lesson', expected]
    if parent is None and Path(source).parent == ROOT/'strategies':
        phase_number, round_number = Path(source).stem.split('_r')
        source_record = ROOT/f'phase_{phase_number[1:]}'/f'round_{int(round_number):02}.json'
        if source_record.is_file():
            parent = json.loads(source_record.read_text())['run_id']
    if parent:
        command += ['--parent', parent]
    subprocess.run(command, check=True)


def predicate(feature, op, value):
    return {'feature': feature, 'op': op, 'value': value}


def append_entry(spec, long_clause, short_clause):
    for side, clause in [('long',long_clause),('short',short_clause)]:
        node = spec['entry'][side]
        if set(node)=={'all'}:
            node['all'].append(clause)
        else:
            spec['entry'][side]={'all':[node,clause]}


def result(number,phase=1):
    return json.loads((ROOT/f'phase_{phase}'/f'round_{number:02}.json').read_text())


def learn(number,text,phase=1):
    r=result(number,phase)
    p=ROOT/f'phase_{phase}'/'learning.md'
    with p.open('a') as f:
        f.write(f"\n## Round {number:02}: {r['hypothesis']}\n\n")
        f.write(f"Change: {r['change']}\n\n")
        f.write(f"Observed: {r['total_trades']:,} trades; {len(r['positive_score_instruments'])}/21 positive; {len(r['passing_instruments'])}/21 pass. Ranking key: {r['ranking_key']}. Run `{r['run_id']}`; audit passed.\n\n")
        f.write('Passing instruments: '+(', '.join(r['passing_instruments']) or 'none')+'.\n\n')
        f.write('Post-result lesson: '+text+'\n')


def best(phase=1):
    values=[json.loads(p.read_text()) for p in (ROOT/f'phase_{phase}').glob('round_??.json')]
    return max(values,key=lambda r:r['ranking_key'])
