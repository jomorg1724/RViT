# Triplet Codebook Cross-Attention

Fresh variant directory for a continuous learned-codebook lookup model.

## Architecture

```text
frame -> conv 4x4 patchifier -> X

Q = Q(X)
K = concat(K1(f1(H1)), K2(f2(H1)), K3(f3(H1)))
V = concat(V1(H_CB1), V2(H_CB2), V3(H_CB3))

Z = softmax(QK^T / sqrt(d)) V     # no residual
H1 = xLSTM(X + Z, H1)

actor / critic read flatten(Z)
```

Key choices:

- Three learned codebooks: `H_CB1`, `H_CB2`, `H_CB3`.
- Single xLSTM only.
- The agent-facing representation is the selected codebook value `Z`.
- The memory update still sees `X + Z`, so visual evidence can shape the next query/key state.

Checkpoints:

```text
~/rvit_plus_checkpoints/triplet_codebook/
```

## Train

```bash
cd /Users/jonathanmorgan/AttentionManuscript
.venv/bin/python RViT_plus_triplet_codebook/train_rl.py --device mps
```

Smoke test:

```bash
.venv/bin/python RViT_plus_triplet_codebook/train_rl.py --iters 2 --device cpu --log-every 1
```
