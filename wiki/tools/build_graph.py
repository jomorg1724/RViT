"""Build JSON, GraphML, and Markdown graph exports for the research wiki."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_escape

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
DB_ROOT = SCRIPT_DIR.parent
GRAPH_DIR = DB_ROOT / "graph"

PAGE_DIRECTORIES = {
    "papers": "paper",
    "concepts": "concept",
    "threads": "thread",
    "briefs": "brief",
    "notes": "note",
    "mocs": "moc",
    "conversations": "conversation",
    "sops": "sop",
    "people": "person",
    "preferences": "preference",
    "_adr": "adr",
}
WORKS = {"recurrent_vit", "prism_v1", "prism_v2"}
WORK_TITLES = {
    "recurrent_vit": "Recurrent ViT (Morgan, Albanna & Herman 2025)",
    "prism_v1": "PRISM v1",
    "prism_v2": "PRISM v2",
}


def parse_frontmatter(path: Path) -> dict[str, Any] | None:
    """Parse YAML frontmatter and retain the Markdown body for legacy links."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    match = re.match(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", text, re.DOTALL)
    if match is None:
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    if not isinstance(data, dict):
        return None
    data["__body__"] = text[match.end():]
    return data


def load_taxonomy_terms(path: Path) -> set[str]:
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8")
    return set(re.findall(r"`([a-zA-Z][a-zA-Z0-9_\-/]+)`", text))


