"""
RViTPlusVideoDecoder — feedforward upsample-and-decode (run-13 redesign).

Architectural intent (user spec, 2026-05-21):

  *"First use conv transposes to bring every recurrent state up to the size of
   the input image. Then, concatenate them all along the channel dimension.
   Finally, use a moderate sized convolutional neural network to decode the
   concatenated memory states into the full video."*

Pipeline:

  1. Encoder produces final states C₁ : (B, c₁, h₁, w₁), C₂ : (B, c₂, h₂, w₂),
     C₃ : (B, c₃, h₃, w₃) — the compressed representation of the T-frame video.
  2. Each Cᵢ is upsampled via a stack of ConvTranspose2d layers to the input
     image resolution (50×50 here).
  3. The three upsampled feature maps are concatenated along the channel dim.
  4. A moderate-sized CNN decodes the concatenated tensor into all T frames
     simultaneously, producing (B, T·image_channels, H, W) → reshaped to
     (B, T, image_channels, H, W).
  5. Output is tanh-bounded to match the input pixel range [-1, 1].

No VAE bottleneck (deferred — passed directly through), no recurrent backwards-
unroll (deferred — replaced with a single feedforward pass), no temporal
embedding (the output channel partitioning IS the temporal index).

Stochastic latent and backwards-unroll are intentionally postponed per the
user's directive: *"Let's just skip the stochastic latent projection for now.
We will reintroduce this later if we get the autoencoder to work."*
"""
from __future__ import annotations

from typing import List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


_GN_GROUPS = 8


def _gn_groups(channels: int) -> int:
    for g in (8, 4, 2, 1):
        if channels % g == 0:
            return g
    return 1


def _convT_block(in_ch: int, out_ch: int,
                 kernel_size: int, stride: int, padding: int, output_padding: int = 0
                 ) -> nn.Sequential:
    """ConvTranspose2d + GroupNorm + GELU. Used for spatial upsampling."""
    return nn.Sequential(
        nn.ConvTranspose2d(in_ch, out_ch, kernel_size=kernel_size,
                           stride=stride, padding=padding, output_padding=output_padding),
        nn.GroupNorm(_gn_groups(out_ch), out_ch),
        nn.GELU(),
    )


