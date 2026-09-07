"""Literal H1=Z and H2=sampled AX VX+AH VH, with cosine QK."""
import inspect
import torch
import torch.nn.functional as F
import kda_conv_memory_model as mod

def test_literal_nomem_equations_normalized_sampled_readout(monkeypatch):
    assert 'raw_attention_readout' in inspect.signature(mod.KDAConvMemoryModel).parameters
    torch.manual_seed(31)
    m=mod.KDAConvMemoryModel(n_channels=8,proto_dim=16,map_size=4,kda_heads=2,kda_head_dim=4,
        attn_mode='token',softmax_mode='split',v_mode='learned_z',readout='h2',cls_head='conv',
        vision_qk_norm=True,sample_attention=True,attention_entropy_coef=1e-6,
        memory_noise_std=0,mem_every=3,raw_attention_readout=True)
    assert m.memory is None and not any(n.startswith('memory.') for n,_ in m.named_parameters())
    b=m.vision; cap={}; samples=[]
    original=mod._sample_attention_st
    def sampled(p):
        a=original(p); samples.append(a); return a
    monkeypatch.setattr(mod,"_sample_attention_st",sampled)
    def capture(_, args, out): cap.update(x=args[0],h=args[1],z=out[0],a=out[2])
    hook=b.register_forward_hook(capture)
    state=m.init_state(2,'cpu',torch.float32)
    for tick in [False,False,True]:
        x=torch.randn(2,8,4,4)
        r,state,stats=m.step(x,state,update_memory=tick,return_stats=True)
        assert torch.equal(state[0],cap['z']) and torch.equal(r,state[1])
        ax,ah=samples[-2:]
        for a in [ax,ah]:
            assert ((a==0)|(a==1)).all() and torch.equal(a.sum(-1),torch.ones_like(a[...,0]))
        tok=lambda x:x.flatten(2).transpose(1,2)
        expected=(ax@tok(b.V_X)+ah@tok(b.V_H)).transpose(1,2).reshape_as(r)
        torch.testing.assert_close(r,expected,rtol=0,atol=0)
        q,kx,kh=[tok(F.normalize(t,dim=1)) for t in [b.W_q(cap['x']),b.W_kx(cap['x']),b._keys_h(cap['h'])]]
        px,ph=[(q@k.transpose(-1,-2)*b.log_temperature.exp()).softmax(-1) for k in [kx,kh]]
        expected_entropy=sum(-(p*p.clamp_min(1e-12).log()).sum(-1).mean() for p in [px,ph])/2
        torch.testing.assert_close(b.attention_entropy,expected_entropy)
    hook.remove()
    (r.square().mean()-1e-6*b.attention_entropy).backward()
    for p in [b.W_q.weight,b.W_kx.weight,b.W_kh.weight,b.log_temperature,b.V_X,b.V_H]:
        assert p.grad is not None and torch.isfinite(p.grad).all() and p.grad.abs().sum()>0
    m.forward_seq(torch.randn(2,7,16,16,3))
    assert m.attention_entropy_count==7
    assert m.attention_entropy.requires_grad
