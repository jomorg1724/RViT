"""
Query the research database graph.

Reads research_db/graph/graph.json (run tools/build_graph.py first to
regenerate). Provides keyword search and structural traversals over the
papers/concepts/threads/works graph.

Subcommands
-----------
    search <terms>...
        Keyword search across node titles, ids, and paper tags/concepts.
        Ranks by simple term overlap. Returns top 20.

    paper <paper-id>
        Show a paper card: frontmatter, outgoing citations, incoming
        citations, concepts it touches, threads that anchor it,
        works it is relevant to.

    concept <concept-id>
        Show a concept card: the set of papers anchored by this concept
        (from the concept file's papers: list) plus the papers that
        list this concept in their own frontmatter.

    thread <thread-id>
        Show a thread card: papers and concepts the thread spans.

    work <work-id>
        Show all papers relevant to a work (recurrent_vit, prism_v1,
        prism_v2), grouped by depth.

    neighbors <node-id> [--depth N]
        Print the neighborhood of a node out to depth N (default 1).
        Includes edge types. Useful for exploring around an unknown node.

    path <id-1> <id-2>
        Shortest undirected path between two nodes, with the edge type
        on each hop. Returns "no path" if disconnected.

    stats
        Summary statistics: node counts, edge counts, top-cited papers,
        most-anchored concepts.

Run without arguments for usage. Uses only the standard library.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict, deque
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DB_ROOT = SCRIPT_DIR.parent
GRAPH_PATH = DB_ROOT / "graph" / "graph.json"


# ---------------------------------------------------------------------------
# Graph loading
# ---------------------------------------------------------------------------

class Graph:
    def __init__(self, data: dict) -> None:
        self.nodes_by_id: dict[str, dict] = {n["id"]: n for n in data["nodes"]}
        self.edges = data["edges"]
        # Adjacency, both directions, with edge types
        self.out: dict[str, list[tuple[str, str]]] = defaultdict(list)
        self.inc: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for e in self.edges:
            self.out[e["source"]].append((e["target"], e["type"]))
            self.inc[e["target"]].append((e["source"], e["type"]))

    def has(self, nid: str) -> bool:
        return nid in self.nodes_by_id

    def kind(self, nid: str) -> str:
        return self.nodes_by_id[nid].get("type", "?")

    def title(self, nid: str) -> str:
        n = self.nodes_by_id.get(nid)
        if not n:
            return f"<unknown:{nid}>"
        return n.get("title") or nid


def load_graph() -> Graph:
    if not GRAPH_PATH.exists():
        print(f"ERROR: graph not built. Run: python3 research_db/tools/build_graph.py", file=sys.stderr)
        sys.exit(2)
    with GRAPH_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    return Graph(data)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_node(g: Graph, nid: str) -> str:
    """One-line node label: `id (kind) — title`."""
    if not g.has(nid):
        return f"{nid} <unresolved>"
    kind = g.kind(nid)
    title = g.title(nid)
    # Keep titles short in lists
    if len(title) > 70:
        title = title[:67] + "..."
    return f"  {kind:<7} {nid:<48} {title}"


def section(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


# ---------------------------------------------------------------------------
# Subcommand: search
# ---------------------------------------------------------------------------

def cmd_search(g: Graph, terms: list[str]) -> int:
    if not terms:
        print("usage: query.py search <term>...", file=sys.stderr)
        return 2
    needles = [t.lower() for t in terms]

    scored: list[tuple[int, str]] = []
    for nid, n in g.nodes_by_id.items():
        haystack_parts = [nid.lower(), str(n.get("title", "")).lower()]
        for k in ("tags", "concepts", "relevance_to"):
            v = n.get(k)
            if isinstance(v, list):
                haystack_parts.append(" ".join(str(x).lower() for x in v))
        hay = " ".join(haystack_parts)
        score = 0
        for needle in needles:
            score += hay.count(needle)
        if score > 0:
            scored.append((score, nid))

    scored.sort(key=lambda x: (-x[0], x[1]))
    if not scored:
        print("(no matches)")
        return 0

    print(f"Top {min(20, len(scored))} of {len(scored)} matches for: {' '.join(terms)}")
    for score, nid in scored[:20]:
        print(f"  [{score:3d}] {fmt_node(g, nid).strip()}")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: paper
# ---------------------------------------------------------------------------

def cmd_paper(g: Graph, pid: str) -> int:
    if not g.has(pid):
        print(f"unknown id: {pid}", file=sys.stderr)
        return 2
    n = g.nodes_by_id[pid]
    if n.get("type") != "paper":
        print(f"{pid} is a {n.get('type')}, not a paper. Try `{n.get('type')} {pid}` if supported.")
        # still show neighbors for convenience
    print(f"{pid}")
    print(f"  title       : {n.get('title','')}")
    print(f"  year        : {n.get('year','')}")
    print(f"  venue       : {n.get('venue','')}")
    print(f"  doi         : {n.get('doi','')}")
    print(f"  arxiv       : {n.get('arxiv','')}")
    print(f"  depth       : {n.get('depth','')}  status: {n.get('status','')}")
    print(f"  tags        : {', '.join(n.get('tags') or [])}")
    print(f"  concepts    : {', '.join(n.get('concepts') or [])}")
    print(f"  relevance_to: {', '.join(n.get('relevance_to') or [])}")
    print(f"  seed_source : {', '.join(n.get('seed_source') or [])}")
    print(f"  path        : {n.get('path','')}")

    out_cites = [t for t, et in g.out[pid] if et == "cites"]
    inc_cites = [s for s, et in g.inc[pid] if et == "cites"]
    out_concepts = [t for t, et in g.out[pid] if et == "has-concept"]
    inc_concept_anchors = [s for s, et in g.inc[pid] if et == "anchors" and g.kind(s) == "concept"]
    inc_thread_anchors = [s for s, et in g.inc[pid] if et == "anchors" and g.kind(s) == "thread"]
    out_works = [t for t, et in g.out[pid] if et == "relevant-to"]

    if out_cites:
        section(f"Cites (related: in frontmatter) — {len(out_cites)}")
        for nid in sorted(out_cites): print(fmt_node(g, nid))
    if inc_cites:
        section(f"Cited by — {len(inc_cites)}")
        for nid in sorted(inc_cites): print(fmt_node(g, nid))
    if out_concepts:
        section(f"Concepts (touches a concept node) — {len(out_concepts)}")
        for nid in sorted(out_concepts): print(fmt_node(g, nid))
    if inc_concept_anchors:
        section(f"Anchored by concepts — {len(inc_concept_anchors)}")
        for nid in sorted(inc_concept_anchors): print(fmt_node(g, nid))
    if inc_thread_anchors:
        section(f"Anchored by threads — {len(inc_thread_anchors)}")
        for nid in sorted(inc_thread_anchors): print(fmt_node(g, nid))
    if out_works:
        section(f"Relevant to — {len(out_works)}")
        for nid in sorted(out_works): print(fmt_node(g, nid))
    return 0


# ---------------------------------------------------------------------------
# Subcommand: concept
# ---------------------------------------------------------------------------

def cmd_concept(g: Graph, cid: str) -> int:
    if not g.has(cid):
        print(f"unknown id: {cid}", file=sys.stderr)
        return 2
    if g.kind(cid) != "concept":
        print(f"{cid} is a {g.kind(cid)}, not a concept", file=sys.stderr)
        return 2
    n = g.nodes_by_id[cid]
    print(cid)
    print(f"  title : {n.get('title','')}")
    print(f"  path  : {n.get('path','')}")

    anchored = [t for t, et in g.out[cid] if et == "anchors"]
    listed_in = [s for s, et in g.inc[cid] if et == "has-concept"]
    threads_touching = [s for s, et in g.inc[cid] if et == "touches-concept"]

    if anchored:
        section(f"Anchored papers (from concept's papers: list) — {len(anchored)}")
        # Group by depth
        by_depth: dict[str, list[str]] = defaultdict(list)
        for pid in anchored:
            depth = g.nodes_by_id[pid].get("depth", "?") if g.has(pid) else "?"
            by_depth[depth].append(pid)
        for d in ("full", "summary", "abstract", "metadata", "?"):
            if d in by_depth:
                print(f"  -- depth: {d}")
                for pid in sorted(by_depth[d]): print(fmt_node(g, pid))
    if listed_in:
        section(f"Papers that list this concept in their frontmatter — {len(listed_in)}")
        for pid in sorted(listed_in): print(fmt_node(g, pid))
    if threads_touching:
        section(f"Threads that touch this concept — {len(threads_touching)}")
        for tid in sorted(threads_touching): print(fmt_node(g, tid))
    return 0


# ---------------------------------------------------------------------------
# Subcommand: thread
# ---------------------------------------------------------------------------

def cmd_thread(g: Graph, tid: str) -> int:
    if not g.has(tid):
        print(f"unknown id: {tid}", file=sys.stderr)
        return 2
    if g.kind(tid) != "thread":
        print(f"{tid} is a {g.kind(tid)}, not a thread", file=sys.stderr)
        return 2
    n = g.nodes_by_id[tid]
    print(tid)
    print(f"  title : {n.get('title','')}")
    print(f"  path  : {n.get('path','')}")

    papers = [t for t, et in g.out[tid] if et == "anchors"]
    concepts = [t for t, et in g.out[tid] if et == "touches-concept"]
    if concepts:
        section(f"Concepts touched — {len(concepts)}")
        for cid in sorted(concepts): print(fmt_node(g, cid))
    if papers:
        section(f"Papers anchored — {len(papers)}")
        by_depth: dict[str, list[str]] = defaultdict(list)
        for pid in papers:
            depth = g.nodes_by_id[pid].get("depth", "?") if g.has(pid) else "?"
            by_depth[depth].append(pid)
        for d in ("full", "summary", "abstract", "metadata", "?"):
            if d in by_depth:
                print(f"  -- depth: {d}")
                for pid in sorted(by_depth[d]): print(fmt_node(g, pid))
    return 0


# ---------------------------------------------------------------------------
# Subcommand: work
# ---------------------------------------------------------------------------

def cmd_work(g: Graph, wid: str) -> int:
    if not g.has(wid):
        print(f"unknown work id: {wid}", file=sys.stderr)
        print("valid: recurrent_vit, prism_v1, prism_v2", file=sys.stderr)
        return 2
    if g.kind(wid) != "work":
        print(f"{wid} is a {g.kind(wid)}, not a work", file=sys.stderr)
        return 2

    papers = [s for s, et in g.inc[wid] if et == "relevant-to"]
    print(f"{wid} — {g.title(wid)}")
    print(f"  relevant papers: {len(papers)}")
    by_depth: dict[str, list[str]] = defaultdict(list)
    for pid in papers:
        depth = g.nodes_by_id[pid].get("depth", "?") if g.has(pid) else "?"
        by_depth[depth].append(pid)
    for d in ("full", "summary", "abstract", "metadata", "?"):
        if d in by_depth:
            section(f"depth = {d} ({len(by_depth[d])})")
            for pid in sorted(by_depth[d]): print(fmt_node(g, pid))
    return 0


# ---------------------------------------------------------------------------
# Subcommand: neighbors
# ---------------------------------------------------------------------------

def cmd_neighbors(g: Graph, args: list[str]) -> int:
    if not args:
        print("usage: query.py neighbors <id> [--depth N]", file=sys.stderr)
        return 2
    nid = args[0]
    depth = 1
    if len(args) >= 3 and args[1] == "--depth":
        try: depth = int(args[2])
        except ValueError:
            print("--depth must be an integer", file=sys.stderr); return 2
    if not g.has(nid):
        print(f"unknown id: {nid}", file=sys.stderr); return 2

    print(f"Neighborhood of {nid} ({g.kind(nid)}: {g.title(nid)}) — depth {depth}")
    visited: set[str] = {nid}
    frontier: list[str] = [nid]
    for d in range(1, depth + 1):
        section(f"depth {d}")
        new_frontier: list[str] = []
        seen_at_this_depth: set[tuple[str, str, str, str]] = set()
        for u in frontier:
            for v, et in g.out[u]:
                key = (u, "→", v, et)
                if key in seen_at_this_depth: continue
                seen_at_this_depth.add(key)
                marker = "  " if v in visited else "* "
                print(f"  {u} --{et}--> {marker}{v} ({g.kind(v)}: {g.title(v)[:50]})")
                if v not in visited:
                    visited.add(v); new_frontier.append(v)
            for s, et in g.inc[u]:
                key = (s, "←", u, et)
                if key in seen_at_this_depth: continue
                seen_at_this_depth.add(key)
                marker = "  " if s in visited else "* "
                print(f"  {u} <--{et}-- {marker}{s} ({g.kind(s)}: {g.title(s)[:50]})")
                if s not in visited:
                    visited.add(s); new_frontier.append(s)
        frontier = new_frontier
        if not frontier:
            break
    return 0


# ---------------------------------------------------------------------------
# Subcommand: path
# ---------------------------------------------------------------------------

def cmd_path(g: Graph, args: list[str]) -> int:
    if len(args) != 2:
        print("usage: query.py path <id-1> <id-2>", file=sys.stderr); return 2
    a, b = args
    if not g.has(a):
        print(f"unknown id: {a}", file=sys.stderr); return 2
    if not g.has(b):
        print(f"unknown id: {b}", file=sys.stderr); return 2

    # BFS treating edges as undirected, but remember direction & type for the trace
    prev: dict[str, tuple[str, str, str]] = {}  # node -> (predecessor, direction, edge type)
    visited = {a}
    q: deque[str] = deque([a])
    found = False
    while q:
        u = q.popleft()
        if u == b:
            found = True; break
        for v, et in g.out[u]:
            if v not in visited:
                visited.add(v); prev[v] = (u, "→", et); q.append(v)
        for s, et in g.inc[u]:
            if s not in visited:
                visited.add(s); prev[s] = (u, "←", et); q.append(s)

    if not found:
        print(f"no path between {a} and {b}"); return 0

    # Reconstruct
    trace: list[tuple[str, str, str, str]] = []  # (from, arrow, to, edge type)
    cur = b
    while cur != a:
        pred, arrow, et = prev[cur]
        trace.append((pred, arrow, cur, et))
        cur = pred
    trace.reverse()
    print(f"path ({len(trace)} hops):")
    print(f"  {a} ({g.kind(a)}: {g.title(a)[:60]})")
    for u, arrow, v, et in trace:
        sigil = "->" if arrow == "→" else "<-"
        print(f"    {sigil} [{et}] {v} ({g.kind(v)}: {g.title(v)[:60]})")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: stats
# ---------------------------------------------------------------------------

def cmd_stats(g: Graph) -> int:
    by_kind: dict[str, int] = defaultdict(int)
    for n in g.nodes_by_id.values():
        by_kind[n.get("type", "?")] += 1
    by_etype: dict[str, int] = defaultdict(int)
    for e in g.edges:
        by_etype[e["type"]] += 1
    print("nodes:")
    for k, c in sorted(by_kind.items()): print(f"  {k:<8} {c}")
    print("edges:")
    for k, c in sorted(by_etype.items()): print(f"  {k:<16} {c}")

    # Top cited papers
    cite_in: dict[str, int] = defaultdict(int)
    for e in g.edges:
        if e["type"] == "cites":
            cite_in[e["target"]] += 1
    section("Top 10 most-cited papers (by `cites` edges in)")
    for pid, c in sorted(cite_in.items(), key=lambda x: -x[1])[:10]:
        print(f"  [{c}] {fmt_node(g, pid).strip()}")

    # Most-anchored concepts
    anchor_out: dict[str, int] = defaultdict(int)
    for e in g.edges:
        if e["type"] == "anchors" and g.kind(e["source"]) == "concept":
            anchor_out[e["source"]] += 1
    section("Top 10 concepts by number of anchored papers")
    for cid, c in sorted(anchor_out.items(), key=lambda x: -x[1])[:10]:
        print(f"  [{c}] {fmt_node(g, cid).strip()}")

    # Most-touched concepts (via paper has-concept edges)
    touched: dict[str, int] = defaultdict(int)
    for e in g.edges:
        if e["type"] == "has-concept":
            touched[e["target"]] += 1
    section("Top 10 concepts by has-concept edges from papers")
    for cid, c in sorted(touched.items(), key=lambda x: -x[1])[:10]:
        print(f"  [{c}] {fmt_node(g, cid).strip()}")
    return 0


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

USAGE = """\
usage: query.py <command> [args]

