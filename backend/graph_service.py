import json
import os
import tempfile
from functools import lru_cache
from typing import Optional

import networkx as nx
from pyvis.network import Network

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH_PATH = os.path.join(BASE_DIR, "data", "knowledge_graph.json")

# ── Color / icon scheme ───────────────────────────────────────────────────────
TYPE_COLORS: dict[str, str] = {
    "Person":   "#c87d50",
    "Topic":    "#5888b8",
    "Artifact": "#4e9e72",
    "Decision": "#b85858",
    "Unknown":  "#6e6e78",
}
TYPE_ICONS: dict[str, str] = {
    "Person":   "👤",
    "Topic":    "💡",
    "Artifact": "📦",
    "Decision": "⚖️",
    "Unknown":  "❓",
}

GRAPH_BG        = "#0d0d0f"
GRAPH_FONT      = "#c8c4bc"
EDGE_COLOR      = "#2a2a32"
EDGE_HIGHLIGHT  = "#b8955a"


# ── Graph loading ─────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def load_graph() -> nx.DiGraph:
    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return nx.node_link_graph(data)


# ── Metadata ──────────────────────────────────────────────────────────────────
def get_meta() -> dict:
    G = load_graph()
    all_types = sorted(set(d.get("type", "Unknown") for _, d in G.nodes(data=True)))
    all_rels  = sorted(set(d.get("relationship", "?") for _, _, d in G.edges(data=True)))
    return {
        "node_count":        G.number_of_nodes(),
        "edge_count":        G.number_of_edges(),
        "entity_types":      all_types,
        "relationship_types": all_rels,
    }


# ── Filtered subgraph ─────────────────────────────────────────────────────────
def build_filtered_subgraph(
    types:      list[str],
    rels:       list[str],
    min_degree: int = 1,
    max_nodes:  int = 200,
    search:     str = "",
) -> nx.DiGraph:
    G = load_graph()
    nodes = [
        n for n, d in G.nodes(data=True)
        if d.get("type", "Unknown") in types
        and G.degree(n) >= min_degree
        and (not search or search.lower() in d.get("display_name", n).lower())
    ]
    nodes = sorted(nodes, key=lambda n: G.degree(n), reverse=True)[:max_nodes]
    node_set = set(nodes)
    edges = [
        (u, v, d) for u, v, d in G.edges(data=True)
        if u in node_set and v in node_set
        and d.get("relationship", "?") in rels
    ]
    sub = nx.DiGraph()
    sub.add_nodes_from([(n, G.nodes[n]) for n in nodes])
    sub.add_edges_from(edges)
    return sub


# ── PyVis HTML rendering ──────────────────────────────────────────────────────
def render_pyvis_html(
    graph:      nx.DiGraph,
    physics_on: bool = True,
    gravity:    int  = -2000,
) -> str:
    net = Network(
        height="670px",
        width="100%",
        bgcolor=GRAPH_BG,
        font_color=GRAPH_FONT,
        directed=True,
        notebook=False,
    )
    net.force_atlas_2based(
        gravity=gravity,
        central_gravity=0.01,
        spring_length=130,
        spring_strength=0.05,
        damping=0.4,
    )

    for node_id, data in graph.nodes(data=True):
        ntype  = data.get("type", "Unknown")
        label  = data.get("display_name", node_id)
        color  = TYPE_COLORS.get(ntype, "#6e6e78")
        deg    = graph.degree(node_id)
        size   = max(12, min(46, 10 + deg * 3))
        # Plain-text tooltip — avoids vis.js printing raw HTML on click
        title  = f"{label}\nType: {TYPE_ICONS.get(ntype, '❓')} {ntype}  ·  degree: {deg}"
        net.add_node(
            node_id,
            label=label[:26] + ("…" if len(label) > 26 else ""),
            title=title,
            color={
                "background": color,
                "border": "#0d0d0f",
                "highlight": {"background": "#e8e4dc", "border": color},
                "hover":     {"background": color,    "border": "#e8e4dc"},
            },
            size=size,
            font={"size": 11, "color": GRAPH_FONT, "strokeWidth": 2, "strokeColor": GRAPH_BG},
            borderWidth=2,
            borderWidthSelected=3,
        )

    for src, tgt, data in graph.edges(data=True):
        rel   = data.get("relationship", "related")
        ev    = data.get("evidence", {})
        url   = ev.get("source_url", "")
        quote = ev.get("quote", "")[:100]
        # Plain-text tooltip
        title = rel.replace('_', ' ')
        if quote:
            title += f"\n{quote}"
        if url:
            title += f"\n↗ {url}"
        net.add_edge(
            src, tgt,
            title=title,
            label=rel.replace("_", " "),
            color={"color": EDGE_COLOR, "highlight": EDGE_HIGHLIGHT, "hover": EDGE_HIGHLIGHT},
            arrows="to",
            smooth={"type": "dynamic"},
            font={"size": 9, "color": "#3e3e44", "strokeWidth": 0},
            width=1.2,
        )

    if not physics_on:
        net.toggle_physics(False)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as f:
        net.save_graph(f.name)
        fname = f.name
    with open(fname, "r", encoding="utf-8") as f:
        html = f.read()
    os.unlink(fname)

    # Inject iframe-level CSS so the graph blends with the React dark theme
    inject = """
<style>
  body { background: #0d0d0f !important; margin: 0 !important; }
  #mynetwork { background: #0d0d0f !important; border: none !important; }
  div.vis-tooltip {
    background: #16161a !important;
    border: 1px solid #2a2a32 !important;
    color: #e8e4dc !important;
    border-radius: 6px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 12px !important;
    line-height: 1.6 !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.6) !important;
    padding: 8px 12px !important;
    white-space: pre-line !important;
    max-width: 320px !important;
    pointer-events: none !important;
  }
  div.vis-network canvas { background: #0d0d0f !important; }
</style>
"""
    html = html.replace("</head>", inject + "</head>")
    return html


