# Frozen-trunk fresh-head VDA4 rescue probe

This experiment asks whether the representation already learned by the failed two-layer transformer-memory run contains task-relevant VDA4 information.

## Frozen parent

- Parent iteration: `16949`
- SHA256: `d9539ef2c4cb0b337da4c87023f10b6507581d189392c2c99c93a624ada10898`
- Loaded and frozen: `front.*`, `encoder.*`
- Not loaded: old actor, old critic, JEPA heads/centers, optimizer, teachers, replay, or curriculum state

## Fresh trainable parameters

Only `actor_head.*` and `critic_head.*` are fresh and trainable. JEPA is disabled, so the trunk cannot continue adapting. Actor and critic both read frozen `H2`.

The actor starts with neutral action bias `[0,0]`, and entropy coefficient is raised to `0.1`. These are deliberate probe safeguards against the previously observed always-wait collapse. They mean the result tests whether frozen H2 exposes useful task information, not whether the failed behavior-policy protocol was itself adequate.

## Interpretation

- Stable above-chance performance: the frozen trunk learned task-relevant information accessible to fresh heads.
- Chance performance with a noncollapsed actor: the frozen trunk does not expose sufficient task information.
- Another always-wait collapse: the probe is inconclusive and needs an explicit behavior-policy exploration floor.

This launcher is local-only and hash-verifies the immutable parent before training.
