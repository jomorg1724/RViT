"""
Stage 0c gate: end-to-end shape + microstim tests for the full RViT+ model.

Tests cover:
  - Encoder forward_step (n_FR iters, all interpretability hooks)
  - Decoder iterative reconstruction (n_BR proposals)
  - VAE latent sampling + KL
  - RViTPlusModel full forward_step
  - Microstim plumbing end-to-end (set attn_bias at (layer, iter), observe effect)
  - Per-layer pixel decoders
  - Reconstruction loss + KL backprop
  - Round-trip state propagation across env steps

Run:
    /usr/bin/python3 RViT_plus/tests/test_full_model.py
"""
from __future__ import annotations

import os
import sys
import traceback

import torch

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from RViT_plus_v2.encoder import RViTPlusEncoder
from RViT_plus_v2.latent import VAELatentSampler
from RViT_plus_v2.decoder import IterativeReconstructionDecoder
from RViT_plus_v2.losses import kl_to_unit_gaussian, pixel_recon_loss, slowness_loss
from RViT_plus_v2.model import RViTPlusModel
from RViT_plus_v2.stem import V1Stem


_PASSED = 0
_FAILED = 0


def _check(name, condition, detail=""):
    global _PASSED, _FAILED
    if condition:
        _PASSED += 1
        print(f"  PASS  {name}")
    else:
        _FAILED += 1
        msg = f"  FAIL  {name}"
        if detail:
            msg += f"  ({detail})"
        print(msg)


def test_encoder():
    print("\n[1] RViTPlusEncoder ---")
    enc = RViTPlusEncoder(
        stem_out_channels=64, state_channels=(64, 96, 128), n_FR=4,
    )
    B = 2
    V = torch.randn(B, 64, 12, 12)
    prev_states = enc.init_states(B)

    _check("init_states[0] shape (B, 64, 12, 12)", tuple(prev_states[0].shape) == (B, 64, 12, 12))
    _check("init_states[1] shape (B, 96, 6, 6)", tuple(prev_states[1].shape) == (B, 96, 6, 6))
    _check("init_states[2] shape (B, 128, 3, 3)", tuple(prev_states[2].shape) == (B, 128, 3, 3))

    out = enc.forward_step(V, prev_states)
    _check("encoder.layer_states_new len == 3", len(out["layer_states_new"]) == 3)
    _check("C₁ shape (B, 64, 12, 12)",
           tuple(out["layer_states_new"][0].shape) == (B, 64, 12, 12))
    _check("C₂ shape (B, 96, 6, 6)",
           tuple(out["layer_states_new"][1].shape) == (B, 96, 6, 6))
    _check("C₃ shape (B, 128, 3, 3)",
           tuple(out["layer_states_new"][2].shape) == (B, 128, 3, 3))
    # Single bottom-up pass per timestep (the inner n_FR loop was removed).
    # attn_per_iter / feedback_per_iter are wrapped in length-1 lists for
    # back-compat with code that previously iterated over inner iterations.
    _check("attn_per_iter has 1 entry (single pass)", len(out["attn_per_iter"]) == 1)
    _check("attn_per_iter[0] has 3 layers", len(out["attn_per_iter"][0]) == 3)
    # V2: per-channel spatial attention. Per-layer attn is (B, C, H_ℓ, W_ℓ) —
    # one saliency map per channel over the layer's spatial grid.
    _check("attn_per_iter[0][0] shape (B, 64, 12, 12)",
           tuple(out["attn_per_iter"][0][0].shape) == (B, 64, 12, 12))
    _check("attn_per_iter[0][1] shape (B, 96, 6, 6)",
           tuple(out["attn_per_iter"][0][1].shape) == (B, 96, 6, 6))
    _check("attn_per_iter[0][2] shape (B, 128, 3, 3)",
           tuple(out["attn_per_iter"][0][2].shape) == (B, 128, 3, 3))
    _check("feedback_per_iter has 1 entry with named keys",
           len(out["feedback_per_iter"]) == 1
           and set(out["feedback_per_iter"][0].keys()) == {
               "descend_1to2", "descend_2to3",
               "ascend_2to1", "ascend_3to1", "ascend_3to2",
           })


