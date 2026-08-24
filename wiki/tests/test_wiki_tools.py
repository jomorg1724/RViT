from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def load_tool(name: str):
    module_path = Path(__file__).parents[1] / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_page(root: Path, directory: str, slug: str, frontmatter: str, body: str = "") -> Path:
    path = root / directory / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter.strip()}\n---\n{body}", encoding="utf-8")
    return path


def write_taxonomy(root: Path) -> None:
    (root / "TAXONOMY.md").write_text("`topic/test` `concept-test`\n", encoding="utf-8")


def legacy_paper(slug: str, *, related: str = "[]") -> str:
    return f"""
id: {slug}
title: Legacy paper
authors: [Example, Author]
year: 2020
venue: Test Venue
tags: [topic/test]
concepts: [concept-test]
related: {related}
relevance_to: [recurrent_vit]
seed_source: [manual]
status: full
depth: full
last_updated: 2026-01-01
"""


def test_audit_accepts_grandfathered_papers_and_valid_current_pages(tmp_path: Path) -> None:
    write_taxonomy(tmp_path)
    write_page(tmp_path, "papers", "legacy_one", legacy_paper("legacy_one", related="[legacy_two]"))
    write_page(tmp_path, "papers", "legacy_two", legacy_paper("legacy_two"))
    write_page(
        tmp_path,
        "concepts",
        "concept_one",
        """
id: concept_one
type: concept
status: draft
created: 2026-07-11
tags: [topic/test]
title: Current concept
summary: A fixture concept.
see_also:
  - slug: legacy_one
    rel: grounded-in
  - legacy_two
""",
    )
    write_page(
        tmp_path,
        "mocs",
        "recurrent_vit",
        """
id: recurrent_vit
type: moc
status: stable
created: 2026-07-11
tags: []
title: Recurrent ViT
""",
    )

    report = load_tool("audit").audit_database(tmp_path)

    assert report["issues"] == []
    assert report["counts"] == {"paper": 2, "concept": 1, "moc": 1}


def test_audit_validates_typed_paper_only_against_current_schema(tmp_path: Path) -> None:
    write_page(tmp_path, "papers", "current_paper", current_page("paper", "current_paper"))

    report = load_tool("audit").audit_database(tmp_path)

    assert report["issues"] == []
    assert report["depth_counts"] == {}


def test_audit_grandfathers_legacy_concepts_and_threads_without_exempting_current_pages(
    tmp_path: Path,
) -> None:
    write_page(
        tmp_path,
        "concepts",
        "legacy_concept",
        """
id: legacy_concept
type: concept
papers: []
concepts: []
last_updated: 2026-01-01
""",
    )
    write_page(
        tmp_path,
        "threads",
        "legacy_thread",
        """
id: legacy_thread
type: thread
title: Legacy thread
papers: []
concepts: [legacy_concept]
last_updated: 2026-01-01
""",
    )
    write_page(
        tmp_path,
        "concepts",
        "incomplete_current_concept",
        """
id: incomplete_current_concept
type: concept
status: draft
created: 2026-07-11
papers: []
""",
    )

    issues = load_tool("audit").audit_database(tmp_path)["issues"]

    assert issues == ["[incomplete_current_concept.md] missing fields: ['tags']"]


def test_audit_reports_current_schema_yaml_slug_and_link_failures(tmp_path: Path) -> None:
    write_taxonomy(tmp_path)
    write_page(tmp_path, "papers", "legacy_one", legacy_paper("legacy_one"))
    write_page(
        tmp_path,
        "concepts",
        "duplicate",
        """
id: duplicate
type: concept
status: stable
created: 2026-07-11
tags: []
""",
    )
    write_page(
        tmp_path,
        "notes",
        "duplicate",
        """
id: wrong_id
type: brief
status: full
see_also:
  - slug: nowhere
    rel: invented
  - slug: legacy_one
    rel: [extends]
  - rel: extends
  - 7
""",
    )
    malformed = tmp_path / "briefs" / "bad_yaml.md"
    malformed.parent.mkdir(parents=True)
    malformed.write_text("---\ntype: brief\ntags: [unterminated\n---\n", encoding="utf-8")

    issues = load_tool("audit").audit_database(tmp_path)["issues"]
    joined = "\n".join(issues)

    assert "frontmatter missing or malformed" in joined
    assert "duplicate slug 'duplicate'" in joined
    assert "missing fields: ['created', 'tags']" in joined
    assert "id 'wrong_id' != filename stem 'duplicate'" in joined
    assert "type 'brief' does not match directory type 'note'" in joined
    assert "status 'full' not in" in joined
    assert "see_also slug 'nowhere' does not resolve" in joined
    assert "see_also rel 'invented' not in" in joined
    assert "see_also object missing string slug" in joined
    assert "see_also entry must be a string or object" in joined


def test_audit_rejects_malformed_current_field_types(tmp_path: Path) -> None:
    write_page(
        tmp_path,
        "notes",
        "bad_types",
        """
id: bad_types
type: note
status: stable
created: []
tags: topic/test
""",
    )

    issues = "\n".join(load_tool("audit").audit_database(tmp_path)["issues"])

    assert "[bad_types.md] created must be a YYYY-MM-DD date" in issues
    assert "[bad_types.md] tags must be a list of strings" in issues