class MemoryUpsamplePyramid(nn.Module):
    """Upsample one encoder memory state to the input resolution via stacked
    ConvTranspose2d layers, halving channels (roughly) at each step.

    Spatial trajectories (PyTorch H_out = (H_in−1)·s − 2p + k + op):
      C₁ : 12 → 25 → 50           via k=3,s=2,p=0,op=0  then  k=5,s=2,p=2,op=1
      C₂ :  6 → 12 → 25 → 50      via k=4,s=2,p=1,op=0  then  k=3,s=2,p=0,op=0  then  k=5,s=2,p=2,op=1
      C₃ :  3 → 6  → 12 → 25 → 50 via k=4,s=2,p=1,op=0  three times then k=5,s=2,p=2,op=1

    Channel trajectory: in_channels → out_channels, halving roughly each stage.
    """

    def __init__(self, in_channels: int, in_hw: Tuple[int, int], out_channels: int,
                 image_hw: Tuple[int, int] = (50, 50)) -> None:
        super().__init__()
        h_in, w_in = in_hw
        h_target, w_target = image_hw
        if h_in != w_in or h_target != w_target:
            raise NotImplementedError("MemoryUpsamplePyramid assumes square grids and targets")
        if h_target != 50:
            raise NotImplementedError("Pyramid is hardcoded for target=50; adjust for other sizes")

        # Build a stage list to reach 50 from h_in via doubling, with a final adjustment.
        # Map h_in (one of 3, 6, 12) to the stage chain.
        chain_specs = {
            3:  [(3, 6,   4, 2, 1, 0),    # k, s, p, op
                 (6, 12,  4, 2, 1, 0),
                 (12, 25, 3, 2, 0, 0),
                 (25, 50, 5, 2, 2, 1)],
            6:  [(6, 12,  4, 2, 1, 0),
                 (12, 25, 3, 2, 0, 0),
                 (25, 50, 5, 2, 2, 1)],
            12: [(12, 25, 3, 2, 0, 0),
                 (25, 50, 5, 2, 2, 1)],
        }
        if h_in not in chain_specs:
            raise NotImplementedError(f"Pyramid for h_in={h_in} not defined; supported {sorted(chain_specs)}")

        chain = chain_specs[h_in]
        n_stages = len(chain)
        # Linear-in-stage channel schedule: in_channels → out_channels.
        # For consistency, halve channels at the first stage, then taper to out_channels.
        # Concretely we use channels[0] = in_channels, channels[-1] = out_channels, geometric.
        channels = [in_channels]
        if n_stages == 1:
            channels.append(out_channels)
        else:
            ratio = (out_channels / in_channels) ** (1 / n_stages)
            for k in range(1, n_stages):
                ch_k = max(out_channels, int(round(in_channels * ratio**k)))
                # Round to nearest multiple of _GN_GROUPS for clean GN groups.
                ch_k = max(_GN_GROUPS, (ch_k // _GN_GROUPS) * _GN_GROUPS)
                channels.append(ch_k)
            channels.append(out_channels)

        # `chain` is one (in_size, out_size, k, s, p, op) per stage.
        # `channels` has n_stages+1 entries (in/out per stage).
        layers: List[nn.Module] = []
        for stage_idx, (h_in_s, h_out_s, k, s, p, op) in enumerate(chain):
            in_ch = channels[stage_idx]
            out_ch = channels[stage_idx + 1]
            layers.append(_convT_block(in_ch, out_ch,
                                       kernel_size=k, stride=s, padding=p, output_padding=op))
        self.layers = nn.Sequential(*layers)
        self.in_hw = in_hw
        self.image_hw = image_hw
        self.in_channels = in_channels
        self.out_channels = out_channels

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() != 4:
            raise ValueError(f"MemoryUpsamplePyramid expects 4D; got {tuple(x.shape)}")
        if x.shape[-2:] != self.in_hw:
            raise ValueError(f"input HW {tuple(x.shape[-2:])} != expected {self.in_hw}")
        out = self.layers(x)
        if out.shape[-2:] != self.image_hw:
            raise ValueError(f"output HW {tuple(out.shape[-2:])} != expected {self.image_hw}")
        return out


class RViTPlusVideoDecoder(nn.Module):
    """Feedforward decoder: encoder memory → upsample pyramid → concat → CNN → T frames.

    Args
    ----
    state_channels      : (c1, c2, c3) — encoder per-layer channel counts.
    grid_hw             : ((h1,w1),(h2,w2),(h3,w3)) — encoder per-layer spatial sizes.
    seq_len             : T, number of frames the decoder produces in one forward pass.
                          Must be known at construction (output channel count = seq_len * image_channels).
    image_h, image_w    : output frame resolution (default 50, 50).
    image_channels      : output channels per frame (default 3 RGB).
    upsample_out_channels: per-layer channel count after upsampling each memory
                           state to image resolution. Default 32 each → 96 total
                           concatenated, then decoded by the CNN.
    cnn_hidden          : CNN decoder hidden channel count. Default 64.
    """

    def __init__(
        self,
        state_channels: Tuple[int, int, int] = (64, 96, 128),
        grid_hw: Tuple[Tuple[int, int], ...] = ((12, 12), (6, 6), (3, 3)),
        seq_len: int = 10,
        image_h: int = 50,
        image_w: int = 50,
        image_channels: int = 3,
        upsample_out_channels: int = 32,
        cnn_hidden: int = 64,
    ) -> None:
        super().__init__()
        c1, c2, c3 = state_channels
        self.state_channels = state_channels
        self.grid_hw = grid_hw
        self.seq_len = seq_len
        self.image_h, self.image_w = image_h, image_w
        self.image_channels = image_channels
        self.upsample_out_channels = upsample_out_channels
        self.cnn_hidden = cnn_hidden

        # ── Per-layer upsample pyramids (Cᵢ → (B, upsample_out_channels, 50, 50)) ──
        self.up_c1 = MemoryUpsamplePyramid(in_channels=c1, in_hw=grid_hw[0],
                                            out_channels=upsample_out_channels,
                                            image_hw=(image_h, image_w))
        self.up_c2 = MemoryUpsamplePyramid(in_channels=c2, in_hw=grid_hw[1],
                                            out_channels=upsample_out_channels,
                                            image_hw=(image_h, image_w))
        self.up_c3 = MemoryUpsamplePyramid(in_channels=c3, in_hw=grid_hw[2],
                                            out_channels=upsample_out_channels,
                                            image_hw=(image_h, image_w))

        # ── CNN decoder ────────────────────────────────────────────────────
        # Input: (B, 3 * upsample_out_channels, 50, 50) = (B, 96, 50, 50) default
        # Output: (B, seq_len * image_channels, 50, 50)
        concat_channels = 3 * upsample_out_channels
        out_channels = seq_len * image_channels

        self.cnn = nn.Sequential(
            nn.Conv2d(concat_channels, cnn_hidden, kernel_size=3, padding=1),
            nn.GroupNorm(_gn_groups(cnn_hidden), cnn_hidden), nn.GELU(),
            nn.Conv2d(cnn_hidden, cnn_hidden, kernel_size=3, padding=1),
            nn.GroupNorm(_gn_groups(cnn_hidden), cnn_hidden), nn.GELU(),
            nn.Conv2d(cnn_hidden, cnn_hidden // 2, kernel_size=3, padding=1),
            nn.GroupNorm(_gn_groups(cnn_hidden // 2), cnn_hidden // 2), nn.GELU(),
            nn.Conv2d(cnn_hidden // 2, out_channels, kernel_size=1),
        )

        # Init final conv with small Gaussian so initial recons are subtle
        # (not zero — to avoid the trivial-constant attractor) and the tanh
        # in forward() will keep them in [-1, 1].
        final_conv = self.cnn[-1]
        nn.init.normal_(final_conv.weight, mean=0.0, std=0.02)
        nn.init.zeros_(final_conv.bias)

    def forward(self, final_states: Tuple[torch.Tensor, torch.Tensor, torch.Tensor]) -> dict:
        """Decode the full video from the encoder's final memory states.

        Args
        ----
        final_states : tuple (C₁, C₂, C₃) from the encoder. No latent sample —
                       the bottleneck IS the encoder's final memory.

        Returns dict with:
            recons    : list of `seq_len` tensors of shape (B, 3, H, W),
                        in source-time order (recons[t] = predicted frame t).
            recon_video: stacked (B, T, 3, H, W) for convenience.
        """
        C1, C2, C3 = final_states
        if C1.shape[-2:] != self.grid_hw[0]:
            raise ValueError(f"C1 HW {tuple(C1.shape[-2:])} != expected {self.grid_hw[0]}")
        if C2.shape[-2:] != self.grid_hw[1]:
            raise ValueError(f"C2 HW {tuple(C2.shape[-2:])} != expected {self.grid_hw[1]}")
        if C3.shape[-2:] != self.grid_hw[2]:
            raise ValueError(f"C3 HW {tuple(C3.shape[-2:])} != expected {self.grid_hw[2]}")

        # Upsample each memory state to image resolution.
        u1 = self.up_c1(C1)   # (B, upsample_out_channels, H, W)
        u2 = self.up_c2(C2)
        u3 = self.up_c3(C3)

        # Concatenate along the channel dim.
        cat = torch.cat([u1, u2, u3], dim=1)   # (B, 3*upsample_out_channels, H, W)

        # CNN decode to (B, T*3, H, W) → reshape → (B, T, 3, H, W).
        # No output activation. Run-12/13 used tanh to match the input range
        # [-1, 1], but the saturation killed the gradient: when pre-activation
        # was strongly negative (matching the bg=-1 majority), tanh's derivative
        # 1−tanh²(x) collapsed to ~0.004, the gradient damped 250×, and the
        # model locked into saturation. Linear output has constant L1 gradient
        # magnitude (sign of the error) regardless of how close to the target
        # — no saturation trap. Outputs may occasionally exceed [-1, 1]; L1
        # penalizes that the same as any other mismatch.
        B = cat.shape[0]
        out = self.cnn(cat)                    # (B, T*3, H, W)
        recon_video = out.view(B, self.seq_len, self.image_channels, self.image_h, self.image_w)

        # Return as a list of T tensors (source-time order) for back-compat
        # with analysis and loss code that consumes `recons` as a list.
        recons = [recon_video[:, t] for t in range(self.seq_len)]

        return {
            "recons": recons,
            "recon_video": recon_video,
            # Retained for back-compat with analysis scripts (None now that
            # there's no recurrent decoder dynamic and no per-step attention).
            "attn_per_step": [],
            "state_per_step": [],
            "final_dec_states": final_states,
        }


# Back-compat alias.
IterativeReconstructionDecoder = RViTPlusVideoDecoder
