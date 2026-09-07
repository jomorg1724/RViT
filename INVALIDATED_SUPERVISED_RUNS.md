# Invalidated supervised runs

The retired supervised collectors discarded the observation returned by reset() and collected only subsequent step() observations. This shifted the input sequence; their supervised runs, checkpoints, metrics, figures, and downstream analyses are invalid and must not be reused or cited as valid results.

This cleanup removes the explicitly identified affected artifacts and retired collectors from the current main tree. No weights or results from the removed scope are retained in this tree, and no replacement backups are created by this cleanup. Unrelated work, including reset-correct RL, is preserved.

Corrected training requires a fresh run with reset observation t0 included, seven inputs t0..t6, and labels 0000011 (blank_first_v1). Corrected trainer/model changes are a separate follow-up; KimiDecayVDAConvRecurrentTF/pretrain_kda_convmem.py remains pending that replacement and must not be used as validation of a repaired pipeline at this commit.

This is not a history purge: older Git commits, other refs, clones, caches, or external run storage may still contain invalid material. Do not recover or reuse it. No shared-history rewrite was performed.
