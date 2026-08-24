# Action-Value Critic for PRISM v2

## 1. Problem Setting

PRISM v2 trains a recurrent policy $\pi_\theta(a\mid s_t)$ jointly with an
auxiliary predictive-coding objective. The critic provides the baseline used
by GAE to form PPO advantages. In the original v2 the critic was a
*distributional state-value head* $Z_\phi(s) \in \mathbb{R}^{N}$ — $N$
quantile estimates of the return distribution — with the scalar baseline
$V_\phi(s) = \frac{1}{N}\sum_i Z_{\phi, i}(s)$ used by the GAE recursion.

**Failure mode observed.** With the bootstrapping prior
`init_action_logit_bias = [0.0, -4.0]`, the policy enters training near-
deterministically committed to action $0$:
$$\pi(a{=}0\mid s) \;=\; \sigma(0 - (-4)) \;=\; \frac{1}{1 + e^{-4}} \;\approx\; 0.982.$$
Under this policy the target the critic chases is

$$ V_\pi(s) \;=\; \sum_a \pi(a\mid s)\, Q_\pi(s, a) \;\approx\; 0.982\, Q_\pi(s, 0) + 0.018\, Q_\pi(s, 1) \;\approx\; Q_\pi(s, 0). $$

So the critic only ever needs to model the value of "look", not "press". The
PPO advantage estimator
$\hat A_t = G_t^{\lambda} - V_\phi(s_t)$ then sees roughly
$G_t^{\lambda} - Q(s_t, 0)$ on every step — *including* the rare exploration
steps where $a_t = 1$. There is no learnable parameter anywhere in the
network whose gradient with respect to the critic loss says "the value of
'press' here is different from the value of 'look'." The advantage signal
the actor receives is therefore mostly noise around the dominant-action
baseline, and the policy gradient cannot escape the prior.

## 2. Mathematical Background

### 2.1 Notation

* $s_t$ — readout-vector state representation at step $t$.
* $a_t \in \mathcal{A}$ — discrete action (here $|\mathcal{A}|=2$).
* $G_t^{\lambda}$ — λ-return / GAE return target at step $t$.
* $\pi_\theta(a\mid s)$ — policy (actor MLP outputs logits, softmaxed).
* $Q_\phi(s, a)$, $V_\phi(s)$ — critic predictions.
* $\rho^\kappa_\tau(\delta) = |\tau - \mathbb{1}\{\delta < 0\}|\, L_\kappa(\delta)$ — quantile Huber.

### 2.2 Action-Conditional Distributional Critic

We replace the marginal $Z_\phi(s)$ head with an action-conditional
distributional Q head:

$$ Q_\phi(s, a; \tau_i) \in \mathbb{R}^{B \times |\mathcal{A}| \times N}, \qquad \tau_i = \frac{2i-1}{2N}, \; i=1,\dots,N. $$

Mean-over-quantiles per action:

$$ Q_\phi(s, a) \;=\; \frac{1}{N}\sum_i Q_\phi(s, a; \tau_i) \quad\in\mathbb{R}^{B\times|\mathcal{A}|}. $$

State value derived analytically:

$$ V_\phi(s) \;=\; \sum_a \mathrm{sg}\!\left[\pi_\theta(a\mid s)\right]\, Q_\phi(s, a) \quad\in\mathbb{R}^{B}, $$

where $\mathrm{sg}[\cdot]$ is the stop-gradient operator. This $V_\phi$ is
used as the GAE bootstrap; the stop-gradient is the key piece of plumbing
discussed in §2.4.

### 2.3 Critic Loss

Action-conditional QR-Huber on the $a_t$ column:

$$ L_Q(\phi) \;=\; \mathbb{E}_{(s_t, a_t, G_t^\lambda) \sim \mathcal{D}} \left[\, \frac{1}{N}\sum_{i=1}^N \rho^\kappa_{\tau_i}\!\big(G_t^{\lambda} - Q_\phi(s_t, a_t; \tau_i)\big) \,\right]. $$

Operationally we gather the $a_t$ slice from $Q_\phi(s_t, \cdot; \cdot)$ and
feed it to `losses.quantile_huber_loss`. The gradient of $L_Q$ flows into:

* the columns of `critic.fc2.weight` and `critic.fc2.bias` corresponding to
  $a_t$ — directly,
* `critic.fc1` and the entire upstream stack (`head_backbone`, `readout`,
  memories, stems, FiLM, decoders) — via the shared features.

