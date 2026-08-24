#!/usr/bin/env python
from pathlib import Path
import argparse,csv,hashlib,json
import matplotlib.pyplot as plt
import numpy as np
from statistics import NormalDist

_NORMAL = NormalDist()

def ndtri(values: np.ndarray) -> np.ndarray:
    flat = np.asarray(values, dtype=float).ravel()
    return np.fromiter((_NORMAL.inv_cdf(float(x)) for x in flat), dtype=float, count=flat.size).reshape(np.shape(values))


def file_sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''): h.update(block)
    return h.hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('export_root',type=Path);a=ap.parse_args()
    base=a.export_root;ex=base/'extracted'
    d=json.loads((ex/'latest_full_battery_results.json').read_text())
    primary=[]
    for cond,rows in d['primary_results'].items():
        for r in rows:
            for role,loc in [('condition',str(r['condition_loc'])),('control',str(r['control_loc']))]:
                m=r['locations'][loc]
                primary.append({'measurement_condition':cond,'id':r['id'],'session':r['session'],'trained_condition_loc':r['condition_loc'],'measured_loc':loc,'location_role':role,'hit_rate':m['hit_rate'],'false_alarm_rate':m['false_alarm_rate'],'dprime':m['dprime'],'criterion':m['criterion'],'balanced_accuracy':m['balanced_accuracy'],'valid_fraction_change':m['valid_fraction_change'],'valid_fraction_no_change':m['valid_fraction_no_change'],'mean_hit_frame':m['mean_hit_frame'],'mean_false_alarm_frame':m['mean_false_alarm_frame'],'mean_correct_rejection_frame':m['mean_correct_rejection_frame']})
    with (base/'primary_summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=primary[0].keys());w.writeheader();w.writerows(primary)
    rng=np.random.default_rng(20260809);draws=10000;psych=[]
    for session in ['sensitivity','criterion']:
        specs=[r for r in d['primary_results']['trained_noise'] if r['session']==session]
        for mag in d['evaluation_contract']['psychometric_magnitudes']:
            key=str(mag).replace('.','p')
            recs={r['id']:r for r in d['psychometric_records'] if r['session']==session and r['magnitude']==mag}
            for role in ['condition','control']:
                model_dp=[];model_c=[];points=[]
                for spec in specs:
                    loc=spec['condition_loc'] if role=='condition' else spec['control_loc'];locs=str(loc)
                    z=np.load(ex/f"{spec['id']}_psychometric_outcomes.npz")
                    cp=z[f'change_press_mag_{key}'];cl=z[f'change_locations_mag_{key}'];npres=z['no_change_press'];nl=z['no_change_locations']
                    co=cp[cl==loc];no=npres[nl==loc]
                    cv=co[(co<0)|(co>=3)];hit=(cv>=3)&(cv<=4)
                    nv=no[(no>=3)&(no!=5)];fa=(nv>=3)&(nv<=4)
                    nc,nf=len(cv),len(nv);ph,pf=hit.mean(),fa.mean()
                    hb=rng.binomial(nc,ph,size=draws)/nc;fb=rng.binomial(nf,pf,size=draws)/nf
                    hb=np.clip(hb,1/(2*nc),1-1/(2*nc));fb=np.clip(fb,1/(2*nf),1-1/(2*nf))
                    zh,zf=ndtri(hb),ndtri(fb);model_dp.append(zh-zf);model_c.append(-0.5*(zh+zf));points.append(recs[spec['id']]['locations'][locs])
                dp=np.mean(model_dp,axis=0);cc=np.mean(model_c,axis=0)
                psych.append({'session':session,'magnitude':mag,'location_role':role,'dprime':float(np.mean([x['dprime'] for x in points])),'dprime_ci_low':float(np.quantile(dp,.025)),'dprime_ci_high':float(np.quantile(dp,.975)),'criterion':float(np.mean([x['criterion'] for x in points])),'criterion_ci_low':float(np.quantile(cc,.025)),'criterion_ci_high':float(np.quantile(cc,.975)),'hit_rate':float(np.mean([x['hit_rate'] for x in points])),'false_alarm_rate':float(np.mean([x['false_alarm_rate'] for x in points])),'balanced_accuracy':float(np.mean([x['balanced_accuracy'] for x in points])),'uncertainty_scope':'trial bootstrap conditional on four fixed seed-0 policies'})
    with (base/'psychometric_summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=psych[0].keys());w.writeheader();w.writerows(psych)
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    def plot(session,metric,title,ylabel,outname):
        fig,ax=plt.subplots(figsize=(7.2,4.6),dpi=180);colors={'condition':'#d1495b','control':'#277da1'};labels={'condition':'Manipulated condition location','control':'Counterphase control location'}
        for role in ['condition','control']:
            rows=sorted([r for r in psych if r['session']==session and r['location_role']==role],key=lambda x:x['magnitude'])
            x=np.array([r['magnitude'] for r in rows]);y=np.array([r[metric] for r in rows]);lo=np.array([r[metric+'_ci_low'] for r in rows]);hi=np.array([r[metric+'_ci_high'] for r in rows])
            ax.plot(x,y,'o-',lw=2.4,ms=5,color=colors[role]);ax.fill_between(x,lo,hi,color=colors[role],alpha=.17,linewidth=0);ax.annotate(labels[role],(x[-1],y[-1]),xytext=(8,0),textcoords='offset points',va='center',color=colors[role],fontweight='bold',fontsize=9)
        ax.axhline(0,color='#777',lw=.8,alpha=.5);ax.set_xlabel('Exact orientation change |Δ| (degrees)');ax.set_ylabel(ylabel);ax.set_title(title,loc='left',fontweight='bold');ax.grid(axis='y',alpha=.18);ax.set_xlim(0,76);fig.tight_layout();fig.savefig(base/outname,bbox_inches='tight');plt.close(fig)
    plot('sensitivity','dprime','Sensitivity-trained policies: psychometric discriminability',"d′",'sensitivity_psychometric_dprime.png')
    plot('criterion','criterion','Criterion-trained policies: response criterion','Criterion c','criterion_psychometric_c.png')
    tr=d['counterphased_effects']['trained_noise'];zn=d['counterphased_effects']['zero_mnemonic_noise']
    report=f'''# Luo 2015 latest full behavioral battery\n\n## Decision\nDo **not** reduce mnemonic noise again on the basis of these agents. Removing mnemonic noise at evaluation leaves the effects nearly unchanged, so residual evaluation-time memory corruption is not the limiting mechanism. The failures are learned location-conditioned response policies.\n\n## Primary counterphased effects (trained noise)\n- Sensitivity d-prime DID: {tr['sensitivity_dprime_did']:.3f} (expected positive; observed negative)\n- Sensitivity criterion cross-effect: {tr['sensitivity_criterion_cross_did']:.3f} (expected near zero)\n- Criterion criterion DID: {tr['criterion_criterion_did']:.3f} (expected negative)\n- Criterion d-prime cross-effect: {tr['criterion_dprime_cross_did']:.3f} (expected near zero)\n\n## Zero-noise manipulation\n- Sensitivity d-prime DID: {zn['sensitivity_dprime_did']:.3f}\n- Sensitivity criterion cross-effect: {zn['sensitivity_criterion_cross_did']:.3f}\n- Criterion criterion DID: {zn['criterion_criterion_did']:.3f}\n- Criterion d-prime cross-effect: {zn['criterion_dprime_cross_did']:.3f}\n\nBoth sensitivity policies declared change on essentially every rewarded-location trial (HR=1, FA=1, d-prime=0). Criterion policies shifted criterion liberally as intended but lost substantial d-prime. All four strict behavioral-dissociation tests failed.\n\nUncertainty in psychometric_summary.csv and figures is a trial bootstrap conditional on the four fixed seed-0 policies; it is not across-seed uncertainty.\n'''
    (base/'analysis_report.md').write_text(report)
    names=['results.tar.gz','extracted/latest_full_battery_results.json','primary_summary.csv','psychometric_summary.csv','sensitivity_psychometric_dprime.png','criterion_psychometric_c.png','analysis_report.md']
    manifest={'files':{n:{'sha256':file_sha256(base/n),'bytes':(base/n).stat().st_size} for n in names},'source_archive_sha256':'b6e08a05ab999c3b1573906dd11621a25dee63ea3f587ef7562574a30290343f','checkpoint_bundle_sha256':'07950e656466d1b5ef6a5045b6522d54ff6e80893d84980e310d723661b4db79','result_archive_sha256':'fa11a75b69ae07c506b6ab251ede155d15aa9ea290ab161c495d774871f7aab6'}
    (base/'analysis_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'analysis_manifest_sha256':file_sha256(base/'analysis_manifest.json'),'trained':tr,'zero':zn},indent=2))
if __name__=='__main__':main()
