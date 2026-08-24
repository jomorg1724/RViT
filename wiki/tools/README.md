# research_db tools

Three standard-library scripts that together cover the schema-enforcement, graph-export, and graph-query workflow for the database.

| Script | Purpose | Outputs |
|---|---|---|
| [audit.py](audit.py) | Schema validation: required frontmatter fields, taxonomy compliance, dangling cross-refs, duplicate ids. Run after every edit batch. | exit 0 if clean, 1 if issues; details to stdout |
| [build_graph.py](build_graph.py) | Walks `papers/`, `concepts/`, `threads/`; emits the database as a graph. Run whenever any of those directories change. | `../graph/graph.json`, `../graph/graph.graphml`, `../graph/graph_summary.md` |
| [query.py](query.py) | Reads the graph; provides keyword search and structural traversals over papers/concepts/threads/works. Read-only. | stdout |

There are also two stub-generation scripts ([generate_stubs.py](generate_stubs.py), [generate_private_stubs.py](generate_private_stubs.py)) used in the initial database build. They are kept for reproducibility but should not be re-run in normal operation.

## Workflow

```bash
# 1. Edit papers/, concepts/, or threads/ files
# 2. Validate
python3 research_db/tools/audit.py

# 3. Refresh the graph export
python3 research_db/tools/build_graph.py

# 4. Query (any time after step 3)
python3 research_db/tools/query.py stats
```

## query.py subcommands

```
search <term>...                  keyword search across titles/ids/tags/concepts
paper <paper-id>                  paper card with citations, concepts, threads, works
concept <concept-id>              concept card with anchored papers and back-refs
thread <thread-id>                thread card with papers and concepts
work <work-id>                    papers relevant to recurrent_vit / prism_v1 / prism_v2
neighbors <node-id> [--depth N]   graph neighborhood, default depth 1
path <id-1> <id-2>                shortest undirected path with edge types
stats                             summary stats and rankings
```

The `work-id` values are `recurrent_vit`, `prism_v1`, `prism_v2`.

## Examples

```bash
# What does the database say about hierarchical predictive coding?
python3 research_db/tools/query.py concept hierarchical_predictive_coding

# What papers ground the user's multi-hub system?
python3 research_db/tools/query.py concept multi_hub_multi_objective_system

# What is the citation neighborhood of the HRM paper?
python3 research_db/tools/query.py neighbors wang2025_hierarchical_reasoning_model --depth 2

# How is Rao-Ballard 1999 connected to Dreamer 2020?
python3 research_db/tools/query.py path rao_ballard1999_predictive_coding hafner2020_dreamer

# Find papers about dendritic Bayesian integration
python3 research_db/tools/query.py search dendritic bayesian

# All full-depth papers relevant to PRISM v2
python3 research_db/tools/query.py work prism_v2

# Top-cited papers and most-anchored concepts
python3 research_db/tools/query.py stats
```

## Notes

- `query.py` is read-only — it loads from `graph/graph.json`. If you've just edited the database, run `build_graph.py` first.
- Edge types in the graph:
  - `cites` — paper → paper (from `related:` in paper frontmatter)
  - `has-concept` — paper → concept (from `concepts:` in paper frontmatter, only when the concept term resolves to a `concepts/*.md` file)
  - `anchors` — concept/thread → paper (from `papers:` in concept/thread frontmatter)
  - `touches-concept` — thread → concept (from `concepts:` in thread frontmatter)
  - `relevant-to` — paper → work (from `relevance_to:` in paper frontmatter)
- The graph is directed but `neighbors` and `path` treat it as undirected for traversal, while preserving direction in the output.
- Pure stdlib, no dependencies. Will run on any Python 3.9+ install.