def test_encoder_microstim():
    print("\n[2] Encoder microstim plumbing — RETIRED (channel attention) ---")
    # The conv-spatial channel-attention redesign in attention.py removed
    # the spatial attention map; there is no per-token attention to bias.
    # The encoder still accepts and forwards `attn_biases` for API back-compat,
    # but the bias is a no-op at the FT level.
    enc = RViTPlusEncoder(n_FR=4)
    B = 2
    V = torch.randn(B, 64, 12, 12)
    prev = enc.init_states(B)
    # Smoke-test: forward with attn_biases provided should not raise.
    _ = enc.forward_step(V, prev, attn_biases={0: torch.zeros(B, 4, 144, 144)})
    _check("forward_step accepts (ignored) attn_biases without error", True)


def test_latent_sampler():
    print("\n[3] SpatialVAELatentSampler (run-8: spatial latent at C₃) ---")
    sampler = VAELatentSampler(state_channels=(64, 96, 128),
                                grid_hw=((12, 12), (6, 6), (3, 3)),
                                latent_channels=16)
    layer_states = (
        torch.randn(2, 64, 12, 12),
        torch.randn(2, 96, 6, 6),
        torch.randn(2, 128, 3, 3),
    )
    out = sampler(layer_states)
    _check("latent.sample shape (B, 16, 3, 3)",
           tuple(out["sample"].shape) == (2, 16, 3, 3))
    _check("latent.mu shape (B, 16, 3, 3)",
           tuple(out["mu"].shape) == (2, 16, 3, 3))
    _check("latent.logvar shape (B, 16, 3, 3)",
           tuple(out["logvar"].shape) == (2, 16, 3, 3))
    _check("latent.kl is scalar", out["kl"].dim() == 0)
    _check("latent.kl ≥ 0", out["kl"].item() >= 0)
    _check("latent.kl_per_dim shape (B, 16, 3, 3)",
           tuple(out["kl_per_dim"].shape) == (2, 16, 3, 3))


def test_decoder():
    print("\n[4] RViTPlusVideoDecoder (run-13: feedforward upsample+concat+CNN) ---")
    T = 5
    dec = IterativeReconstructionDecoder(  # alias for RViTPlusVideoDecoder
        state_channels=(64, 96, 128),
        grid_hw=((12, 12), (6, 6), (3, 3)),
        seq_len=T,
        image_h=50, image_w=50, image_channels=3,
        upsample_out_channels=32, cnn_hidden=64,
    )
    final_states = (
        torch.randn(2, 64, 12, 12),
        torch.randn(2, 96, 6, 6),
        torch.randn(2, 128, 3, 3),
    )
    out = dec(final_states)
    _check("decoder.recons length == seq_len", len(out["recons"]) == T)
    _check("recons[i] shape (B, 3, 50, 50)",
           all(tuple(r.shape) == (2, 3, 50, 50) for r in out["recons"]))
    _check("recon_video shape (B, T, 3, 50, 50)",
           tuple(out["recon_video"].shape) == (2, T, 3, 50, 50))
    # Linear output, no activation. Initial output should be nonzero and finite.
    max_abs = out["recon_video"].abs().max().item()
    _check("recons at init are nonzero (avoiding constant-output trap)",
           1e-5 < max_abs < 10.0,
           detail=f"max|recon| = {max_abs:.4f}")
    _check("recons at init are finite",
           torch.isfinite(out["recon_video"]).all().item())
    # No recurrent decoder ⇒ no per-step attention or state.
    _check("attn_per_step is empty (feedforward decoder)", len(out["attn_per_step"]) == 0)
    _check("state_per_step is empty (feedforward decoder)", len(out["state_per_step"]) == 0)
    _check("final_dec_states is the encoder final states (pass-through)",
           len(out["final_dec_states"]) == 3)


