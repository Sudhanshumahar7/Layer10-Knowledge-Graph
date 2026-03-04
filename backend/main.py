from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import Optional

from graph_service import (
    get_meta,
    build_filtered_subgraph,
    render_pyvis_html,
    get_analytics,
    get_all_nodes,
    get_node_detail,
)

app = FastAPI(title="Layer10 Knowledge Graph API", version="1.0.0")

# Allow the React dev server (and any origin) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── /api/graph/meta ───────────────────────────────────────────────────────────
@app.get("/api/graph/meta")
def graph_meta():
    """Return node count, edge count, all entity types, all relationship types."""
    return get_meta()


# ── /api/graph/render ─────────────────────────────────────────────────────────
@app.get("/api/graph/render", response_class=HTMLResponse)
def graph_render(
    types:      list[str] = Query(default=[]),
    rels:       list[str] = Query(default=[]),
    min_degree: int       = Query(default=1, ge=1),
    max_nodes:  int       = Query(default=200, ge=10, le=500),
    search:     str       = Query(default=""),
    physics:    bool      = Query(default=True),
    gravity:    int       = Query(default=-2000),
):
    """
    Build a filtered subgraph and return the PyVis HTML page.
    The React frontend loads this URL inside an <iframe>.
    """
    meta = get_meta()

    # Default to all types/rels if none supplied
    if not types:
        types = meta["entity_types"]
    if not rels:
        rels = meta["relationship_types"]

    sub  = build_filtered_subgraph(types, rels, min_degree, max_nodes, search)
    html = render_pyvis_html(sub, physics, gravity)
    return HTMLResponse(content=html)


# ── /api/analytics ────────────────────────────────────────────────────────────
@app.get("/api/analytics")
def analytics():
    """Entity type distribution, top-10 relationship types, top-15 most-connected nodes."""
    return get_analytics()


# ── /api/nodes ────────────────────────────────────────────────────────────────
@app.get("/api/nodes")
def nodes_list():
    """All nodes (id + display label) — used for the Node Explorer dropdown."""
    return get_all_nodes()


# ── /api/nodes/{node_id} ─────────────────────────────────────────────────────
@app.get("/api/nodes/{node_id}")
def node_detail(node_id: str):
    """Full detail for a single node: attrs, in-edges, out-edges."""
    detail = get_node_detail(node_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found.")
    return detail
