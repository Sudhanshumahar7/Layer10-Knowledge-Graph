from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import Optional
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse

from graph_service import (
    get_meta,
    build_filtered_subgraph,
    render_pyvis_html,
    get_analytics,
    get_all_nodes,
    get_node_detail,
)

app = FastAPI(title="Layer10 Knowledge Graph API", version="1.0.0")
print("--- Backend Initialization Started ---")

import threading
import time
import urllib.request

def keep_alive_ping():
    """Background thread to ping the server every 30s to help prevent Render sleep."""
    while True:
        time.sleep(30)
        try:
            # Ping our own API to simulate activity
            urllib.request.urlopen("http://127.0.0.1:8000/api/graph/meta")
        except Exception:
            pass

@app.on_event("startup")
def startup_event():
    print("Starting keep-alive background task (30s interval)...")
    threading.Thread(target=keep_alive_ping, daemon=True).start()


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

# ── Static Files & SPA Routing ────────────────────────────────────────────────
# In production/docker, the React build folder will be at /app/frontend/build
FRONTEND_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "build")

# Serve the 'static' folder inside 'build' for CSS/JS
if os.path.exists(os.path.join(FRONTEND_PATH, "static")):
    app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_PATH, "static")), name="static")

@app.get("/{full_path:path}")
async def serve_react(full_path: str):
    """
    Catch-all route. If the file exists in the build folder, serve it.
    Otherwise, serve index.html for React Router to handle the path.
    """
    file_path = os.path.join(FRONTEND_PATH, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Fallback to index.html for SPA
    index_path = os.path.join(FRONTEND_PATH, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # If build directory doesn't exist yet (local dev without build), return 404
    return {"detail": "Frontend build files not found. Run 'npm run build' in the frontend directory."}