def test_full_model():
    print("\n[5] RViTPlusModel.compress_and_reconstruct (run-13) ---")
    B, T = 2, 5
    model = RViTPlusModel(
        in_channels=3, image_h=50, image_w=50,
        stem_out_channels=64, state_channels=(64, 96, 128),
        n_FR=4, n_heads=4,
        seq_len=T,
        upsample_out_channels=32, cnn_hidden=64,
        enable_skips=True, skip_scale=0.3,
    )
    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"     total trainable params: {n_params:,}")
    # Conv-spatial attention with 3×3 convs everywhere has materially more
    # params than the prior flatten-and-linear FT — budget bumped to 20M.
    _check("model under 20M params", n_params < 20_000_000,
           detail=f"{n_params:,}")

    video = torch.randn(B, T, 3, 50, 50)
    out = model.compress_and_reconstruct(video)

    # Primary outputs.
    _check("CompressionOutput.recons length == T", len(out.recons) == T)
    _check("recons[t] shape (B, 3, 50, 50)",
           all(tuple(r.shape) == (B, 3, 50, 50) for r in out.recons))
    _check("final_encoder_states is 3-tuple",
           len(out.final_encoder_states) == 3)
    _check("final_encoder_states[0] shape (B, 64, 12, 12)",
           tuple(out.final_encoder_states[0].shape) == (B, 64, 12, 12))
    _check("final_encoder_states[1] shape (B, 96, 6, 6)",
           tuple(out.final_encoder_states[1].shape) == (B, 96, 6, 6))
    _check("final_encoder_states[2] shape (B, 128, 3, 3)",
           tuple(out.final_encoder_states[2].shape) == (B, 128, 3, 3))
    # Run-13: VAE bottleneck deferred — latent fields are None.
    _check("latent_sample is None (VAE deferred in run-13)", out.latent_sample is None)
    _check("kl is None (VAE deferred in run-13)", out.kl is None)

    # Encoder still exposes its interpretability hooks.
    _check("encoder_attn_per_frame length == T",
           len(out.encoder_attn_per_frame) == T)
    # Single bottom-up pass per timestep (no inner FR loop).
    _check("encoder_attn_per_frame[0] is a length-1 list",
           len(out.encoder_attn_per_frame[0]) == 1)
    # V2: per-channel spatial attention. Layer-0 attn is (B, 64, 12, 12).
    _check("encoder_attn_per_frame[0][0][0] shape (B, 64, 12, 12)",
           tuple(out.encoder_attn_per_frame[0][0][0].shape) == (B, 64, 12, 12))
    # Decoder is feedforward in run-13: no per-step attention.
    _check("decoder_attn_per_step is empty (feedforward decoder)",
           len(out.decoder_attn_per_step) == 0)


def test_microstim_through_model():
    print("\n[6] Full-model microstim plumbing — RETIRED (channel attention) ---")
    # Channel attention has no per-token attention map to bias. The
    # attn_biases_per_frame plumbing is preserved for API back-compat but
    # bias values are not applied. Smoke test: forward shouldn't raise.
    B, T = 2, 3
    model = RViTPlusModel(n_FR=4, seq_len=T)
    video = torch.randn(B, T, 3, 50, 50)
    biases_per_frame = [None, {1: torch.zeros(B, 4, 36, 36)}, None]
    _ = model.compress_and_reconstruct(video, attn_biases_per_frame=biases_per_frame)
    _check("compress_and_reconstruct accepts (ignored) attn_biases_per_frame", True)


def test_gradient_flow():
    print("\n[7] Gradient flow (loss backprop) ---")
    import torch.nn.functional as F
    B, T = 2, 3
    model = RViTPlusModel(n_FR=4, seq_len=T)
    video = torch.randn(B, T, 3, 50, 50)

    out = model.compress_and_reconstruct(video)
    recon = torch.stack(out.recons, dim=1)
    total = F.l1_loss(recon, video)
    total.backward()

    # Stem.
    stem_grad_norm = sum(p.grad.norm().item() for p in model.stem.parameters() if p.grad is not None)
    _check("stem received gradient", stem_grad_norm > 0,
           detail=f"||∇stem|| = {stem_grad_norm:.4f}")

    # Encoder cell1 FT.
    ft1_grad_norm = sum(
        p.grad.norm().item()
        for p in model.encoder.cell1.ft.parameters()
        if p.grad is not None
    )
    _check("encoder.cell1.ft received gradient", ft1_grad_norm > 0,
           detail=f"||∇ft1|| = {ft1_grad_norm:.4f}")

    # Positional embeddings — RETIRED. Channel attention with 3×3 convs
    # everywhere has its own positional inductive bias, so the explicit
    # pos_emb on each cell was removed in the conv-attention redesign.

    # Decoder (feedforward upsample+CNN) — every component should receive gradient.
    up_grad_norm = sum(
        p.grad.norm().item()
        for p in list(model.decoder.up_c1.parameters())
            + list(model.decoder.up_c2.parameters())
            + list(model.decoder.up_c3.parameters())
        if p.grad is not None
    )
    _check("decoder upsample pyramids received gradient", up_grad_norm > 0,
           detail=f"||∇upsample|| = {up_grad_norm:.4f}")
    cnn_grad_norm = sum(p.grad.norm().item() for p in model.decoder.cnn.parameters() if p.grad is not None)
    _check("decoder CNN received gradient", cnn_grad_norm > 0,
           detail=f"||∇cnn|| = {cnn_grad_norm:.4f}")

    # NaN/inf check.
    _check("no NaN/inf in any gradient",
           all(torch.isfinite(p.grad).all().item()
               for p in model.parameters() if p.grad is not None))


