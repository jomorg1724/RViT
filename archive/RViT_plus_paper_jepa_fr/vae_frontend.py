"""
VAE patch front-end — EXACTLY as specified in the paper (Model Architecture §VAE
Pre-Processing and §ViT).

Each 50x50 input frame is converted to grayscale and split into FOUR 25x25 patches
in the paper's order:  S1 (top-left), S2 (bottom-left), S3 (top-right), S4 (bottom-
right).  Each patch is run through the VAE encoder up to the SECOND flattened encoder
layer (o_flat,2, 128-d) — the paper feeds the ViT this layer, NOT the latent z:

    z_conv1 = ReLU(Conv(1→16, k3, s2, p1)(o_i))            # 25→13
    z_conv2 = ReLU(Conv(16→32, k3, s2, p1)(z_conv1))       # 13→7  → 7*7*32 = 1568
    o_flat2 = ReLU(W1 · flatten(z_conv2) + b1)             # 1568 → 128   == ô_i

The token is then  x_i = Concat[ô_i, ρ_i, τ]  (Eq 1):
    ρ_i = one-hot patch position (4)     τ = one-hot timestep (8)
    → 128 + 4 + 8 = 140  ⇒  X = (x_1,…,x_4)ᵀ ∈ ℝ^{4×140}   (Eq 2)

CHOICES (flagged; per the user's locked spec):
  • The VAE encoder is a TRAINABLE front-end, learned end-to-end with the RL objective
    (no separate pretrain, no reconstruction loss). Decoder is omitted.
  • The paper used C=1 grayscale; our env renders 3-channel RGB, so we average the
    channels to a single luminance channel before the paper's Conv(1→16). This keeps
    the encoder byte-faithful to the paper while accepting our env's frames.
"""
from __future__ import annotations

import torch
import torch.nn as nn

N_PATCH = 4
O_FLAT2 = 128                 # paper's second flattened encoder layer width
POS_DIM = 4                   # one-hot over the 4 patch positions
TEMP_DIM = 8                  # one-hot over timestep (T=7 task; 8 slots, t clamped)
TOKEN_DIM = O_FLAT2 + POS_DIM + TEMP_DIM   # = 140 (matches the paper's 4×140)


class VAEPatchFrontEnd(nn.Module):
    def __init__(self, in_channels: int = 1) -> None:
        super().__init__()
        # in_channels: 1 = GRAYSCALE front-end (averages RGB → luminance, paper-faithful, value-BLIND);
        #              3 = COLOUR front-end (keeps RGB, so the value cue red/green/blue is visible).
        self.in_channels = int(in_channels)
        # encoder components (1)–(4) — the path to o_flat,2 (paper §VAE Pre-Processing)
        self.conv1 = nn.Conv2d(self.in_channels, 16, kernel_size=3, stride=2, padding=1)   # 25→13
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1)  # 13→7
        self.fc1 = nn.Linear(7 * 7 * 32, O_FLAT2)                           # 1568 → 128
        self.n_tokens = N_PATCH
        self.token_dim = TOKEN_DIM
        self.frozen = False

    def load_pretrained(self, encoder_state: dict, freeze: bool = True):
        """Load conv1/conv2/fc1 from a pretrained PatchVAE; optionally freeze the front-end.
        GUARD: refuses a grayscale↔colour mismatch (the conv1 input-channel count must match)
        so a value-blind grayscale VAE can never be silently loaded into a colour run, or vice versa."""
        ck_ch = encoder_state["conv1.weight"].shape[1] if "conv1.weight" in encoder_state else self.in_channels
        if int(ck_ch) != self.in_channels:
            raise ValueError(
                f"VAE channel MISMATCH: checkpoint conv1 has in_channels={ck_ch} but the front-end "
                f"is in_channels={self.in_channels}. A {('grayscale' if ck_ch==1 else 'colour')} VAE "
                f"cannot load into a {('grayscale' if self.in_channels==1 else 'colour')} front-end. "
                f"Use the matching VAE (grayscale→paper_vae/vae.pt, colour→paper_vae_color/vae_color.pt) "
                f"and set --vae-color accordingly.")
        res = self.load_state_dict(encoder_state, strict=False)
        if freeze:
            for m in (self.conv1, self.conv2, self.fc1):
                for p in m.parameters():
                    p.requires_grad_(False)
            self.frozen = True
        return res

    def _encode_patch(self, o: torch.Tensor) -> torch.Tensor:
        """o: (B,C,25,25) → ô (B,128) = o_flat,2 (encoder components 1–4)."""
        z = torch.relu(self.conv1(o))
        z = torch.relu(self.conv2(z))
        z = z.flatten(1)
        return torch.relu(self.fc1(z))                                      # ô = o_flat,2

    def forward(self, x: torch.Tensor, t: int) -> torch.Tensor:
        """x: (B,3,50,50) RGB frame, t: integer timestep. Returns X: (B,4,140)."""
        B = x.shape[0]
        # GRAYSCALE front-end averages RGB → luminance (value-blind); COLOUR front-end keeps RGB.
        g = x.mean(dim=1, keepdim=True) if self.in_channels == 1 else x     # (B,1,50,50) or (B,3,50,50)
        # four 25×25 quadrants in the ENV's cell order [TL, TR, BL, BR] (rows outer,
        # cols inner) so the patch index matches cue_index / change_index. Paper S1/S4
        # (top-left / bottom-right) are indices 0 and 3.
        patches = [
            g[:, :, :25, :25], g[:, :, :25, 25:],
            g[:, :, 25:, :25], g[:, :, 25:, 25:],
        ]
        embs = [self._encode_patch(p) for p in patches]                     # 4 × (B,128)
        emb = torch.stack(embs, dim=1)                                      # (B,4,128)

        # one-hot positional ρ_i (per patch) and temporal τ (shared), Eq 1
        pos = torch.eye(POS_DIM, device=x.device, dtype=x.dtype).unsqueeze(0).expand(B, -1, -1)
        ti = max(0, min(int(t), TEMP_DIM - 1))
        tau = torch.zeros(B, N_PATCH, TEMP_DIM, device=x.device, dtype=x.dtype)
        tau[:, :, ti] = 1.0
        X = torch.cat([emb, pos, tau], dim=-1)                             # (B,4,140)
        return X
