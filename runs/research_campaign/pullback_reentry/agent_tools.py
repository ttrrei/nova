"""Direction-local experiment authoring helpers, separate from YAML runtime."""

import copy
import json
from pathlib import Path
import subprocess
import yaml

ROOT = Path('runs/research_campaign/pullback_reentry')


def baseline():
    return yaml.safe_load(Path('strategies/directions/pullback_reentry.yaml').read_text())


def spec_for(number, phase=1):
    return yaml.safe_load((ROOT/'strategies'/f'phase_{phase}_round_{number:02d}.yaml').read_text())


def record(number, phase=1):
    return json.loads((ROOT/f'phase_{phase}'/f'round_{number:02d}.json').read_text())


def best(phase=1):
    rows = [json.loads(p.read_text()) for p in (ROOT/f'phase_{phase}').glob('round_??.json')]
    return max(rows, key=lambda r: r['ranking_key'])


def run_round(number, spec, hypothesis, change, expected, parent=None, phase=1):
    spec=copy.deepcopy(spec)
    spec['id']=f'pullback_phase{phase}_r{number:02d}'
    spec['hypothesis']=hypothesis
    path=ROOT/'strategies'/f'phase_{phase}_round_{number:02d}.yaml'
    path.write_text(yaml.safe_dump(spec,sort_keys=False))
    phase_root=ROOT/f'phase_{phase}';phase_root.mkdir(exist_ok=True)
    args=['.venv/bin/python','scripts/research_round.py','--family','pullback_reentry',
          '--phase',str(phase),'--round',str(number),'--strategy',str(path),
          '--hypothesis',hypothesis,'--change',change,'--lesson',expected]
    if parent:args.extend(['--parent',parent])
    with (phase_root/f'agent_round_{number:02d}.log').open('w') as log:
        subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,check=True)
    r=record(number,phase)
    print(json.dumps({'round':number,'run_id':r['run_id'],'rank':r['ranking_key'],
      'trades':r['total_trades'],'passes':r['passing_instruments'],
      'positive_missing_months':r['positive_score_but_fails_monthly'],
      'seconds':r['seconds'],
      'pass_scores':{k:round(r['per_instrument'][k]['annualized_trade_return_score'],5) for k in r['passing_instruments']}},indent=2))
    with (phase_root/'learning.md').open('a') as f:
        f.write(f'\n## Round {number}\n\nHypothesis: {hypothesis}\n\nChange: {change}\n\nExpected lesson: {expected}\n\nObserved: {r["automatic_diagnosis"]} Trades: {r["total_trades"]:,}. Ranking: {r["ranking_key"]}. Passing instruments: {", ".join(r["passing_instruments"]) or "none"}. Run `{r["run_id"]}`.\n')
    return r


def learn(number,text,phase=1):
    with (ROOT/f'phase_{phase}'/'learning.md').open('a') as f:
        f.write(f'\nPost-result lesson and next decision after round {number}: {text}\n')