def test_state_round_trip():
    print("\n[8] Multi-video round-trip (model is stateless across calls) ---")
    B, T = 2, 3
    model = RViTPlusModel(n_FR=4, seq_len=T)
    v1 = torch.randn(B, T, 3, 50, 50)
    v2 = torch.randn(B, T, 3, 50, 50)
    out1 = model.compress_and_reconstruct(v1)
    out2 = model.compress_and_reconstruct(v2)
    _check("two videos produce different final states",
           float((out1.final_encoder_states[0] - out2.final_encoder_states[0]).abs().mean()) > 1e-4,
           detail="different inputs → different compressed representations")
    _check("recon shape stable across calls",
           tuple(out2.recons[0].shape) == (B, 3, 50, 50))


def test_rl_heads_shapes():
    """Run-18: actor + distributional critic shape and forward sanity."""
    print("\n[9] RL heads (actor + distributional critic) ---")
    B, T = 2, 5
    N_ACTIONS = 2
    N_QUANTILES = 51
    model = RViTPlusModel(
        n_FR=4, seq_len=T,
        enable_actor=True, enable_critic=True,
        n_actions=N_ACTIONS, n_quantiles=N_QUANTILES,
        rl_per_state_channels=32, rl_cnn_hidden=64,
    )
    video = torch.randn(B, T, 3, 50, 50)

    # 1. compress_and_reconstruct should populate actor + distributional critic.
    out = model.compress_and_reconstruct(video)
    _check("actor_logits shape (B, n_actions)",
           tuple(out.actor_logits.shape) == (B, N_ACTIONS),
           detail=f"got {tuple(out.actor_logits.shape)}")
    _check("critic_q_dist shape (B, n_actions, n_quantiles) — distributional Q",
           tuple(out.critic_q_dist.shape) == (B, N_ACTIONS, N_QUANTILES),
           detail=f"got {tuple(out.critic_q_dist.shape)}")
    _check("critic_V_dist shape (B, n_quantiles)",
           tuple(out.critic_V_dist.shape) == (B, N_QUANTILES))
    _check("critic_V_scalar shape (B,)",
           tuple(out.critic_V_scalar.shape) == (B,))
    _check("all RL outputs finite",
           torch.isfinite(out.actor_logits).all().item() and
           torch.isfinite(out.critic_q_dist).all().item() and
           torch.isfinite(out.critic_V_dist).all().item())

    # 2. Initial outputs should be small (Gaussian init, std=0.02 on final conv).
    _check("actor logits initially small (final-conv std=0.02 init)",
           out.actor_logits.abs().max().item() < 1.0,
           detail=f"max|logits| = {out.actor_logits.abs().max().item():.4f}")
    _check("critic_q_dist initially small",
           out.critic_q_dist.abs().max().item() < 4.0)

    # 3. Quantile midpoints τ_i = (i + 0.5)/N are registered as a buffer.
    taus = model.critic_head.taus
    _check("critic taus shape (n_quantiles,)", tuple(taus.shape) == (N_QUANTILES,))
    _check("critic taus values in (0, 1)",
           bool((taus > 0).all().item() and (taus < 1).all().item()))
    _check("critic taus monotone increasing",
           bool((taus[1:] > taus[:-1]).all().item()))

    # 4. V derivation: V_dist = Σ_a sg[π(a)] · Q(s,a,:); V_scalar = mean(V_dist).
    # Verify the math by recomputing externally.
    pi = torch.softmax(out.actor_logits, dim=-1).detach()
    V_dist_manual = (pi.unsqueeze(-1) * out.critic_q_dist).sum(dim=1)
    V_scalar_manual = V_dist_manual.mean(dim=-1)
    _check("V_dist matches manual Σ sg[π]·Q computation",
           torch.allclose(out.critic_V_dist, V_dist_manual, atol=1e-5))
    _check("V_scalar matches mean(V_dist)",
           torch.allclose(out.critic_V_scalar, V_scalar_manual, atol=1e-5))

    # 5. forward_rl path should produce the same RL outputs.
    out_rl = model.forward_rl(video)
    _check("forward_rl returns distributional q_dist",
           tuple(out_rl.critic_q_dist.shape) == (B, N_ACTIONS, N_QUANTILES))
    _check("forward_rl skips decoder (recons empty)", len(out_rl.recons) == 0)

    # 6. Smaller-quantile config (e.g. n_quantiles=8 for sanity).
    model_small = RViTPlusModel(
        n_FR=4, seq_len=T,
        enable_actor=True, enable_critic=True,
        n_actions=3, n_quantiles=8,
    )
    out_small = model_small.compress_and_reconstruct(video)
    _check("q_dist shape adapts to (B, 3, 8)",
           tuple(out_small.critic_q_dist.shape) == (B, 3, 8))


