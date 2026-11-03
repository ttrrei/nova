from pathlib import Path
import copy,json,subprocess,yaml
ROOT=Path('runs/research_campaign/mean_reversion')
PHASE=ROOT/'phase_1';PHASE.mkdir(exist_ok=True)
BASE=yaml.safe_load(Path('strategies/directions/mean_reversion.yaml').read_text())
def predicate(feature,op,value):return {'feature':feature,'op':op,'value':value}
def all_(*conditions):return {'all':list(conditions)}
def within(n,condition):return {'within':{'bars':n,'condition':condition}}
def held(n,condition):return {'held_for':{'bars':n,'condition':condition}}
def prior(n):return json.loads((PHASE/f'round_{n:02d}.json').read_text())
def spec(n):return yaml.safe_load((ROOT/'strategies'/f'phase_1_round_{n:02d}.yaml').read_text())
def learn(n,text):
 r=prior(n)
 with (PHASE/'learning.md').open('a') as f:
  f.write(f"\n## Round {n:02d}\n\nHypothesis: {r['hypothesis']}\n\nChange: {r['change']}\n\nResult: {len(r['passing_instruments'])}/21 pass, {len(r['positive_score_instruments'])}/21 positive, {r['total_trades']:,} trades; rank {r['ranking_key']}; run `{r['run_id']}`.\n\nPost-result lesson: {text}\n")
def run(n,s,hyp,change,expected,parent=None):
 s=copy.deepcopy(s);s['id']=f'mean_reversion_p1_r{n:02d}';s['hypothesis']=hyp
 p=ROOT/'strategies'/f'phase_1_round_{n:02d}.yaml';p.write_text(yaml.safe_dump(s,sort_keys=False))
 args=['.venv/bin/python','scripts/research_round.py','--family','mean_reversion','--phase','1','--round',str(n),'--strategy',str(p),'--hypothesis',hyp,'--change',change,'--lesson',expected]
 if parent:args+=['--parent',prior(parent)['run_id']]
 c=subprocess.run(args,capture_output=True,text=True)
 if c.returncode:print(c.stdout,c.stderr);raise RuntimeError(c.returncode)
 r=prior(n)
 print('ROUND',n,'PASSES',len(r['passing_instruments']),'POSITIVE',len(r['positive_score_instruments']),'TRADES',r['total_trades'],'RANK',r['ranking_key'])
 print('PASS_NAMES',r['passing_instruments'])
 print('POSITIVE_MONTHLY_FAIL',r['positive_score_but_fails_monthly'])
 print('SCORES',[(k,round(v['annualized_trade_return_score']*100,2),v['zero_entry_complete_months']) for k,v in r['per_instrument'].items()])
 return r
