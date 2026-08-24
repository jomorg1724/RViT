---
id: tay2022_efficient_transformers_survey
title: "Efficient Transformers: A Survey"
authors:
  - "Tay, Yi"
  - "Dehghani, Mostafa"
  - "Bahri, Dara"
  - "Metzler, Donald"
year: 2022
venue: "ACM Computing Surveys"
doi: ""
arxiv: "2009.06732"
url: "https://arxiv.org/abs/2009.06732"
tags:
  - transformers
  - deep-learning
  - review
concepts:
  - scaled-dot-product-attention
related:
  - vaswani2017_attention
  - dosovitskiy2020_vit
  - khan2022_transformers_vision_survey
relevance_to:
  - recurrent_vit
  - prism_v2
seed_source:
  - manual
status: full
depth: full
last_updated: "2026-05-14"
---

# Efficient Transformers: A Survey

## 1. Abstract

Transformer model architectures have garnered immense interest lately due to their effectiveness across a range of domains like language, vision and reinforcement learning. In the field of natural language processing for example, Transformers have become an indispensable staple in the modern deep learning stack. Recently, a dizzying number of "X-former" models have been proposed — Reformer, Linformer, Performer, Longformer, to name a few — which improve upon the original Transformer architecture, many of which make improvements around computational and memory efficiency. With the aim of helping the avid researcher navigate this flurry, this paper characterizes a large and thoughtful selection of recent efficiency-flavored "X-former" models, providing an organized and comprehensive overview of existing work and models across multiple domains.

## 2. Why this matters for us

The user's published Recurrent ViT (2502.10955) uses standard Vaswani-style scaled-dot-product self-attention, whose cost is $O(n^2 d)$ in the number of tokens $n$. The architectural program (`threads/the_user_architectural_program.md` §1) extends this with a Feedback Transformer that integrates $K$ recurrent feedback sources via Hadamard-broadcast Q/K/V combination prior to the softmax. The $K$-source extension does not change the softmax cost — it changes only how Q and K are constructed — so the dominant $O(n^2)$ term is unaffected. This survey is the canonical map of the efficient-attention landscape: when the program scales to longer token sequences (full-frame video, multi-modal fusion at high resolution) or to more parallel hubs (PRISM v2's MSI / RL / VAE hubs each contributing tokens), Tay et al. supply the menu of softmax replacements (Performer, Linformer, Longformer, Big Bird, Reformer, Linear Transformer) that the Feedback Transformer can be combined with.

## 3. Key claims

1. The $O(n^2)$ self-attention cost is the dominant scaling bottleneck of Vaswani-style Transformers; a large family of variants reduces this to $O(n \log n)$, $O(n\sqrt{n})$, or $O(n)$ via fixed sparsity, learned sparsity, low-rank projection, kernel approximation, or recurrence.
2. The "X-former" zoo can be organized into a small taxonomy: fixed patterns (Sparse Transformer, Blockwise, Longformer local windows), combinations of patterns (Big Bird, Longformer global + local), learnable patterns (Reformer LSH, Routing Transformer), memory-based (Compressive Transformer, Set Transformer), low-rank / kernel (Linformer, Performer, Linear Transformer, Synthesizer), and recurrence (Transformer-XL, Compressive Transformer).
3. Efficiency improvements trade off against expressive power and accuracy on long-range tasks in non-trivial ways; no single variant dominates across the Long Range Arena benchmark.
4. The choice of efficient-attention variant should be matched to the task: local-window methods favor tasks with strong locality (vision, NLP with short dependencies); kernel/low-rank methods favor tasks with diffuse dependencies but moderate expressivity needs; learned-sparsity methods favor tasks with content-dependent dependency structure.
5. Most efficient variants are drop-in replacements for the softmax attention block and preserve the rest of the Transformer architecture (LayerNorm, residuals, FFN, multi-head structure).

## 4. Methods