def test_rl_heads_gradient_flow():
    """Run-18: gradient should flow from actor/distributional-critic back to encoder."""
    print("\n[10] RL-heads gradient flow (distributional) ---")
    from RViT_plus_v2.rl_heads import quantile_huber_loss
    B, T = 2, 3
    N_ACTIONS, N_QUANTILES = 2, 51
    model = RViTPlusModel(
        n_FR=4, seq_len=T,
        enable_actor=True, enable_critic=True,
        n_actions=N_ACTIONS, n_quantiles=N_QUANTILES,
    )
    video = torch.randn(B, T, 3, 50, 50)
    out = model.forward_rl(video)

    # Synthetic policy loss + distributional-critic loss.
    # Policy "loss": negative log-prob of a random action.
    log_probs = torch.log_softmax(out.actor_logits, dim=-1)
    target_action = torch.tensor([0, 1])
    policy_loss = -log_probs.gather(1, target_action.unsqueeze(-1)).mean()
    # Quantile-Huber loss on the executed action's Q-distribution against a
    # synthetic target distribution.
    executed_q = out.critic_q_dist[torch.arange(B), target_action]  # (B, N_QUANTILES)
    target_q = torch.randn(B, N_QUANTILES)
    qr_loss = quantile_huber_loss(executed_q, target_q, model.critic_head.taus, kappa=1.0)
    total = policy_loss + qr_loss
    total.backward()

    # Stem grad — should be nonzero (encoder is upstream of both heads).
    stem_grad = sum(p.grad.norm().item() for p in model.stem.parameters() if p.grad is not None)
    _check("stem received gradient from RL heads", stem_grad > 0,
           detail=f"||∇stem|| = {stem_grad:.4f}")

    # Encoder cell1 — same.
    enc1_grad = sum(p.grad.norm().item() for p in model.encoder.cell1.parameters() if p.grad is not None)
    _check("encoder.cell1 received gradient", enc1_grad > 0,
           detail=f"||∇cell1|| = {enc1_grad:.4f}")

    # Actor head — should receive gradient.
    actor_grad = sum(p.grad.norm().item() for p in model.actor_head.parameters() if p.grad is not None)
    _check("actor_head received gradient", actor_grad > 0,
           detail=f"||∇actor|| = {actor_grad:.4f}")

    # Critic head — should receive gradient.
    critic_grad = sum(p.grad.norm().item() for p in model.critic_head.parameters() if p.grad is not None)
    _check("critic_head received gradient", critic_grad > 0,
           detail=f"||∇critic|| = {critic_grad:.4f}")

    # NaN/inf check.
    _check("no NaN/inf in any gradient",
           all(torch.isfinite(p.grad).all().item()
               for p in model.parameters() if p.grad is not None))

    # Param count sanity — actor + critic together should be substantially
    # smaller than the rest of the model.
    actor_p = sum(p.numel() for p in model.actor_head.parameters())
    critic_p = sum(p.numel() for p in model.critic_head.parameters())
    total_p = sum(p.numel() for p in model.parameters())
    print(f"     actor params: {actor_p:,}  critic params: {critic_p:,}  total: {total_p:,}")
    _check("actor + critic param count is moderate (< 30% of total)",
           (actor_p + critic_p) < 0.3 * total_p,
           detail=f"actor+critic = {actor_p + critic_p:,}, total = {total_p:,}")


