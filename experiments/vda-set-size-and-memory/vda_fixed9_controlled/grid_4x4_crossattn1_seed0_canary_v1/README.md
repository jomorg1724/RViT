# VDA fixed-set-size 9 cross-attention canary v1

This is the controlled VDA9 midpoint: `vda_fixed9` renders exactly nine active
items on the invariant 4x4, 100px canvas. The model therefore has 16 visual and
recurrent-memory tokens, matching `vda_fixed1/2/4/16`; this is not the historical
3x3/9-token `vda9` task.

Locked training contract: seed 0, fresh uninterrupted initialization, 20,000
iterations numbered 0..19999, 8 episodes/iteration, `xlstm`, `crossattn1`,
`d_mem=128`, memory decay 1.0, memory noise 0, trained convolutional frontend,
temporal JEPA coefficient 0.5, and CUDA. Scientific values are not environment
overrides. Only `PYTHON_BIN` may be supplied to select the RunPod interpreter.

Run the static preflight from the project root before upload and again on the pod:

```bash
python experiments/vda_fixed9_controlled/grid_4x4_crossattn1_seed0_canary_v1/preflight_contract_v1.py \
  --project-root . \
  --config experiments/vda_fixed9_controlled/grid_4x4_crossattn1_seed0_canary_v1/config_v1.json \
  --launcher experiments/vda_fixed9_controlled/grid_4x4_crossattn1_seed0_canary_v1/launch_runpod_v1.sh
```

Launch in the foreground (a caller may wrap this in `nohup` and record the PID):

```bash
bash experiments/vda_fixed9_controlled/grid_4x4_crossattn1_seed0_canary_v1/launch_runpod_v1.sh
```

The launcher emits a unique `RUN_DIR`, writes `launch_contract.json` before
training, and mirrors trainer output to `RUN_DIR/train.log`. It refuses an absent
runtime or source tree and binds both this launcher and its dedicated config into
checkpoint `producer_sha256` metadata.

Do not call the canary complete from a periodic checkpoint or training accuracy.
Completion requires the trainer to exit, exactly contiguous finite metrics
0..19999, schema-v3 terminal final/latest checkpoints, exact task/model/training
and source-hash contracts, finite equal required state, a clean final-save log,
remote/local byte and SHA-256 agreement through a unique `.partial` pull, and an
independent held-out behavioral evaluation. Only held-out behavior can decide
whether follow-up seeds are warranted or support an attention claim.
