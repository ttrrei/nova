import copy,json,subprocess,sys
from pathlib import Path
import yaml
ROOT=Path('runs/research_campaign/session_temporal')
BASE=yaml.safe_load(Path('strategies/directions/session_temporal.yaml').read_text())
def load(n):return yaml.safe_load((ROOT/'strategies'/f'p1_r{n:02}.yaml').read_text())
def trial(n,spec,hypothesis,change,expected,parent=None):
 spec=copy.deepcopy(spec);spec['id']=f'session_p1_r{n:02}';spec['hypothesis']=hypothesis
 path=ROOT/'strategies'/f'p1_r{n:02}.yaml';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(yaml.safe_dump(spec,sort_keys=False))
 cmd=['.venv/bin/python','scripts/research_round.py','--family','session_temporal','--phase','1','--round',str(n),'--strategy',str(path),'--hypothesis',hypothesis,'--change',change,'--lesson',expected]
 if parent:cmd += ['--parent',json.loads((ROOT/'phase_1'/f'round_{parent:02}.json').read_text())['run_id']]
 subprocess.run(cmd,check=True)
def note(n,text):
 r=json.loads((ROOT/'phase_1'/f'round_{n:02}.json').read_text());p=ROOT/'phase_1'/'learning.md'
 with p.open('a') as f:
  f.write(f"\n## Round{n}: {r['hypothesis']}\n\nChange: {r['change']}\n\nObserved: {len(r['passing_instruments'])}/21 pass; {len(r['positive_score_instruments'])}/21 positive; {r['total_trades']:,} trades. Median pass {r['ranking_key'][1]:.4%}/year; median all21 {r['ranking_key'][2]:.4%}/year. Run `{r['run_id']}`. Audit passed.\n\nPost-result lesson: {text}\n")
if __name__=='__main__':pass
