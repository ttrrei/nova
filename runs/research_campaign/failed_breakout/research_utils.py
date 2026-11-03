import argparse
import contextlib
import io
import json
from pathlib import Path
import sys
import yaml
sys.path.insert(0,str(Path('scripts').resolve()))
from research_round import execute_round
ROOT=Path('runs/research_campaign/failed_breakout')
PHASE=1

def record(n):
 return json.loads((ROOT/f'phase_{PHASE}'/f'round_{n:02d}.json').read_text())

def spec(n=0):
 p=Path('strategies/directions/failed_breakout.yaml') if n==0 else Path(record(n)['strategy_path'])
 return yaml.safe_load(p.read_text())

def atom(feature,op,value):return {'feature':feature,'op':op,'value':value}

def add(s,long,short=None):
 for side,condition in [('long',long),('short',short if short is not None else long)]:
  if side not in s['entry']:continue
  old=s['entry'][side]
  if set(old)=={'all'}:old['all'].append(condition)
  else:s['entry'][side]={'all':[old,condition]}
 return s

def test(n,parent,mutate,hypothesis,change,expectation):
 s=spec(parent);mutate(s)
 s['id']=f'campaign_failed_breakout_p{PHASE}_r{n:02d}';s['hypothesis']=hypothesis
 p=ROOT/'strategies'/f'p{PHASE}_r{n:02d}.yaml';p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(yaml.safe_dump(s,sort_keys=False))
 a=argparse.Namespace(campaign='runs/research_campaign',family='failed_breakout',phase=PHASE,round=n,strategy=str(p),hypothesis=hypothesis,change=change,lesson=expectation,parent=record(parent)['run_id'] if parent else None)
 with contextlib.redirect_stdout(io.StringIO()):r=execute_round(a)
 note=ROOT/f'phase_{PHASE}'/'learning.md'
 with note.open('a') as f:
  f.write(f"\n## Round {n:02d}\n\nHypothesis: {hypothesis}\n\nChange: {change}\n\nExpected lesson: {expectation}\n\nObserved: {r['automatic_diagnosis']} Trades {r['total_trades']:,}; ranking {r['ranking_key']}; run `{r['run_id']}`; audit passed. Passing: {', '.join(r['passing_instruments']) or 'none'}.\n")
 print(json.dumps({k:r[k] for k in ['round','run_id','total_trades','ranking_key','passing_instruments','positive_score_but_fails_monthly','automatic_diagnosis']}))
 print('Scores:',[(k,round(v['annualized_trade_return_score'],4),v['zero_entry_complete_months']) for k,v in r['per_instrument'].items()])
 return r

def learn(n,text):
 with (ROOT/f'phase_{PHASE}'/'learning.md').open('a') as f:f.write(f'\nPost-result lesson after round {n:02d}: {text}\n')