commands:
  search <term>...                  keyword search across titles/ids/tags/concepts
  paper <paper-id>                  show paper card
  concept <concept-id>              show concept card
  thread <thread-id>                show thread card
  work <work-id>                    show papers relevant to a work
  neighbors <node-id> [--depth N]   neighborhood out to depth N
  path <id-1> <id-2>                shortest undirected path
  stats                             summary stats and rankings
"""


def main(argv: list[str]) -> int:
    if not argv:
        sys.stderr.write(USAGE); return 2
    g = load_graph()
    cmd, rest = argv[0], argv[1:]
    if cmd == "search":
        return cmd_search(g, rest)
    if cmd == "paper":
        if not rest: sys.stderr.write("usage: query.py paper <paper-id>\n"); return 2
        return cmd_paper(g, rest[0])
    if cmd == "concept":
        if not rest: sys.stderr.write("usage: query.py concept <concept-id>\n"); return 2
        return cmd_concept(g, rest[0])
    if cmd == "thread":
        if not rest: sys.stderr.write("usage: query.py thread <thread-id>\n"); return 2
        return cmd_thread(g, rest[0])
    if cmd == "work":
        if not rest: sys.stderr.write("usage: query.py work <work-id>\n"); return 2
        return cmd_work(g, rest[0])
    if cmd == "neighbors":
        return cmd_neighbors(g, rest)
    if cmd == "path":
        return cmd_path(g, rest)
    if cmd == "stats":
        return cmd_stats(g)
    if cmd in ("-h", "--help", "help"):
        sys.stdout.write(USAGE); return 0
    sys.stderr.write(f"unknown command: {cmd}\n"); sys.stderr.write(USAGE); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
