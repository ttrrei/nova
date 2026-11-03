"""Local experiment submission convenience; candidates remain reviewed YAML."""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import yaml

ROOT=Path('runs/research_campaign/volume_activity')
PHASE=ROOT/'phase_1'
PHASE.mkdir(parents=True,exist_ok=True)

def spec(n=None):
    path=ROOT/'strategies'/f'p1_r{n:02d}.yaml' if n else Path('strategies/directions/volume_activity.yaml')
    return yaml.safe_load(path.read_text())

def result(n):
    return json.loads((PHASE/f'round_{n:02d}.json').read_text())

def learn(n,text):
    with (PHASE/'learning.md').open('a') as f:
        f.write(f'\nPost-result lesson for round {n}: {text}\n')

def atom(feature,op,value):
    return dict(feature=feature,op=op,value=value)

def perform(n,s,hypothesis,change,expected,parent=None):
    s=copy.deepcopy(s);s['id']=f'campaign_volume_activity_p1_r{n:02d}';s['hypothesis']=hypothesis
    path=ROOT/'strategies'/f'p1_r{n:02d}.yaml';path.write_text(yaml.safe_dump(s,sort_keys=False))
    argv=['.venv/bin/python','scripts/research_round.py','--family','volume_activity','--phase','1','--round',str(n),'--strategy',str(path),'--hypothesis',hypothesis,'--change',change,'--lesson',expected]
    if parent:argv+=['--parent',result(parent)['run_id']]
    proc=subprocess.run(argv,text=True,capture_output=True)
    if proc.returncode:print(proc.stdout,proc.stderr);raise RuntimeError('round failed')
    r=result(n)
    with (PHASE/'learning.md').open('a') as f:
        f.write(f'\n## Round {n}\n\nHypothesis: {hypothesis}\n\nChange: {change}\n\nExpected learning: {expected}\n\nObserved: {len(r["passing_instruments"])}/21 pass, {len(r["positive_score_instruments"])}/21 positive, {r["total_trades"]:,} trades. Rank {r["ranking_key"]}. Run `{r["run_id"]}`; audit passed.\n')
    print(json.dumps({'round':n,'passes':r['passing_instruments'],'positive_monthly_failures':r['positive_score_but_fails_monthly'],'rank':r['ranking_key'],'trades':r['total_trades'],'per_instrument':{k:{'score':round(v['annualized_trade_return_score'],5),'zero_months':v['zero_entry_complete_months']} for k,v in r['per_instrument'].items()}},indent=2))
    return r