def test_audit_validates_legacy_concept_and_thread_relationships(tmp_path: Path) -> None:
    write_page(tmp_path, "papers", "paper_one", legacy_paper("paper_one"))
    write_page(
        tmp_path,
        "concepts",
        "concept_one",
        """
id: concept_one
type: concept
papers: [paper_one, missing_paper]
concepts:
  - [nested_concept]
last_updated: 2026-01-01
""",
    )
    write_page(
        tmp_path,
        "threads",
        "thread_one",
        """
id: thread_one
type: thread
title: Thread
papers: {bad: shape}
concepts: [concept-one, missing-concept]
last_updated: 2026-01-01
""",
    )

    issues = "\n".join(load_tool("audit").audit_database(tmp_path)["issues"])

    assert "[concept_one.md] papers id 'missing_paper' does not resolve to a paper file" in issues
    assert "[concept_one.md] concepts must be a list of strings" in issues
    assert "[thread_one.md] papers must be a list of strings" in issues
    assert "[thread_one.md] concepts id 'missing-concept' does not resolve to a concept page or taxonomy term" in issues


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("concepts", "concept-test"),
        ("concepts", "[[concept-test]]"),
        ("related", "paper_two"),
        ("related", "[{bad: shape}]"),
        ("relevance_to", "recurrent_vit"),
        ("relevance_to", "[[recurrent_vit]]"),
    ],
)
def test_audit_rejects_malformed_legacy_paper_relationship_values(
    tmp_path: Path, field: str, value: str
) -> None:
    canonical = {
        "concepts": "[concept-test]",
        "related": "[]",
        "relevance_to": "[recurrent_vit]",
    }[field]
    paper = legacy_paper("paper_one").replace(
        f"{field}: {canonical}",
        f"{field}: {value}",
    )
    write_page(tmp_path, "papers", "paper_one", paper)

    issues = load_tool("audit").audit_database(tmp_path)["issues"]

    assert f"[paper_one.md] {field} must be a list of strings" in issues


def current_page(page_type: str, slug: str, *, extra: str = "") -> str:
    return f"""
id: {slug}
type: {page_type}
status: stable
created: 2026-07-11
tags: [topic/test]
title: {slug.replace('_', ' ').title()}
summary: Summary for {slug}.
{extra}
"""


def test_graph_discovers_current_types_and_preserves_legacy_edges(tmp_path: Path) -> None:
    write_taxonomy(tmp_path)
    write_page(tmp_path, "papers", "legacy_one", legacy_paper("legacy_one", related="[legacy_two]"))
    write_page(tmp_path, "papers", "legacy_two", legacy_paper("legacy_two"))
    write_page(
        tmp_path,
        "concepts",
        "concept_test",
        current_page(
            "concept",
            "concept_test",
            extra="""
papers: [legacy_one]
see_also:
  - slug: legacy_two
    rel: grounded-in
  - legacy_one
""",
        ),
    )
    write_page(
        tmp_path,
        "threads",
        "thread_one",
        current_page("thread", "thread_one", extra="papers: [legacy_two]\nconcepts: [concept-test]"),
    )
    write_page(tmp_path, "mocs", "recurrent_vit", current_page("moc", "recurrent_vit"))
    write_page(tmp_path, "notes", "finding", current_page("note", "finding"))
    for directory, page_type in {
        "briefs": "brief",
        "conversations": "conversation",
        "sops": "sop",
        "people": "person",
        "preferences": "preference",
        "_adr": "adr",
    }.items():
        write_page(tmp_path, directory, f"fixture_{page_type}", current_page(page_type, f"fixture_{page_type}"))

    graph = load_tool("build_graph").build_graph(tmp_path)
    nodes = {node["id"]: node for node in graph["nodes"]}
    edges = {(edge["source"], edge["target"], edge["type"]) for edge in graph["edges"]}

    assert len(nodes) == len(graph["nodes"])
    assert nodes["recurrent_vit"]["type"] == "moc"
    assert nodes["recurrent_vit"]["path"] == "mocs/recurrent_vit.md"
    assert nodes["finding"] == {
        "id": "finding",
        "type": "note",
        "title": "Finding",
        "status": "stable",
        "summary": "Summary for finding.",
        "tags": ["topic/test"],
        "path": "notes/finding.md",
    }
    assert graph["metadata"]["types"]["moc"] == 1
    assert graph["metadata"]["types"]["note"] == 1
    assert graph["metadata"]["mocs"] == 1
    assert ("legacy_one", "legacy_two", "cites") in edges
    assert ("legacy_one", "concept_test", "has-concept") in edges
    assert ("concept_test", "legacy_one", "anchors") in edges
    assert ("thread_one", "legacy_two", "anchors") in edges
    assert ("thread_one", "concept_test", "touches-concept") in edges
    assert ("legacy_one", "recurrent_vit", "relevant-to") in edges
    assert ("concept_test", "legacy_two", "grounded-in") in edges
    assert ("concept_test", "legacy_one", "see-also") in edges