The survey is taxonomic rather than experimental. The authors enumerate $\sim 17$ named architectures and classify each along the dimensions:

- **Complexity:** the asymptotic cost in sequence length $n$. Standard Transformer is $O(n^2 d)$; Reformer with LSH is $O(n \log n)$; Sparse / Longformer with local windows of size $w$ is $O(nw)$; Linformer and Performer are $O(n)$ with constants that depend on the rank or feature-map dimension.
- **Memory pattern:** fixed (predetermined sparsity mask), learned (data-dependent sparsity), or full (dense but factorized).
- **Decomposition strategy:** sparsity, low-rank projection, kernel approximation, or recurrence over chunks.

For each architecture they describe the modification to the attention computation. For example, Linformer replaces the keys and values $K, V \in \mathbb{R}^{n \times d}$ with low-rank projections $E K, F V \in \mathbb{R}^{k \times d}$ for $k \ll n$, reducing the softmax to $O(nk)$. Performer replaces the softmax kernel $\exp(q^\top k / \sqrt d)$ with a positive-orthogonal-random-feature approximation $\phi(q)^\top \phi(k)$, allowing the matmul order to be rearranged for $O(n)$ cost. Longformer uses a sparse mask combining sliding-window local attention with a small set of global tokens. Big Bird adds random attention to the Longformer pattern. Reformer hashes queries to attend only within hash buckets.

The survey also reviews recurrent and memory-augmented variants — Transformer-XL re-uses cached hidden states across chunks; Compressive Transformer compresses older states into a coarser summary memory — as alternative routes to long-context efficiency that retain the $O(n^2)$ within-chunk cost but bound $n$ per chunk.

## 5. Results

The survey itself does not report a unified empirical evaluation; the empirical companion is the Long Range Arena benchmark (Tay et al. 2021, separate paper). The survey summarizes that benchmark's headline findings: on five long-context tasks (ListOps, byte-level text classification, byte-level retrieval, image classification on CIFAR-10 sequences, Pathfinder), the efficient variants cluster within a few percentage points of each other and of the dense Transformer, with no single variant winning across all tasks. Big Bird and Performer are noted as relatively strong all-rounders; Linformer is competitive on tasks with strong low-rank structure but weaker on Pathfinder; Reformer is moderate.

The survey also documents typical speedups: at $n = 4096$ tokens, the linear-cost variants (Performer, Linformer, Linear Transformer) are roughly $4$–$8\times$ faster than the dense baseline; at $n = 16384$ the speedup grows to $\sim 30\times$. Memory savings scale similarly.

## 6. Critique / limitations

The survey is a 2020–2022 snapshot; it predates several major developments — FlashAttention (Dao et al. 2022) which makes dense softmax attention practical at much longer $n$ via IO-aware kernels; Mamba and the state-space-model resurgence; sliding-window-only variants in modern open-weights LLMs (Llama, Mistral). These post-survey shifts have reduced the practical pressure to replace softmax attention at moderate context lengths.

The taxonomy is a snapshot of a moving target; many of the named architectures (Linformer, Reformer) have seen their practical use decline, while others (Longformer-style local attention, Performer-style kernel methods, mixture-of-experts) have been absorbed into mainstream practice. The classification dimensions occasionally overlap (Big Bird is both sparse-pattern and random, Synthesizer is both low-rank and learnable-pattern), and the boundaries are fuzzy.

The empirical claim that "no variant dominates" is true within the Long Range Arena evaluation but may not generalize to vision tasks, multi-modal fusion, or recurrent-state integration — exactly the regimes the user's architectural program targets. The survey explicitly notes that benchmark coverage is thin outside NLP.

The survey does not address the integration of efficient attention with *side channels* (recurrent memory states, top-down feedback, multi-modal tokens). This is the gap the user's Feedback Transformer fills — none of the efficient variants are designed to accept Hadamard-broadcast feedback from multiple recurrent states prior to the softmax.

## 7. Connection to our work