def _values(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _relationship_values(record: dict[str, Any], field: str) -> list[str]:
    """Return a legacy relationship list or reject malformed semantic values."""
    value = record["frontmatter"].get(field, [])
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{record['path']} field '{field}' must be a list of strings")
    return value


def _plural(page_type: str) -> str:
    if page_type == "person":
        return "people"
    return f"{page_type}s"


def _discover_records(db_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for directory, page_type in PAGE_DIRECTORIES.items():
        page_dir = db_root / directory
        if not page_dir.exists():
            continue
        for path in sorted(page_dir.glob("*.md")):
            fm = parse_frontmatter(path)
            if fm is None:
                relative = path.relative_to(db_root).as_posix()
                raise ValueError(f"could not parse YAML frontmatter for {relative}")
            records.append({
                "id": path.stem,
                "type": page_type,
                "path": path.relative_to(db_root).as_posix(),
                "frontmatter": fm,
            })
    return records


def _node_from_record(record: dict[str, Any]) -> dict[str, Any]:
    fm = record["frontmatter"]
    heading_match = re.search(r"^#\s+(.+?)\s*$", str(fm.get("__body__", "")), re.MULTILINE)
    title = fm.get("title") or fm.get("defines")
    if not title and heading_match:
        title = heading_match.group(1)
    node: dict[str, Any] = {
        "id": record["id"],
        "type": record["type"],
        "title": title or record["id"],
        "status": fm.get("status", "") or "",
        "summary": fm.get("summary", "") or "",
        "tags": fm.get("tags", []) or [],
    }
    if record["type"] == "paper":
        for field, default in (
            ("year", ""), ("venue", ""), ("doi", ""), ("arxiv", ""),
            ("url", ""), ("tags", []), ("concepts", []),
            ("relevance_to", []), ("depth", ""), ("status", ""),
            ("seed_source", []),
        ):
            node[field] = fm.get(field, default) or default
    node["path"] = record["path"]
    return node


def build_graph(db_root: Path = DB_ROOT) -> dict[str, Any]:
    """Build a graph from every supported page directory under ``db_root``."""
    db_root = Path(db_root)
    records = _discover_records(db_root)
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []

    # Audit reports duplicate slugs; the graph nevertheless guarantees unique ids.
    records_by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        records_by_id.setdefault(record["id"], record)
    real_records = list(records_by_id.values())
    nodes.extend(_node_from_record(record) for record in real_records)

    # Preserve the three historical work targets, but let a real page (notably a
    # current MOC) own the id and all node attributes when one exists.
    for work in sorted(WORKS - set(records_by_id)):
        nodes.append({"id": work, "type": "work", "title": WORK_TITLES[work], "path": ""})

    paper_records = [record for record in real_records if record["type"] == "paper"]
    concept_records = [record for record in real_records if record["type"] == "concept"]
    thread_records = [record for record in real_records if record["type"] == "thread"]
    paper_ids = {record["id"] for record in paper_records}
    concept_ids = {record["id"] for record in concept_records}

    # Validate every paper relationship shape before resolving any target so a
    # malformed value cannot be hidden by an earlier, unrelated resolution error.
    for record in paper_records:
        for field in ("concepts", "related", "relevance_to"):
            _relationship_values(record, field)

    concept_term_to_id: dict[str, str] = {}
    for concept_id in concept_ids:
        concept_term_to_id[concept_id] = concept_id
        concept_term_to_id[concept_id.replace("_", "-")] = concept_id

    taxonomy_terms = load_taxonomy_terms(db_root / "TAXONOMY.md")
    concept_sources = paper_records + concept_records + thread_records
    for record in concept_sources:
        for term in _relationship_values(record, "concepts"):
            normalized = term.replace("-", "_")
            if term in concept_term_to_id or normalized in concept_term_to_id:
                continue
            taxonomy_id = term if term in taxonomy_terms else normalized if normalized in taxonomy_terms else None
            if taxonomy_id is None:
                raise ValueError(
                    f"{record['path']} concepts target '{term}' does not resolve to a concept or taxonomy term"
                )
            if taxonomy_id not in {node["id"] for node in nodes}:
                nodes.append({
                    "id": taxonomy_id,
                    "type": "taxonomy-concept",
                    "title": taxonomy_id.replace("-", " ").replace("_", " ").title(),
                    "path": "TAXONOMY.md",
                })
            concept_term_to_id[term] = taxonomy_id
            concept_term_to_id[normalized] = taxonomy_id
            concept_term_to_id[taxonomy_id] = taxonomy_id

    node_ids = {node["id"] for node in nodes}

    def concept_id_for(term: Any) -> str | None:
        if not isinstance(term, str):
            return None
        return concept_term_to_id.get(term) or concept_term_to_id.get(term.replace("-", "_"))

    # Legacy graph semantics.
    for record in paper_records:
        for related in _relationship_values(record, "related"):
            if related not in paper_ids:
                raise ValueError(
                    f"{record['path']} related target '{related}' does not resolve to a paper"
                )
            edges.append({"source": record["id"], "target": related, "type": "cites"})
        for term in _relationship_values(record, "concepts"):
            concept_id = concept_id_for(term)
            if concept_id:
                edges.append({"source": record["id"], "target": concept_id, "type": "has-concept"})
        for work in _relationship_values(record, "relevance_to"):
            if work not in node_ids:
                raise ValueError(
                    f"{record['path']} relevance_to target '{work}' does not resolve to a page or historical work"
                )
            edges.append({"source": record["id"], "target": work, "type": "relevant-to"})

    for record in concept_records:
        for paper_id in _relationship_values(record, "papers"):
            if paper_id not in paper_ids:
                raise ValueError(
                    f"{record['path']} papers target '{paper_id}' does not resolve to a paper"
                )
            edges.append({"source": record["id"], "target": paper_id, "type": "anchors"})
        for term in _relationship_values(record, "concepts"):
            concept_id = concept_id_for(term)
            if concept_id is None:
                raise ValueError(
                    f"{record['path']} concepts target '{term}' does not resolve to a concept"
                )
            edges.append({"source": record["id"], "target": concept_id, "type": "related-concept"})

    for record in thread_records:
        for paper_id in _relationship_values(record, "papers"):
            if paper_id not in paper_ids:
                raise ValueError(
                    f"{record['path']} papers target '{paper_id}' does not resolve to a paper"
                )
            edges.append({"source": record["id"], "target": paper_id, "type": "anchors"})
        for term in _relationship_values(record, "concepts"):
            concept_id = concept_id_for(term)
            if concept_id is None:
                raise ValueError(
                    f"{record['path']} concepts target '{term}' does not resolve to a concept"
                )
            edges.append({"source": record["id"], "target": concept_id, "type": "touches-concept"})

    for record in concept_records:
        body = str(record["frontmatter"].get("__body__", ""))
        for concept_id in concept_ids:
            if concept_id != record["id"] and re.search(r"\b" + re.escape(concept_id) + r"\b", body):
                edges.append({
                    "source": record["id"], "target": concept_id, "type": "related-concept",
                })

    # Current typed links. Object edges carry their controlled relationship;
    # accepted bare string entries use an explicit generic edge type.
    for record in real_records:
        see_also = record["frontmatter"].get("see_also", []) or []
        if not isinstance(see_also, list):
            continue
        for entry in see_also:
            if isinstance(entry, str):
                target, relationship = entry, "see-also"
            elif isinstance(entry, dict):
                target, relationship = entry.get("slug"), entry.get("rel")
            else:
                continue
            if isinstance(target, str) and target in node_ids and isinstance(relationship, str):
                edges.append({
                    "source": record["id"], "target": target, "type": relationship,
                })

    node_type_counts = Counter(node["type"] for node in nodes)
    metadata: dict[str, Any] = {
        "types": dict(sorted(node_type_counts.items())),
        "nodes": len(nodes),
        "edges": len(edges),
    }
    for page_type, count in sorted(node_type_counts.items()):
        metadata[_plural(page_type)] = count

    return {"metadata": metadata, "nodes": nodes, "edges": edges}


def write_json(graph: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")


def _graphml_value(value: Any) -> str:
    if isinstance(value, list):
        return ",".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    return str(value)


def write_graphml(graph: dict[str, Any], path: Path) -> None:
    """Serialize every emitted node field, including fields of new page types."""
    field_values: dict[str, list[Any]] = {}
    for node in graph["nodes"]:
        for key, value in node.items():
            if key != "id":
                field_values.setdefault(key, []).append(value)
    node_keys: dict[str, str] = {}
    for key, values in sorted(field_values.items()):
        nonempty = [value for value in values if value not in (None, "")]
        node_keys[key] = (
            "int" if nonempty and all(isinstance(value, int) and not isinstance(value, bool) for value in nonempty)
            else "string"
        )

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<graphml xmlns="http://graphml.graphdrawing.org/xmlns">')
    for name, value_type in node_keys.items():
        escaped_name = xml_escape(name, {'"': "&quot;"})
        lines.append(
            f'  <key id="n_{escaped_name}" for="node" attr.name="{escaped_name}" attr.type="{value_type}"/>'
        )
    lines.append('  <key id="e_type" for="edge" attr.name="type" attr.type="string"/>')
    lines.append('  <graph id="research_db" edgedefault="directed">')

    for node in graph["nodes"]:
        node_id = xml_escape(str(node["id"]), {'"': "&quot;"})
        lines.append(f'    <node id="{node_id}">')
        for key in node_keys:
            if key not in node or node[key] in (None, ""):
                continue
            value = xml_escape(_graphml_value(node[key]))
            lines.append(f'      <data key="n_{key}">{value}</data>')
        lines.append("    </node>")

    for index, edge in enumerate(graph["edges"]):
        source = xml_escape(str(edge["source"]), {'"': "&quot;"})
        target = xml_escape(str(edge["target"]), {'"': "&quot;"})
        edge_type = xml_escape(str(edge["type"]))
        lines.append(f'    <edge id="e{index}" source="{source}" target="{target}">')
        lines.append(f'      <data key="e_type">{edge_type}</data>')
        lines.append("    </edge>")

    lines.extend(("  </graph>", "</graphml>"))
    path.write_text("\n".join(lines), encoding="utf-8")


def write_summary_markdown(graph: dict[str, Any], path: Path) -> None:
    metadata = graph["metadata"]
    edge_counts = Counter(edge["type"] for edge in graph["edges"])
    node_counts = Counter(node["type"] for node in graph["nodes"])

    lines = [
        "# Graph export summary",
        "",
        "Generated by `tools/build_graph.py`. Re-run that script to refresh.",
        "",
        f"- **Nodes:** {metadata['nodes']}",
    ]
    for page_type, count in sorted(node_counts.items()):
        lines.append(f"  - {page_type}: {count}")
    lines.append(f"- **Edges:** {metadata['edges']}")
    for edge_type, count in sorted(edge_counts.items()):
        lines.append(f"  - {edge_type}: {count}")
    lines.extend([
        "", "## Artifacts", "",
        "- `graph.json` — JSON dump with full node and edge attributes.",
        "- `graph.graphml` — GraphML, suitable for yEd, Gephi, Cytoscape.",
        "- `graph_summary.md` — this file.",
        "", "## Loading from Python", "", "```python",
        "import json, networkx as nx",
        "g = json.load(open('research_db/graph/graph.json'))",
        "G = nx.DiGraph()",
        "for n in g['nodes']: G.add_node(n['id'], **{k:v for k,v in n.items() if k!='id'})",
        "for e in g['edges']: G.add_edge(e['source'], e['target'], type=e['type'])",
        "```", "", "## Edge types", "",
        "Legacy edges retain `cites`, `has-concept`, `anchors`, `touches-concept`, "
        "`related-concept`, and `relevant-to`; current `see_also` objects use their "
        "controlled `rel`, while bare slug entries use `see-also`.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not (DB_ROOT / "papers").exists():
        print(f"FATAL: papers dir not found: {DB_ROOT / 'papers'}", file=sys.stderr)
        return 1
    GRAPH_DIR.mkdir(exist_ok=True)
    try:
        graph = build_graph(DB_ROOT)
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    write_json(graph, GRAPH_DIR / "graph.json")
    write_graphml(graph, GRAPH_DIR / "graph.graphml")
    write_summary_markdown(graph, GRAPH_DIR / "graph_summary.md")

    metadata = graph["metadata"]
    print(f"Wrote graph: {metadata['nodes']} nodes, {metadata['edges']} edges")
    for page_type, count in metadata["types"].items():
        print(f"  {page_type:<9}: {count}")
    print(f"Artifacts in {GRAPH_DIR}:")
    for output in sorted(GRAPH_DIR.iterdir()):
        print(f"  {output.name} ({output.stat().st_size / 1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