The columns of `critic.fc2` corresponding to $a' \neq a_t$ get **zero**
gradient on this update. They learn only via shared upstream features and
inter-batch averaging across episodes where the agent did sample $a'$. This
is by design and matches Q-learning's update rule (which trains
$Q(s, a_t)$ alone per transition).

### 2.4 Gradient Routing — Why the Stop-Gradient Matters

Without `sg[·]` on the policy probabilities in the $V_\phi$ definition,
backprop from $L_Q$ would flow:

$$ L_Q \;\to\; G_t^\lambda - Q_\phi(s_t, a_t; \tau_i) \;\to\; (\text{not via } V_\phi) \;\to\; Q_\phi $$

so $L_Q$ alone is fine. But $V_\phi$ is *also* used downstream — in the
GAE recursion — and any path through $V_\phi$ to $\theta_{\text{actor}}$
would inject value-target supervision into the policy. We avoid this in
two complementary ways:

1. The critic loss is on $Q_\phi(s_t, a_t; \cdot)$ directly, never on
   $V_\phi$. So $L_Q$ has no path to $\theta_{\text{actor}}$ at all, even
   without stop-gradient.
2. The PPO surrogate consumes GAE advantages whose values $V_{\text{old}}(s)$
   are *stored at rollout time as constants* (a numpy array). At update
   time, $V_\phi$ would only re-enter if we re-bootstrapped — we do not.

The stop-gradient on $\pi$ in $V_\phi(s) = \sum \mathrm{sg}[\pi]\,Q$ is
nonetheless retained for clarity and as a defence against any future code
path that uses $V_\phi$ in a differentiable loss. It costs nothing.

### 2.5 Actor Loss (unchanged)

The PPO clipped surrogate uses GAE advantages computed from $V_\phi$ as
the baseline:

$$ \delta_t \;=\; r_t + \gamma V_\phi(s_{t+1}) - V_\phi(s_t), \qquad \hat A_t \;=\; \sum_{l=0}^{T-t-1} (\gamma\lambda)^l\, \delta_{t+l}. $$

The advantage is normalised across the batch (per `compute_gae`). The
policy loss is the standard

$$ L_\pi(\theta) \;=\; -\mathbb{E}\Big[\min\big(r_t(\theta) \hat A_t, \mathrm{clip}(r_t, 1\pm\epsilon) \hat A_t\big)\Big], $$

with $r_t(\theta) = \exp(\log \pi_\theta(a_t|s_t) - \log \pi_{\text{old}}(a_t|s_t))$.

### 2.6 Total Loss

$$ L(\theta, \phi) \;=\; L_\pi + c_v\, L_Q + c_e\, L_{\text{entropy}} + c_{\text{PC}}\, L_{\text{PC}} + c_s\, L_{\text{slow}}. $$

No coefficient changes from the v2 baseline.

## 3. Connection to Literature

* **QR-DQN** (Dabney et al. 2018) — distributional Q with quantile
  regression. We use its loss exactly, applied per action.
* **Dueling networks** (Wang et al. 2016) — explicit $Q = V + A$
  decomposition. We do *not* use the dueling parameterisation; we expose
  $Q(s, a)$ directly and derive $V$ analytically as $\sum \pi Q$. This is
  the *expected-SARSA* baseline (Sutton & Barto 2018, §6.6).
* **Soft Actor-Critic** (Haarnoja et al. 2018) — uses $V(s) = \mathbb{E}_\pi[Q - \alpha \log \pi]$ and entropy regularisation. We use the same
  $V$ machinery (without the entropy term inside $V$, since PPO already
  has its own $L_{\text{entropy}}$).
* **PPG / phasic policy gradient** (Cobbe et al. 2020) — separates value
  and policy training phases. Our gradient-routing argument echoes the PPG
  motivation but achieves separation by detaching $\pi$ in $V$, not by
  separating optimisation phases.

## 4. Implementation Considerations

### 4.1 Numerical Stability

* `state_value` uses `log_softmax(...).exp()` rather than `softmax`
  directly, for numerically stable conversion of logits to probabilities.
  This is the standard pattern when both log probs and probs are needed.
* Quantile Huber is stable by construction (Huber transition prevents the
  outer derivative from blowing up).
* `init_action_logit_bias=[0,-4]` is preserved; with the new critic, even
  the rare $a_t=1$ exploration steps now produce a learning signal at the
  correct slot of `critic.fc2`, so we expect the bias to be *easier* to
  escape than under the old V critic.

