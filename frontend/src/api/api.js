const BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

export { BASE_URL };

// ── /api/graph/meta ─────────────────────────────────────────────────────────
/** Returns { node_count, edge_count, entity_types[], relationship_types[] } */
export async function getGraphMeta() {
    const res = await fetch(`${BASE_URL}/api/graph/meta`);
    if (!res.ok) throw new Error(`getGraphMeta: ${res.status}`);
    return res.json();
}

// ── /api/graph/render ────────────────────────────────────────────────────────
/**
 * Builds the URL string used as the graph iframe's src.
 * No fetch here — the iframe loads it directly.
 */
export function buildGraphRenderUrl({
    types = [],
    rels = [],
    minDegree = 1,
    maxNodes = 200,
    search = '',
    physics = true,
    gravity = -2000,
} = {}) {
    const p = new URLSearchParams();
    types.forEach(t => p.append('types', t));
    rels.forEach(r => p.append('rels', r));
    p.set('min_degree', minDegree);
    p.set('max_nodes', maxNodes);
    p.set('search', search);
    p.set('physics', physics);
    p.set('gravity', gravity);
    return `${BASE_URL}/api/graph/render?${p.toString()}`;
}

// ── /api/analytics ───────────────────────────────────────────────────────────
/** Returns { type_counts, top_rel_counts, top_nodes[] } */
export async function getAnalytics() {
    const res = await fetch(`${BASE_URL}/api/analytics`);
    if (!res.ok) throw new Error(`getAnalytics: ${res.status}`);
    return res.json();
}

// ── /api/nodes ───────────────────────────────────────────────────────────────
/** Returns [{ id, label }] — all nodes, sorted alphabetically by caller */
export async function getAllNodes() {
    const res = await fetch(`${BASE_URL}/api/nodes`);
    if (!res.ok) throw new Error(`getAllNodes: ${res.status}`);
    return res.json();
}

// ── /api/nodes/{node_id} ─────────────────────────────────────────────────────
/** Returns full node detail + in/out edges, or null if 404 */
export async function getNodeDetail(nodeId) {
    const res = await fetch(
        `${BASE_URL}/api/nodes/${encodeURIComponent(nodeId)}`
    );
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(`getNodeDetail: ${res.status}`);
    return res.json();
}
