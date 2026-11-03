import copy,json,subprocess
from pathlib import Path
import yaml
ROOT=Path('runs/research_campaign/range_trading')
PHASE=1

def load(n=None):
 return yaml.safe_load((ROOT/'strategies'/f'p1_r{n:02d}.yaml').read_text()) if n else yaml.safe_load(Path('strategies/directions/range_trading.yaml').read_text())

def learn(n,text):
 with (ROOT/f'phase_{PHASE}'/'learning.md').open('a') as f:f.write(f'\nPost-result lesson after round{n}: {text}\n')

def execute(n,spec,hypothesis,change,expected,parent=None):
 spec=copy.deepcopy(spec);spec['id']=f'range_p1_r{n:02d}';spec['hypothesis']=hypothesis
 p=ROOT/'strategies'/f'p1_r{n:02d}.yaml';p.write_text(yaml.safe_dump(spec,sort_keys=False))
 args=['.venv/bin/python','scripts/research_round.py','--family','range_trading','--phase',str(PHASE),'--round',str(n),'--strategy',str(p),'--hypothesis',hypothesis,'--change',change,'--lesson',expected]
 if parent:
  args+=['--parent',json.loads((ROOT/f'phase_{PHASE}'/f'round_{parent:02d}.json').read_text())['run_id']]
 q=subprocess.run(args,capture_output=True,text=True)
 if q.returncode:print(q.stdout,q.stderr);raise RuntimeError(q.returncode)
 r=json.loads((ROOT/f'phase_{PHASE}'/f'round_{n:02d}.json').read_text())
 with (ROOT/f'phase_{PHASE}'/'learning.md').open('a') as f:
  f.write(f"\n## Round {n}\n\nHypothesis: {hypothesis}\n\nChange: {change}\n\nExpected learning: {expected}\n\nObserved: {r['automatic_diagnosis']} Trades{r['total_trades']}; ranking{r['ranking_key']}. Run`{r['run_id']}`, audit passed.\n\nPassing: {', '.join(r['passing_instruments']) or 'none'}.\n")
 print(json.dumps({k:r[k] for k in ['round','run_id','total_trades','passing_instruments','positive_score_instruments','ranking_key']}))
 print(' '.join(f"{k}:{v['annualized_trade_return_score']*100:+.2f}%/z{v['zero_entry_complete_months']}" for k,v in r['per_instrument'].items()))
 return r

def atom(feature,op,value):return {'feature':feature,'op':op,'value':value}
