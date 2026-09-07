from pathlib import Path
import importlib.util
import pytest

def test_fresh_training_contract():
    spec=importlib.util.find_spec('launch')
    assert spec is not None, 'corrected fresh launcher missing'
    from launch import training_args
    a=training_args('/workspace/runs/fresh')
    expected={'--T':'7','--frame-repeat':'1','--frame-window':'1','--frame-stride':'1','--min-change-time':'5','--max-change-time':'5','--v-mode':'learned_z','--readout':'h2','--cls-head':'conv','--softmax-mode':'split','--memory-noise-std':'0.0','--attention-entropy-coef':'1e-6','--seed':'3','--n-trials':'123904','--jepa-coef':'0.0','--theta-start':'65.0'}
    for key,value in expected.items():assert a[a.index(key)+1]==value
    for flag in ['--raw-attention-readout','--sample-attention','--vision-qk-norm','--change-per-step']:assert flag in a
    assert '--resume' not in a
    c=training_args('/workspace/runs/fresh',canary=True)
    c[c.index('--n-trials')+1]='123904'
    assert c==a

def test_checkpoint_protocol_guard():
    from launch import validate_checkpoint
    with pytest.raises(ValueError):validate_checkpoint({'collection':120})
    with pytest.raises(ValueError):validate_checkpoint({'supervised_sequence_version':'shifted','collection':120})
    c={'supervised_sequence_version':'blank_first_v1','collection':0,'raw_attention_readout':True,'v_mode':'learned_z','sample_attention':True,'softmax_mode':'split','memory_noise_std':0,'readout':'h2'}
    validate_checkpoint(c)
    c['sample_attention']=False
    with pytest.raises(ValueError):validate_checkpoint(c)