The user's Recurrent ViT (2502.10955) uses standard $O(n^2)$ scaled-dot-product attention with multiplicative feedback (§6.7 of the paper). At the published patch resolution ($16 \times 16$ patches on $224 \times 224$ images, so $n \approx 196$) this is fully tractable; efficient-attention substitutions provide no benefit. The argument for this survey kicks in along three axes of program-level scaling.

**Axis 1: longer sequences.** The Video VAE work (`threads/the_user_architectural_program.md` §6) operates on UCF101 clips and integrates up to twelve feedback sources. At higher spatial resolution or longer temporal windows, $n$ grows multiplicatively (frames $\times$ patches-per-frame). At $n \sim 10^4$ the $O(n^2)$ cost dominates and a Performer-style kernel approximation or Longformer-style local-window mask becomes load-bearing. The Feedback Transformer's Hadamard-broadcast structure (§1 of the thread) is independent of the softmax replacement: the feedback sources contribute to $Q$ and $K$ before the kernel approximation, so Performer's $\phi(q)^\top \phi(k)$ rearrangement is still valid.

**Axis 2: more feedback sources.** PRISM v2 (`PRISM_V2_PROPOSAL.md` §3.4) and the multi-hub system (`threads/the_user_architectural_program.md` §5) contemplate $K \geq 3$ feedback sources (MSI, RL, VAE hubs). The per-source cost is $O(K \cdot n \cdot d)$ for the Hadamard projections — linear in $K$ and never dominant — but this confirms that the bottleneck remains the softmax, not the feedback integration. Efficient softmax replacements therefore deliver near-proportional speedups even at large $K$.

**Axis 3: choice of variant.** The vision regime favors local-window methods (Longformer, Swin-style window attention) because visual receptive fields are spatially local. The Feedback Transformer's design assumption — that every feedback source has the same token grid as the sensory input — composes cleanly with windowed attention: a feedback token at grid position $(i,j)$ enters the same window as the corresponding sensory token. For the iterative variational encoder–decoder (`threads/the_user_architectural_program.md` §4), where the $n_{FR}$ forward-reasoning passes share the same image, kernel methods (Performer) are attractive because the $\phi(K)$ projection of the keys can be cached across passes.

**Concrete recommendation.** When the program scales beyond $n \sim 10^3$ tokens, the survey's taxonomy says: try Performer first (strong general performance, $O(n)$ cost, drop-in for the softmax in the Feedback Transformer), Longformer second (better for spatially-local vision tasks, $O(nw)$ cost, compatible with the Feedback Transformer's per-position broadcasting), Big Bird third (combines locality and global tokens, useful for multi-modal fusion where some tokens must attend globally).

## 8. Citations to follow

- `dao2022_flashattention` — IO-aware exact softmax that makes dense attention practical at much longer $n$; supersedes much of the efficiency motivation for some variants. Not yet in seed.
- `child2019_sparse_transformer` — Sparse Transformer, the canonical fixed-pattern variant. Not yet in seed.
- `kitaev2020_reformer` — LSH-based learnable sparsity at $O(n \log n)$. Not yet in seed.
- `wang2020_linformer` — Linear-cost low-rank projection. Not yet in seed.
- `choromanski2020_performer` — Kernel-based softmax approximation at $O(n)$; the most likely drop-in for the Feedback Transformer at scale. Not yet in seed.
- `beltagy2020_longformer` — Sliding-window plus global tokens; well-matched to vision tasks. Not yet in seed.
- `zaheer2020_bigbird` — Sparse + global + random pattern; theoretical universality result. Not yet in seed.
- `dai2019_transformer_xl` — Segment-level recurrence; the closest published precedent for the Feedback Transformer's recurrent-state integration. Not yet in seed.
- `katharopoulos2020_linear_transformers` — Linear-cost kernel attention with recurrent formulation. Not yet in seed.
- `tay2021_long_range_arena` — The empirical benchmark companion to this survey. Not yet in seed.
