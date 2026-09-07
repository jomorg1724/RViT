"""Fresh blank-first no-memory run. No resume path, no automatic restart."""
import argparse,datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
VERSION='blank_first_v1'
def training_args(root,canary=False):
    pairs={'--task':'vda16','--label':'change','--attn-mode':'token','--readout':'h2','--v-mode':'learned_z','--softmax-mode':'split','--cls-head':'conv','--jepa-coef':'0.0','--theta-start':'65.0','--curr-threshold':'0.85','--curr-step':'3.0','--curr-floor':'8.0','--T':'7','--frame-repeat':'1','--frame-window':'1','--frame-stride':'1','--min-change-time':'5','--max-change-time':'5','--noise':'5.0','--accum-mode':'kda','--accum-decay':'0.5','--kda-heads':'4','--kda-head-dim':'32','--n-channels':'128','--map-size':'16','--proto-dim':'256','--memory-noise-std':'0.0','--mem-every':'3','--change-coef':'1.0','--entropy-coef':'0','--vision-qk-temperature':'11.313708498984761','--attention-entropy-coef':'1e-6','--n-trials':'1024' if canary else '123904','--collection-size':'1024','--epochs':'5','--batch-size':'16','--lr':'0.0003','--grad-clip':'1.0','--seed':'3','--device':'cuda','--save-every':'10','--log-every':'1','--checkpoint-dir':str(root)}
    a=['--vision-qk-norm','--change-per-step','--sample-attention','--raw-attention-readout']
    for k,v in pairs.items():a.extend([k,v])
    return a

def validate_checkpoint(c):
    expected={'supervised_sequence_version':VERSION,'raw_attention_readout':True,'v_mode':'learned_z','sample_attention':True,'softmax_mode':'split','memory_noise_std':0,'readout':'h2'}
    for k,v in expected.items():
        if c.get(k)!=v:raise ValueError('Incompatible checkpoint '+k+': '+repr(c.get(k)))

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--canary',action='store_true');p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    source=Path(__file__).resolve().parent;root=Path(a.root).resolve()
    argv=[sys.executable,'-u',str(source/'pretrain_kda_convmem.py')]+training_args(root,a.canary)
    if a.dry_run:print(json.dumps(argv));return
    from envs.sequences import SUPERVISED_SEQUENCE_VERSION
    assert SUPERVISED_SEQUENCE_VERSION==VERSION
    root.mkdir(parents=True,exist_ok=False)
    m={'protocol':VERSION,'supervised_sequence_version':VERSION,'fresh':True,'parent_checkpoint':None,'argv':argv,'frames':['blank','cue','blank','sample','sample','change','change'],'environment_times':list(range(7)),'changed_labels':[0,0,0,0,0,1,1],'seed':3,'terminal_collection':0 if a.canary else 120,'source_sha256':{str(f.relative_to(source)).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest() for f in source.rglob('*.py')},'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (root/'manifest.json').write_text(json.dumps(m,indent=2));(root/'supervisor.pid').write_text(str(os.getpid()))
    with (root/'supervisor.log').open('w',buffering=1) as log:
        proc=subprocess.Popen(argv,cwd=source,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
        (root/'trainer.pid').write_text(str(proc.pid));rc=proc.wait()
    if rc==0:
        import torch
        ck=torch.load(root/'kda_convmem_latest.pt',map_location='cpu',weights_only=False)
        validate_checkpoint(ck)
        assert ck['collection']==m['terminal_collection']
    (root/'exit.json').write_text(json.dumps({'exit_code':rc,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}))
    raise SystemExit(rc)
if __name__=='__main__':main()
