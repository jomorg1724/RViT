"""
Generate stubs for the cite-trail papers referenced in the user's
Private & Shared notes but not in the original ViT-paper / THESIS / V2
seed bibliographies. These are the load-bearing references for the
user's architectural program (the Feedback Transformer, GridCell RNN,
multi-compartmental memory, and competition-emergent PC).

Run:
    python3 research_db/tools/generate_private_stubs.py
"""
from __future__ import annotations
from pathlib import Path
from textwrap import dedent

SCRIPT_DIR = Path(__file__).resolve().parent
PAPERS_DIR = SCRIPT_DIR.parent / "papers"
TODAY = "2026-05-13"

# (id, title, authors, year, venue, tags, concepts, relevance, seed,
#  arxiv, doi, related)
PRIVATE_REFS = [
    # --- Core load-bearing references for the architectural program ---
    ("schmidhuber2015_learn_to_think", "On Learning to Think: Algorithmic Information Theory for Novel Combinations of RL Controllers and Recurrent Neural World Models",
     ["Schmidhuber, Juergen"], 2015, "arXiv:1511.09249",
     ["deep-learning", "reinforcement-learning", "theoretical-essay"],
     ["world-model-emergence", "coalition-resource-competition", "multi-hub-multi-objective-system"],
     ["recurrent_vit", "prism_v2"], ["prism_private_notes"], "1511.09249", "", []),
    ("wang2025_hierarchical_reasoning_model", "Hierarchical Reasoning Model",
     ["Wang, Guan", "et al."], 2025, "arXiv:2506.21734",
     ["deep-learning", "recurrent-networks", "theoretical-essay"],
     ["slow-fast-recurrence", "parallel-recurrent-units", "hierarchical-reasoning-model"],
     ["prism_v2", "recurrent_vit"], ["prism_private_notes"], "2506.21734", "", []),
    ("higgins2017_factorized_representations", "Beta-VAE: Learning Basic Visual Concepts with a Constrained Variational Framework / Factorized Representations",
     ["Higgins, Irina", "Matthey, Loic", "Pal, Arka", "et al."], 2017, "ICLR",
     ["self-supervised-learning", "representation-learning", "deep-learning"],
     ["factorized-representations", "variational-free-energy"],
     ["prism_v2"], ["prism_private_notes"], "", "", []),
    ("manns_eichenbaum2006_lec_mec", "Evolution of declarative memory / LEC and MEC factorization",
     ["Manns, Joseph R.", "Eichenbaum, Howard"], 2006, "Hippocampus",
     ["primate-neurophysiology", "review"],
     ["lec-mec-factorization", "factorized-representations"],
     ["prism_v2"], ["prism_private_notes"], "", "", []),
    ("sherman2022_ctc_loop", "Functions of the cortico-thalamo-cortical loop",
     ["Sherman, S. Murray"], 2022, "Frontiers / NCBI",
     ["cortical-anatomy", "review", "primate-neurophysiology"],
     ["cortico-thalamo-cortical-loops", "top-down-feedback"],
     ["recurrent_vit", "prism_v2"], ["prism_private_notes"], "", "", []),
    ("haber2015_cbgtc_circuits", "Cortico-basal ganglia-thalamic circuits in goal-directed behavior",
     ["Haber, Suzanne N."], 2015, "Dialogues in Clinical Neuroscience / NCBI",
     ["cortical-anatomy", "subcortical", "review"],
     ["cortico-basal-ganglia-thalamic-loops", "reward-modulated-attention"],
     ["prism_v2"], ["prism_private_notes"], "", "", []),
    ("weiler2025_l6_corticocortical", "Layer 6 corticocortical neurons are a major route for intra and interhemispheric feedback",
     ["Weiler, Simon", "Teichert, Manuel", "Margrie, Troy W."], 2025, "eLife",
     ["primate-neurophysiology", "cortical-anatomy"],
     ["top-down-feedback", "cortical-microcircuit-model"],
     ["recurrent_vit", "prism_v2"], ["prism_private_notes"], "", "", []),
    ("jordan2023_dendritic_bayesian", "Conductance-based dendrites perform Bayes-optimal cue integration",
     ["Jordan, Jakob", "Sacramento, Joao", "Wybo, Willem A. M.", "Petrovici, Mihai A.", "Senn, Walter"],
     2023, "arXiv:2104.13238",
     ["theoretical-essay", "cortical-anatomy"],
     ["dendritic-bayesian-integration", "multi-sensory-integration"],
     ["prism_v2"], ["prism_private_notes"], "2104.13238", "", []),
    ("laughlin1998_metabolic_cost", "The metabolic cost of neural information",
     ["Laughlin, Simon B.", "de Ruyter van Steveninck, R. R.", "Anderson, J. C."], 1998,
     "Nature Neuroscience",
     ["primate-neurophysiology", "theoretical-essay"],
     ["metabolic-cost-of-neural-information", "coalition-resource-competition"],
     ["prism_v2"], ["prism_private_notes"], "", "", []),
    ("senkowski_engel2024_multi_timescale_msi", "Multi-timescale neural dynamics for multisensory integration",
     ["Senkowski, Daniel", "Engel, Andreas K."], 2024, "Nature Reviews Neuroscience",
     ["primate-neurophysiology", "review"],
     ["multi-sensory-integration", "neural-oscillations-cfc"],
     ["prism_v2"], ["prism_private_notes"], "", "", []),
    ("choi2023_msi_review", "Multisensory integration in the mammalian brain: diversity and flexibility in health and disease",
     ["Choi, I.", "Demir, I.", "Oh, S.", "Lee, S. H."], 2023,
     "Philosophical Transactions of the Royal Society B",
     ["primate-neurophysiology", "review"],
     ["multi-sensory-integration"],
     ["prism_v2"], ["prism_private_notes"], "", "", []),
    ("masse2019_circuit_wm", "Circuit mechanisms for the maintenance and manipulation of information in working memory",
     ["Masse, Nicolas Y.", "Yang, Guangyu R.", "Song, H. Francis", "Wang, Xiao-Jing", "Freedman, David J."],
     2019, "Nature Neuroscience",
     ["primate-neurophysiology", "working-memory", "deep-learning"],
     ["working-memory-persistent-activity", "recurrence-for-temporal-dynamics"],
     ["prism_v2"], ["prism_private_notes"], "", "", []),
    # --- Cortical hierarchy and visual processing ---
    ("riesenhuber_poggio1999_hierarchical_models", "Hierarchical models of object recognition in cortex",
     ["Riesenhuber, Maximilian", "Poggio, Tomaso"], 1999, "Nature Neuroscience",
     ["primate-neurophysiology", "review", "theoretical-essay"],
     ["ventral-stream-hierarchy"],
     ["prism_v2", "recurrent_vit"], ["prism_private_notes"], "", "", []),
    ("mishkin1983_two_pathways", "Object vision and spatial vision: two cortical pathways",
     ["Mishkin, Mortimer", "Ungerleider, Leslie G.", "Macko, Kathleen A."], 1983,
     "Trends in Neurosciences",
     ["primate-neurophysiology", "review"],
     ["ventral-stream-hierarchy", "dorsal-stream"],
     ["recurrent_vit"], ["prism_private_notes"], "", "", []),
    ("hubel_wiesel1968_macaque", "Receptive fields and functional architecture of monkey striate cortex",
     ["Hubel, David H.", "Wiesel, Torsten N."], 1968, "Journal of Physiology",
     ["primate-neurophysiology", "early-visual-cortex"],
     ["gabor-receptive-fields", "orientation-selectivity"],
     ["prism_v1", "prism_v2"], ["prism_private_notes"], "", "", []),
    ("tanaka1996_it_object_vision", "Inferotemporal cortex and object vision",
     ["Tanaka, Keiji"], 1996, "Annual Review of Neuroscience",
     ["primate-neurophysiology", "review"],
     ["ventral-stream-hierarchy"],
     ["recurrent_vit"], ["prism_private_notes"], "", "", []),
    ("larkum2013_apical_basal", "A cellular mechanism for cortical associations: an organizing principle for the cerebral cortex",
     ["Larkum, Matthew"], 2013, "Trends in Neurosciences",
     ["primate-neurophysiology", "cortical-anatomy", "theoretical-essay"],
     ["cortical-microcircuit-model", "top-down-feedback"],
     ["prism_v2"], ["prism_private_notes"], "", "", []),
    ("gilbert_li2013_topdown", "Top-down influences on visual processing",
     ["Gilbert, Charles D.", "Li, Wu"], 2013, "Nature Reviews Neuroscience",
     ["primate-neurophysiology", "visual-attention", "review"],
     ["top-down-feedback", "gain-modulation"],
     ["prism_v2", "recurrent_vit"], ["prism_private_notes"], "", "", []),
    # --- LLM critiques / AGI framing ---
    ("lecun2022_path_to_agi", "A Path Towards Autonomous Machine Intelligence",
     ["LeCun, Yann"], 2022, "Open Review / Meta AI",
     ["deep-learning", "theoretical-essay", "world-models"],
     ["world-model-emergence", "system-1-vs-system-2"],
     ["recurrent_vit", "prism_v2"], ["prism_private_notes"], "", "", []),
    ("marcus2025_llm_critique", "Generative AI's crippling and widespread failure to induce robust models of the world",
     ["Marcus, Gary"], 2025, "Substack essay",
     ["deep-learning", "theoretical-essay", "review"],
     ["world-model-emergence", "causal-reasoning", "system-1-vs-system-2"],
     ["prism_v2"], ["prism_private_notes"], "", "", []),
    ("pearl2018_book_of_why", "The Book of Why / Ladder of Causation",
     ["Pearl, Judea"], 2018, "Basic Books",
     ["theoretical-essay", "review"],
     ["causal-reasoning"],
     ["prism_v2"], ["prism_private_notes"], "", "", []),
    ("hawkins2021_thousand_brains", "A Thousand Brains: A New Theory of Intelligence",
     ["Hawkins, Jeff"], 2021, "Basic Books",
     ["theoretical-essay", "review"],
     ["cortical-microcircuit-model", "hierarchical-predictive-coding"],
     ["prism_v2"], ["prism_private_notes"], "", "", []),
    # --- Predictive coding canon (cite trail) ---
    ("clark2013_whatever_next", "Whatever next? Predictive brains, situated agents, and the future of cognitive science",
     ["Clark, Andy"], 2013, "Behavioral and Brain Sciences",
     ["predictive-coding", "review", "theoretical-essay"],
     ["hierarchical-predictive-coding", "embodied-cognition"],
     ["prism_v1", "prism_v2"], ["prism_private_notes"], "", "", []),
    ("keller_mrsic_flogel2018_pc_review", "Predictive processing: a canonical cortical computation",
     ["Keller, Georg B.", "Mrsic-Flogel, Thomas D."], 2018, "Neuron",
     ["predictive-coding", "review", "primate-neurophysiology"],
     ["hierarchical-predictive-coding", "rao-ballard-coding"],
     ["prism_v1", "prism_v2"], ["prism_private_notes"], "", "", []),
    ("srinivasan1982_predictive_coding_retina", "Predictive coding: a fresh view of inhibition in the retina",
     ["Srinivasan, Mandyam V.", "Laughlin, Simon B.", "Dubs, Andreas"], 1982,
     "Proceedings of the Royal Society B",
     ["predictive-coding", "theoretical-essay"],
     ["rao-ballard-coding"],
     ["prism_v1"], ["prism_private_notes"], "", "", []),
    ("friston2005_cortical_responses", "A theory of cortical responses",
     ["Friston, Karl"], 2005, "Philosophical Transactions of the Royal Society B",
     ["free-energy-principle", "predictive-coding", "theoretical-essay"],
     ["variational-free-energy", "hierarchical-predictive-coding"],
     ["prism_v1", "prism_v2"], ["prism_private_notes"], "", "", []),
    ("summerfield_delange2014_expectation", "Expectation in perceptual decision making: neural and computational mechanisms",
     ["Summerfield, Christopher", "de Lange, Floris P."], 2014, "Nature Reviews Neuroscience",
     ["predictive-coding", "decision-making", "review"],
     ["hierarchical-predictive-coding"],
     ["prism_v1"], ["prism_private_notes"], "", "", []),
    ("aitchison_lengyel2017_pc_bayesian", "With or without you: predictive coding and Bayesian inference in the brain",
     ["Aitchison, Laurence", "Lengyel, Mate"], 2017, "Current Opinion in Neurobiology",
     ["predictive-coding", "theoretical-essay", "review"],
     ["hierarchical-predictive-coding", "variational-free-energy"],
     ["prism_v1"], ["prism_private_notes"], "", "", []),
    # --- Biased competition canon ---
    ("moran_desimone1985_selective_attention", "Selective attention gates visual processing in extrastriate cortex",
     ["Moran, Jeffrey", "Desimone, Robert"], 1985, "Science",
     ["primate-neurophysiology", "visual-attention", "early-visual-cortex"],
     ["biased-competition", "gain-modulation"],
     ["recurrent_vit", "prism_v1"], ["prism_private_notes"], "", "", []),
    ("miller_cohen2001_pfc_function", "An integrative theory of prefrontal cortex function",
     ["Miller, Earl K.", "Cohen, Jonathan D."], 2001, "Annual Review of Neuroscience",
     ["prefrontal-cortex", "review", "theoretical-essay"],
     ["working-memory-persistent-activity", "top-down-feedback"],
     ["prism_v1", "prism_v2"], ["prism_private_notes"], "", "", []),
    ("bundesen2005_neural_theory_attention", "A neural theory of visual attention: bridging cognition and neurophysiology",
     ["Bundesen, Claus", "Habekost, Thomas", "Kyllingsbæk, Søren"], 2005,
     "Psychological Review",
     ["visual-attention", "theoretical-essay"],
     ["biased-competition", "attentional-template"],
     ["prism_v1"], ["prism_private_notes"], "", "", []),
    # --- Game-theoretic and coalition framing ---
    ("edelman1987_neural_darwinism", "Neural Darwinism: The Theory of Neuronal Group Selection",
     ["Edelman, Gerald M."], 1987, "Basic Books",
     ["theoretical-essay", "review"],
     ["coalition-resource-competition"],
     ["prism_v2"], ["prism_private_notes"], "", "", []),
    ("buzsaki2010_cell_assemblies", "Neural syntax: cell assemblies, synapsembles, and readers",
     ["Buzsaki, Gyorgy"], 2010, "Neuron",
     ["primate-neurophysiology", "review", "theoretical-essay"],
     ["coalition-resource-competition"],
     ["prism_v2"], ["prism_private_notes"], "", "", []),
    ("lee2008_game_theory_neural", "Game theory and neural basis of social decision making",
     ["Lee, Daeyeol"], 2008, "Neuron",
     ["primate-neurophysiology", "decision-making", "review"],
     ["coalition-resource-competition"],
     ["prism_v2"], ["prism_private_notes"], "", "", []),
    ("carrillo_dewatripont2008_brain_executive", "The brain as a Central Executive System",
     ["Carrillo, Juan D.", "Dewatripont, Mathias"], 2008, "IEA Conference Volume",
     ["theoretical-essay", "review"],
     ["coalition-resource-competition"],
     ["prism_v2"], ["prism_private_notes"], "", "", []),
    ("glimcher2011_dopamine_rpe", "Understanding dopamine and reinforcement learning: the dopamine reward prediction error hypothesis",
     ["Glimcher, Paul W."], 2011, "PNAS",
     ["dopamine", "reinforcement-learning", "review"],
     ["reward-modulated-attention"],
     ["prism_v1"], ["prism_private_notes"], "", "", []),
    ("logie2003_mental_workspace", "Spatial and Visual Working Memory: A Mental Workspace",
     ["Logie, Robert H."], 2003, "Psychology of Learning and Motivation",
     ["working-memory", "review", "theoretical-essay"],
     ["working-memory-persistent-activity"],
     ["prism_v1", "prism_v2"], ["prism_private_notes"], "", "", []),
    # --- Embodied cognition / system 2 ---
    ("varela_thompson_rosch_embodied", "The Embodied Mind: Cognitive Science and Human Experience",
     ["Varela, Francisco J.", "Thompson, Evan", "Rosch, Eleanor"], 1991, "MIT Press",
     ["theoretical-essay", "review"],
     ["embodied-cognition"],
     ["prism_v2"], ["prism_private_notes"], "", "", []),
]