def test_graph_serializers_support_current_node_fields_and_dynamic_summary(tmp_path: Path) -> None:
    graph = {
        "metadata": {"nodes": 1, "edges": 0, "types": {"brief": 1}, "briefs": 1},
        "nodes": [{
            "id": "brief_one", "type": "brief", "title": "Brief", "status": "draft",
            "summary": "A <useful> summary.", "tags": ["topic/test"], "path": "briefs/brief_one.md",
        }],
        "edges": [],
    }
    builder = load_tool("build_graph")
    graphml_path = tmp_path / "graph.graphml"
    summary_path = tmp_path / "summary.md"

    builder.write_graphml(graph, graphml_path)
    builder.write_summary_markdown(graph, summary_path)

    graphml = graphml_path.read_text(encoding="utf-8")
    summary = summary_path.read_text(encoding="utf-8")
    assert 'attr.name="summary"' in graphml
    assert "A &lt;useful&gt; summary." in graphml
    assert "  - brief: 1" in summary


def test_graph_rejects_malformed_yaml(tmp_path: Path) -> None:
    malformed = tmp_path / "notes" / "bad.md"
    malformed.parent.mkdir(parents=True)
    malformed.write_text("---\ntags: [unterminated\n---\n", encoding="utf-8")

    with pytest.raises(ValueError, match="notes/bad.md"):
        load_tool("build_graph").build_graph(tmp_path)


@pytest.mark.parametrize(
    ("directory", "slug", "field", "value", "message"),
    [
        (
            "concepts", "concept_one", "papers", "[[nested]]",
            "concepts/concept_one.md field 'papers' must be a list of strings",
        ),
        (
            "threads", "thread_one", "concepts", "[{bad: shape}]",
            "threads/thread_one.md field 'concepts' must be a list of strings",
        ),
        (
            "papers", "paper_one", "related", "paper_two",
            "papers/paper_one.md field 'related' must be a list of strings",
        ),
        (
            "papers", "paper_one", "concepts", "[[concept-test]]",
            "papers/paper_one.md field 'concepts' must be a list of strings",
        ),
        (
            "papers", "paper_one", "relevance_to", "[{bad: shape}]",
            "papers/paper_one.md field 'relevance_to' must be a list of strings",
        ),
    ],
)
def test_graph_rejects_malformed_legacy_relationship_values(
    tmp_path: Path, directory: str, slug: str, field: str, value: str, message: str
) -> None:
    if directory == "papers":
        canonical = {
            "concepts": "[concept-test]",
            "related": "[]",
            "relevance_to": "[recurrent_vit]",
        }[field]
        frontmatter = legacy_paper(slug).replace(
            f"{field}: {canonical}",
            f"{field}: {value}",
        )
    else:
        page_type = "concept" if directory == "concepts" else "thread"
        frontmatter = f"""
id: {slug}
type: {page_type}
title: Fixture
papers: []
concepts: []
last_updated: 2026-01-01
{field}: {value}
"""
    write_page(tmp_path, directory, slug, frontmatter)

    with pytest.raises(ValueError, match=message):
        load_tool("build_graph").build_graph(tmp_path)


def test_graph_rejects_unresolved_legacy_relationship_targets(tmp_path: Path) -> None:
    write_page(
        tmp_path,
        "concepts",
        "concept_one",
        """
id: concept_one
type: concept
papers: [missing_paper]
concepts: []
last_updated: 2026-01-01
""",
    )

    with pytest.raises(ValueError, match="papers target 'missing_paper' does not resolve"):
        load_tool("build_graph").build_graph(tmp_path)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        (
            "related",
            "[missing_paper]",
            "papers/paper_one.md related target 'missing_paper' does not resolve to a paper",
        ),
        (
            "relevance_to",
            "[missing_work]",
            "papers/paper_one.md relevance_to target 'missing_work' does not resolve to a page or historical work",
        ),
    ],
)
def test_graph_rejects_unresolved_legacy_paper_relationship_targets(
    tmp_path: Path, field: str, value: str, message: str
) -> None:
    write_taxonomy(tmp_path)
    canonical = {"related": "[]", "relevance_to": "[recurrent_vit]"}[field]
    frontmatter = legacy_paper("paper_one").replace(
        f"{field}: {canonical}",
        f"{field}: {value}",
    )
    write_page(tmp_path, "papers", "paper_one", frontmatter)

    with pytest.raises(ValueError, match=message):
        load_tool("build_graph").build_graph(tmp_path)


def test_graph_uses_body_heading_and_emits_common_fields_for_legacy_pages(tmp_path: Path) -> None:
    write_page(
        tmp_path,
        "concepts",
        "legacy_concept",
        """
id: legacy_concept
type: concept
papers: []
""",
        body="# Human-readable concept title\n",
    )

    node = load_tool("build_graph").build_graph(tmp_path)["nodes"][0]

    assert node == {
        "id": "legacy_concept",
        "type": "concept",
        "title": "Human-readable concept title",
        "status": "",
        "summary": "",
        "tags": [],
        "path": "concepts/legacy_concept.md",
    }
