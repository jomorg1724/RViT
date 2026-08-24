"""
The paper's exact patch VAE (Model Architecture §VAE Pre-Processing), used to
PRETRAIN a feed-forward visual front-end before RL. The encoder path to the second
flattened layer (o_flat,2, 128-d) is what the ViT reads; pretraining on reconstruction
forces o_flat,2 to be an orientation-informative representation that sparse RL reward
would never teach on its own.

Encoder (components 1–4 + latent params):
    z_conv1 = ReLU(Conv(1→16, k3, s2, p1))        25→13
    z_conv2 = ReLU(Conv(16→32, k3, s2, p1))       13→7  → 7·7·32 = 1568
    o_flat2 = ReLU(W1·flatten + b1)               1568 → 128      == ô (fed to the ViT)
    z_mu, z_logvar = Linear(128→d_latent)
Reparam: z = μ + σ⊙ε.   Decoder mirrors with transposed convs → Sigmoid (25×25).
Loss: (1/d_image)‖o−ô‖² − β·½(1+logσ²−μ²−σ²).

The encoder modules are named conv1/conv2/fc1 to MATCH VAEPatchFrontEnd, so the
pretrained weights load straight into the RL model's front-end.
"""
from __future__ import annotations

import torch
import torch.nn as nn


class PatchVAE(nn.Module):
    def __init__(self, d_latent: int = 32, in_channels: int = 1) -> None:
        super().__init__()
        self.in_channels = int(in_channels)        # 1 = GRAYSCALE VAE; 3 = COLOUR VAE (sees the value cue)
        # encoder (names match VAEPatchFrontEnd: conv1, conv2, fc1 → o_flat,2)
        self.conv1 = nn.Conv2d(self.in_channels, 16, kernel_size=3, stride=2, padding=1)   # 25→13
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1)   # 13→7
        self.fc1 = nn.Linear(7 * 7 * 32, 128)                                # → o_flat,2
        self.fc_mu = nn.Linear(128, d_latent)
        self.fc_logvar = nn.Linear(128, d_latent)
        # decoder
        self.dec_fc1 = nn.Linear(d_latent, 128)
        self.dec_fc2 = nn.Linear(128, 7 * 7 * 32)
        self.deconv1 = nn.ConvTranspose2d(32, 16, kernel_size=3, stride=2, padding=1, output_padding=0)  # 7→13
        self.deconv2 = nn.ConvTranspose2d(16, self.in_channels, kernel_size=3, stride=2, padding=1, output_padding=0)  # 13→25

    def encode(self, o: torch.Tensor):
        z = torch.relu(self.conv1(o))
        z = torch.relu(self.conv2(z))
        o_flat2 = torch.relu(self.fc1(z.flatten(1)))             # 128-d (what the ViT reads)
        return o_flat2, self.fc_mu(o_flat2), self.fc_logvar(o_flat2)

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        h = torch.relu(self.dec_fc1(z))
        h = torch.relu(self.dec_fc2(h)).view(-1, 32, 7, 7)
        h = torch.relu(self.deconv1(h))
        return torch.sigmoid(self.deconv2(h))                    # (B,1,25,25) in [0,1]

    def forward(self, o: torch.Tensor):
        o_flat2, mu, logvar = self.encode(o)
        z = mu + torch.exp(0.5 * logvar) * torch.randn_like(logvar)
        return self.decode(z), mu, logvar, o_flat2

    @staticmethod
    def loss(o: torch.Tensor, recon: torch.Tensor, mu: torch.Tensor, logvar: torch.Tensor,
             beta: float = 1e-3):
        d_image = o.shape[1] * o.shape[2] * o.shape[3]
        recon_l = ((o - recon) ** 2).sum(dim=(1, 2, 3)).mean() / d_image
        kl = -0.5 * (1 + logvar - mu.pow(2) - logvar.exp()).sum(dim=1).mean()
        return recon_l + beta * kl, recon_l.item(), kl.item()

    def encoder_state_dict(self) -> dict:
        """Just conv1/conv2/fc1 — the o_flat,2 path that loads into VAEPatchFrontEnd."""
        return {k: v for k, v in self.state_dict().items()
                if k.split(".")[0] in ("conv1", "conv2", "fc1")}