# Same template as the main generator
TEMPLATE = dedent("""\
    ---
    id: {id}
    title: "{title}"
    authors:
    {authors_block}
    year: {year}
    venue: "{venue}"
    doi: "{doi}"
    arxiv: "{arxiv}"
    url: "{url}"
    tags:
    {tags_block}
    concepts:
    {concepts_block}
    related:
    {related_block}
    relevance_to:
    {relevance_block}
    seed_source:
    {seed_block}
    status: stub
    depth: metadata
    last_updated: "{today}"
    ---

    # {title}

    > **Stub from user's private/shared notes cite-trail.** This paper is cited in the user's working notes (`Private & Shared` folders) as load-bearing for the architectural program. Deep-summarize in a future session per `SCHEMA.md`.

    ## 1. Abstract

    *Pending.*

    ## 2. Why this matters for us

    *Pending — but the entry is in the seed because it appears in `{seed_human}`.*
    """)


def _yaml_list(items, indent=2):
    if not items:
        return " " * indent + "[]"
    pad = " " * indent
    return "\n".join(f"{pad}- {x}" for x in items)


def _qyaml_list(items, indent=2):
    if not items:
        return " " * indent + "[]"
    pad = " " * indent
    return "\n".join(f'{pad}- "{x}"' for x in items)


def main():
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    n_created = 0
    n_skipped = 0
    for entry in PRIVATE_REFS:
        (eid, title, authors, year, venue, tags, concepts, relevance, seed,
         arxiv, doi, related) = entry
        url = f"https://arxiv.org/abs/{arxiv}" if arxiv else ""

        body = TEMPLATE.format(
            id=eid,
            title=title.replace('"', "'"),
            authors_block=_qyaml_list(authors),
            year=year,
            venue=venue,
            doi=doi,
            arxiv=arxiv,
            url=url,
            tags_block=_yaml_list(tags),
            concepts_block=_yaml_list(concepts),
            related_block=_yaml_list(related),
            relevance_block=_yaml_list(relevance),
            seed_block=_yaml_list(seed),
            seed_human=", ".join(seed),
            today=TODAY,
        )

        out = PAPERS_DIR / f"{eid}.md"
        if out.exists():
            n_skipped += 1
            continue
        out.write_text(body, encoding="utf-8")
        n_created += 1

    print(f"Created: {n_created} stubs from private/shared notes cite-trail")
    print(f"Skipped (already on disk): {n_skipped}")
    print(f"Total private cite-trail entries: {len(PRIVATE_REFS)}")


if __name__ == "__main__":
    main()