### 4.2 Computational Cost

`critic.fc2` grows from $H \times N$ to $H \times (|\mathcal{A}| \cdot N)$
parameters — for $H=128$, $|\mathcal{A}|=2$, $N=51$ that's
$128 \times 102 = 13{,}056$ vs $128 \times 51 = 6{,}528$, a 6.5K-parameter
increase. Negligible against the ~1.48 M total budget.

Forward FLOPs: identical except for the final `Linear` which doubles its
output count. Negligible.

### 4.3 Common Pitfalls

* **Forgetting to gather $a_t$.** If you accidentally feed the full
  $Q_\phi(s, \cdot; \cdot)$ tensor to `quantile_huber_loss` against scalar
  $G_t$, broadcasting will silently train every action's Q to the same
  return — re-introducing exactly the action-marginal bug the redesign was
  meant to fix. The PPO update file gathers explicitly:
  ```python
  act_idx = actions_chunk.view(B, T, 1, 1).expand(B, T, 1, N)
  q_at_t = q_dist_t.gather(2, act_idx).squeeze(2)  # (B, T, N)
  ```
* **Rollout `value` shape regression.** `step_out.value` is now `(B,)`
  (was `(B, N)` in the broken intermediate). The collector calls
  `step_out.value[0].item()` directly. Double-check this if you re-thread
  the collector.
* **`StepOutput.q_values` vs `q_dist`.** `q_values` is the mean-over-
  quantile reduction, used for downstream analysis only (e.g. the
  `q_action_spread` diagnostic). The PPO update operates on the full
  `q_dist` so the QR loss can shape the *distribution*, not just its mean.

## 5. Verification Suggestions

The new tests in `tests/test_shapes.py`:

* `test_critic_head_action_conditional_distributional` — shape contract,
  $V = \sum \pi Q$ identity, stop-gradient correctness.
* `test_full_model_step` — `value` shape `(B,)`, `q_dist` shape
  `(B, |A|, N)`, $V = \sum \pi Q$ identity at the model level.
* `test_action_conditional_critic_grad_routing` — *the* test for this
  redesign: when all examples take $a_t = 1$, the rows of
  `critic.fc2.weight` for $a = 0$ must receive **zero** gradient and the
  rows for $a = 1$ must be nonzero. Failure here means the gather was
  wrong or the loss is silently broadcasting.

Recommended sanity checks once training resumes:

* The new train-loop log column `dQ` is the mean
  $|Q(s, a{=}0) - Q(s, a{=}1)|$ across the batch. It should grow (above
  zero) within the first few hundred PPO updates as the critic learns to
  discriminate actions. If it stays at $\sim 0$, the action-conditioning
  is not engaging — likely either too small `value_coef`, dominated PC
  gradients, or insufficient $a_t = 1$ exploration to populate the column.
* Run `analysis/gradient_audit.py` after, say, 200 PPO iterations and
  confirm `critic.fc2` gets nonzero L2 grad from `RL-ONLY`.

## 6. References

1. Dabney, W., Rowland, M., Bellemare, M., Munos, R. (2018). *Distributional
   Reinforcement Learning with Quantile Regression*. AAAI. — Eqs. 5–6 (QR
   loss), §3 (mean derivation). Our `losses.quantile_huber_loss` is their
   loss.
2. Wang, Z., Schaul, T., Hessel, M., van Hasselt, H., Lanctot, M., de
   Freitas, N. (2016). *Dueling Network Architectures for Deep
   Reinforcement Learning*. ICML. — Motivates explicit per-action Q
   exposure even when V is the only direct target.
3. Sutton, R. S., Barto, A. G. (2018). *Reinforcement Learning: An
   Introduction* (2nd ed.). MIT Press. §6.6 — Expected SARSA, the
   on-policy analogue of $V = \sum \pi Q$.
4. Schulman, J., Wolski, F., Dhariwal, P., Radford, A., Klimov, O. (2017).
   *Proximal Policy Optimization Algorithms*. arXiv:1707.06347. §3 —
   surrogate objective and value-baseline structure we preserve.
5. Cobbe, K., Hilton, J., Klimov, O., Schulman, J. (2020). *Phasic Policy
   Gradient*. ICML 2021. — Argues for separating value and policy gradient
   pathways; our stop-gradient on $\pi$ in $V$ is a lightweight alternative.
