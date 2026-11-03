"""Small local authoring utility; emits YAML only, never runs strategy callbacks."""
import copy,json,subprocess
from pathlib import Path
import yaml
ROOT=Path('runs/research_campaign/volatility_expansion')
def run(n,parent,mutate,hypothesis,change,expected):
    spec=yaml.safe_load((ROOT/'strategies'/f'p1_r{parent:02d}.yaml').read_text())
    spec=copy.deepcopy(spec); mutate(spec)
    spec['id']=f'volatility_expansion_p1_r{n:02d}'
    spec['hypothesis']=hypothesis
    path=ROOT/'strategies'/f'p1_r{n:02d}.yaml';path.write_text(yaml.safe_dump(spec,sort_keys=False))
    prev=json.loads((ROOT/'phase_1'/f'round_{parent:02d}.json').read_text())
    args=['.venv/bin/python','scripts/research_round.py','--family','volatility_expansion','--phase','1','--round',str(n),'--strategy',str(path),'--hypothesis',hypothesis,'--change',change,'--lesson',expected,'--parent',prev['run_id']]
    result=subprocess.run(args,capture_output=True,text=True)
    (ROOT/'phase_1'/f'round_{n:02d}.stdout.txt').write_text(result.stdout+result.stderr)
    if result.returncode: print(result.stdout+result.stderr);raise RuntimeError(f'Round{n} failed')
    r=json.loads((ROOT/'phase_1'/f'round_{n:02d}.json').read_text())
    print(json.dumps({'round':n,'run':r['run_id'],'rank':r['ranking_key'],'trades':r['total_trades'],'positive':r['positive_score_instruments'],'passes':r['passing_instruments'],'missing_months_positive':r['positive_score_but_fails_monthly'],'seconds':r['seconds']},indent=2))
    with (ROOT/'phase_1'/'learning.md').open('a') as f:
      f.write(f"\n## Round {n}: {change}\n\nHypothesis: {hypothesis}\n\nExpected learning: {expected}\n\nObserved: {r['automatic_diagnosis']} Ranking {r['ranking_key']}; {r['total_trades']} actual trades.\n")
    return r

def note(text):
 with (ROOT/'phase_1'/'learning.md').open('a') as f:f.write('\nInterpretation and next decision: '+text+'\n')