# ── Analytics ─────────────────────────────────────────────────────────────────
def get_analytics() -> dict:
    G = load_graph()

    type_counts: dict[str, int] = {}
    for _, d in G.nodes(data=True):
        t = d.get("type", "Unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    rel_counts: dict[str, int] = {}
    for _, _, d in G.edges(data=True):
        r = d.get("relationship", "?")
        rel_counts[r] = rel_counts.get(r, 0) + 1
    top_rels = dict(sorted(rel_counts.items(), key=lambda x: -x[1])[:10])

    top_nodes = []
    for nid, deg in sorted(G.degree(), key=lambda x: -x[1])[:15]:
        nd = G.nodes[nid]
        top_nodes.append({
            "id":          nid,
            "name":        nd.get("display_name", nid),
            "type":        nd.get("type", "Unknown"),
            "icon":        TYPE_ICONS.get(nd.get("type", "Unknown"), "❓"),
            "total_degree": deg,
            "in_degree":   G.in_degree(nid),
            "out_degree":  G.out_degree(nid),
        })

    return {
        "type_counts": type_counts,
        "top_rel_counts": top_rels,
        "top_nodes": top_nodes,
    }


# ── All nodes list (for explorer dropdown) ────────────────────────────────────
def get_all_nodes() -> list[dict]:
    G = load_graph()
    return [
        {"id": n, "label": d.get("display_name", n)}
        for n, d in G.nodes(data=True)
    ]


# ── Node detail ───────────────────────────────────────────────────────────────
def get_node_detail(node_id: str) -> Optional[dict]:
    G = load_graph()
    if node_id not in G:
        return None
    nd    = G.nodes[node_id]
    ntype = nd.get("type", "Unknown")

    in_edges = []
    for src, _, d in G.in_edges(node_id, data=True):
        ev = d.get("evidence", {})
        in_edges.append({
            "source":       src,
            "source_name":  G.nodes[src].get("display_name", src),
            "relationship": d.get("relationship", "?"),
            "quote":        ev.get("quote", ""),
            "source_url":   ev.get("source_url", ""),
        })

    out_edges = []
    for _, tgt, d in G.out_edges(node_id, data=True):
        ev = d.get("evidence", {})
        out_edges.append({
            "target":       tgt,
            "target_name":  G.nodes[tgt].get("display_name", tgt),
            "relationship": d.get("relationship", "?"),
            "quote":        ev.get("quote", ""),
            "source_url":   ev.get("source_url", ""),
        })

    return {
        "id":           node_id,
        "display_name": nd.get("display_name", node_id),
        "type":         ntype,
        "icon":         TYPE_ICONS.get(ntype, "❓"),
        "color":        TYPE_COLORS.get(ntype, "#6e6e78"),
        "degree":       G.degree(node_id),
        "in_degree":    G.in_degree(node_id),
        "out_degree":   G.out_degree(node_id),
        "in_edges":     in_edges,
        "out_edges":    out_edges,
    }