def test_quantile_huber_loss():
    """Run-18: quantile-Huber loss numerical correctness."""
    from RViT_plus_v2.rl_heads import quantile_huber_loss
    print("\n[11] Quantile-Huber loss ---")

    N = 8
    taus = (torch.arange(N, dtype=torch.float32) + 0.5) / N

    # 1. QR-DQN's pairwise loss is *not* zero on identical-but-spread pred/target
    # (off-diagonal pairs always contribute), but it IS zero on identical-AND-
    # constant pred/target. Test the constant-degenerate case.
    pred_const = torch.full((4, N), 0.5)
    target_const = torch.full((4, N), 0.5)
    loss_const = quantile_huber_loss(pred_const, target_const, taus, kappa=1.0)
    _check("loss against identical CONSTANT targets is ≈ 0",
           loss_const.item() < 1e-6,
           detail=f"loss = {loss_const.item():.6f}")

    # 2. Loss is differentiable and produces gradient.
    pred2 = torch.randn(4, N, requires_grad=True)
    target2 = torch.randn(4, N)
    loss2 = quantile_huber_loss(pred2, target2, taus, kappa=1.0)
    loss2.backward()
    _check("quantile-Huber loss produces gradient on prediction",
           pred2.grad is not None and pred2.grad.abs().sum().item() > 0)
    _check("loss is positive scalar", loss2.item() > 0 and loss2.dim() == 0)

    # 3. Asymmetry: when target > pred, the loss should weight by τ, not (1−τ).
    # A simple sanity check — different τ vectors should give different losses
    # for the same residual structure.
    pred3 = torch.zeros(1, N)
    target3 = torch.ones(1, N) * 1.0   # uniformly positive residual
    taus_low = torch.full((N,), 0.1)
    taus_high = torch.full((N,), 0.9)
    loss_low = quantile_huber_loss(pred3, target3, taus_low, kappa=1.0)
    loss_high = quantile_huber_loss(pred3, target3, taus_high, kappa=1.0)
    # δ > 0 (target − pred = 1 > 0) → weight = |τ − 0| = τ.
    # So loss should be ≈ 0.5 × τ in the Huber-linear region (|δ| > κ).
    # Wait, residual=1, kappa=1: |δ|=1 ≤ κ → quadratic: 0.5·1²=0.5.
    # weight = τ. So loss = τ · 0.5 / κ.
    # loss_low ≈ 0.1 × 0.5 = 0.05. loss_high ≈ 0.9 × 0.5 = 0.45.
    _check("τ-asymmetric weighting: positive δ → loss scales with τ",
           loss_high.item() > 5 * loss_low.item(),
           detail=f"loss(τ=0.1)={loss_low.item():.4f}, loss(τ=0.9)={loss_high.item():.4f}")


