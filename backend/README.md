# Layer10 Backend (FastAPI)

The backend service for the Layer10 Knowledge Graph. It provides APIs for graph metadata, analytics, filtering, and interactive visualization rendering.

## Setup & Running

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run with Uvicorn**:
   ```bash
   python -m uvicorn main:app --reload --port 8000
   ```

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/graph/meta` | GET | Returns node count, edge count, and lists of all entity/relationship types. |
| `/api/graph/render` | GET | Accepts filter params (`types`, `rels`, `min_degree`, etc.) and returns a PyVis HTML string for iframe embedding. |
| `/api/analytics` | GET | Returns data for entity distribution, top relationships, and the top-connected nodes table. |
| `/api/nodes` | GET | Returns a list of all node IDs and labels for search and discovery. |
| `/api/nodes/{id}` | GET | Returns detailed attributes for a single node, plus its full list of incoming/outgoing edges (with evidence). |

## Core Components

- **`main.py`**: The FastAPI application entry point. Handles routing and CORS.
- **`graph_service.py`**: The heart of the backend. Uses **NetworkX** to load the graph from `data/knowledge_graph.json`, apply filters, and build the PyVis interactive visualization.
- **`requirements.txt`**: Pinned dependencies for reproducible deployment.

## Deployment

The backend is configured for deployment on **Render.com** via the `render.yaml` found in the project root.