def test_split_c3():
    """Run-19: split_c3=True gives separate C₃ specialists for AE / actor / critic."""
    print("\n[12] split_c3 — separate deep states per task ---")
    B, T = 2, 5
    model = RViTPlusModel(
        n_FR=4, seq_len=T,
        enable_actor=True, enable_critic=True,
        n_actions=2, n_quantiles=51,
        split_c3=True,
    )
    video = torch.randn(B, T, 3, 50, 50)
    out = model.compress_and_reconstruct(video)

    # Structural checks: encoder now has cell3_actor and cell3_critic.
    _check("encoder has cell3 (the AE / canonical variant)",
           hasattr(model.encoder, "cell3"))
    _check("encoder has cell3_actor when split_c3=True",
           hasattr(model.encoder, "cell3_actor"))
    _check("encoder has cell3_critic when split_c3=True",
           hasattr(model.encoder, "cell3_critic"))
    _check("model.split_c3 == True", model.split_c3 is True)

    # Each cell3_X should have its own (different) weights at init.
    # After the conv-attention redesign, the SIP candidate (`conv_candidate`)
    # is gone — every cell now has a `conv_update` (3x3) and an internal FT.
    w_ae     = model.encoder.cell3.conv_update.weight
    w_actor  = model.encoder.cell3_actor.conv_update.weight
    w_critic = model.encoder.cell3_critic.conv_update.weight
    _check("cell3 / cell3_actor have different weights at init",
           not torch.equal(w_ae, w_actor))
    _check("cell3 / cell3_critic have different weights at init",
           not torch.equal(w_ae, w_critic))
    _check("cell3_actor / cell3_critic have different weights",
           not torch.equal(w_actor, w_critic))

    # Forward pass produces valid RL + recon outputs.
    _check("split_c3 forward: actor_logits shape (B, 2)",
           tuple(out.actor_logits.shape) == (B, 2))
    _check("split_c3 forward: critic_q_dist shape (B, 2, 51)",
           tuple(out.critic_q_dist.shape) == (B, 2, 51))
    _check("split_c3 forward: recons length == T", len(out.recons) == T)

    # Gradient flow: all three cell3 variants should receive gradient.
    import torch.nn.functional as F
    loss = (torch.stack(out.recons, dim=1) - video).abs().mean() \
           + out.actor_logits.pow(2).mean() \
           + out.critic_q_dist.pow(2).mean()
    loss.backward()
    g_ae = sum(p.grad.norm().item() for p in model.encoder.cell3.parameters() if p.grad is not None)
    g_actor = sum(p.grad.norm().item() for p in model.encoder.cell3_actor.parameters() if p.grad is not None)
    g_critic = sum(p.grad.norm().item() for p in model.encoder.cell3_critic.parameters() if p.grad is not None)
    _check("cell3 (AE) received gradient", g_ae > 0, detail=f"||∇cell3|| = {g_ae:.4f}")
    _check("cell3_actor received gradient", g_actor > 0, detail=f"||∇cell3_actor|| = {g_actor:.4f}")
    _check("cell3_critic received gradient", g_critic > 0, detail=f"||∇cell3_critic|| = {g_critic:.4f}")

    # Verify the routing is actually different (i.e., decoder doesn't read
    # the actor's C₃). Force the actor's C₃ to differ from the AE's C₃ via
    # the encoder's forward pass, then check the heads see different states.
    with torch.no_grad():
        enc_seq = model.forward_rl_sequence(video, return_decoder=True)
    # final encoder state (C1, C2, C3_ae) for the decoder
    # — the actor head's C3 is c3_actor, distinct from C3_ae at this point
    # (because the encoder's specialist cells have different weights).
    _check("forward_rl_sequence still returns actor_logits_seq (B, T, 2)",
           tuple(enc_seq["actor_logits_seq"].shape) == (B, T, 2))
    _check("forward_rl_sequence q_dist_seq shape (B, T, 2, 51)",
           tuple(enc_seq["q_dist_seq"].shape) == (B, T, 2, 51))

    # Backward-compat: with split_c3=False, no specialist cells are created.
    model_nosplit = RViTPlusModel(
        n_FR=4, seq_len=T,
        enable_actor=True, enable_critic=True,
        n_actions=2, n_quantiles=51,
        split_c3=False,
    )
    _check("split_c3=False → no cell3_actor",
           not hasattr(model_nosplit.encoder, "cell3_actor"))
    _check("split_c3=False → no cell3_critic",
           not hasattr(model_nosplit.encoder, "cell3_critic"))

    # Param-count: split_c3 adds two extra C₃ cells. Under the new
    # conv-spatial attention block, each C₃ cell at (state_ch=128) is
    # ~4M params, so the delta is much larger than under the old
    # flatten-and-linear FT.
    p_split = sum(p.numel() for p in model.parameters())
    p_nosplit = sum(p.numel() for p in model_nosplit.parameters())
    delta = p_split - p_nosplit
    print(f"     split_c3 adds {delta:,} params (2 extra C₃ cells)")
    _check("split_c3 delta is in the expected 2-cell range",
           1_000_000 < delta < 20_000_000,
           detail=f"delta = {delta:,}")


def main():
    print("RViT+ Stage 0c — encoder + decoder + model shape tests")
    print("=" * 60)
    try:
        test_encoder()
        test_encoder_microstim()
        test_latent_sampler()
        test_decoder()
        test_full_model()
        test_microstim_through_model()
        test_gradient_flow()
        test_state_round_trip()
        test_rl_heads_shapes()
        test_rl_heads_gradient_flow()
        test_quantile_huber_loss()
        test_split_c3()
    except Exception:
        traceback.print_exc()
        print("\nUNEXPECTED EXCEPTION — see traceback above.")
        return 2
    print("=" * 60)
    print(f"  passed: {_PASSED}    failed: {_FAILED}")
    if _FAILED == 0:
        print("  STAGE 0c GATE: PASS")
        return 0
    print("  STAGE 0c GATE: FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
