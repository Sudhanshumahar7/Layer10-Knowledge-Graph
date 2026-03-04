import json
import os
import re
import networkx as nx
from collections import defaultdict

# Paths relative to this script (script lives in pipeline/, data is at ../data/)
DATA_DIR    = os.path.join(os.path.dirname(__file__), "..", "data")
INPUT_FILE  = os.path.join(DATA_DIR, "graph_extractions.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "knowledge_graph.json")


# ---------------------------------------------------------------------------
# 1. Entity Resolution helpers
# ---------------------------------------------------------------------------

def normalize_id(raw_id: str) -> str:
    key = raw_id.lower().strip()
    key = re.sub(r"[\s\-]+", "_", key)
    key = re.sub(r"_+", "_", key)
    return key


def resolve_entities(all_entities: list[dict]) -> dict[str, dict]:
    resolved: dict[str, dict] = {}
    for ent in all_entities:
        key = normalize_id(ent["id"])
        if key not in resolved:
            resolved[key] = {**ent, "canonical_id": key, "aliases": set()}
        else:
            existing = resolved[key]
            if len(ent.get("display_name", "")) > len(existing.get("display_name", "")):
                existing["display_name"] = ent["display_name"]
            existing["aliases"].add(ent["id"])

    for ent in resolved.values():
        ent["aliases"] = sorted(ent["aliases"])

    return resolved


# ---------------------------------------------------------------------------
# 2. Build the graph
# ---------------------------------------------------------------------------

def build_graph(extractions: list[dict]) -> nx.DiGraph:
    G = nx.DiGraph()

    raw_entities: list[dict] = []
    for batch in extractions:
        raw_entities.extend(batch.get("entities", []))

    entity_map = resolve_entities(raw_entities)
    print(f"  Raw entity count  : {len(raw_entities)}")
    print(f"  After dedup       : {len(entity_map)} unique entities")

    for canonical_id, ent in entity_map.items():
        G.add_node(
            canonical_id,
            display_name=ent.get("display_name", canonical_id),
            type=ent.get("type", "Unknown"),
            aliases=ent.get("aliases", []),
        )

    edge_count = 0
    skipped    = 0
    for batch in extractions:
        for claim in batch.get("claims", []):
            src_key  = normalize_id(claim.get("source_entity_id", ""))
            tgt_key  = normalize_id(claim.get("target_entity_id", ""))
            rel      = claim.get("relationship", "Related_To")
            evidence = claim.get("evidence", {})

            if src_key not in G or tgt_key not in G:
                skipped += 1
                continue

            if G.has_edge(src_key, tgt_key):
                existing = G[src_key][tgt_key]
                if existing.get("relationship") == rel:
                    existing.setdefault("evidence_list", [existing.get("evidence", {})]).append(evidence)
                    edge_count += 1
                    continue

            G.add_edge(src_key, tgt_key, relationship=rel, evidence=evidence, evidence_list=[evidence])
            edge_count += 1

    print(f"  Total claims      : {sum(len(b.get('claims',[])) for b in extractions)}")
    print(f"  Edges added       : {edge_count}")
    print(f"  Edges skipped     : {skipped}  (unknown entity IDs)")
    return G


# ---------------------------------------------------------------------------
# 3. Print summary stats
# ---------------------------------------------------------------------------

def print_stats(G: nx.DiGraph):
    print("\n── Graph Statistics ────────────────────────────────")
    print(f"  Nodes            : {G.number_of_nodes()}")
    print(f"  Edges            : {G.number_of_edges()}")

    type_counts: dict[str, int] = defaultdict(int)
    for _, data in G.nodes(data=True):
        type_counts[data.get("type", "Unknown")] += 1
    print("  Node types:")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"    {t:<15} {c}")

    rel_counts: dict[str, int] = defaultdict(int)
    for _, _, data in G.edges(data=True):
        rel_counts[data.get("relationship", "?")] += 1
    print("  Top 10 relationships:")
    for r, c in sorted(rel_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"    {r:<30} {c}")

    top_nodes = sorted(G.degree(), key=lambda x: -x[1])[:10]
    print("  Top 10 most-connected nodes:")
    for node_id, deg in top_nodes:
        name = G.nodes[node_id].get("display_name", node_id)
        print(f"    {name:<40} degree={deg}")
    print("────────────────────────────────────────────────────")


# ---------------------------------------------------------------------------
# 4. Serialise to JSON
# ---------------------------------------------------------------------------

def save_graph(G: nx.DiGraph, path: str):
    data = nx.node_link_data(G)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    size_kb = os.path.getsize(path) / 1024
    print(f"\n  Graph saved → {path}  ({size_kb:.1f} KB)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Loading {INPUT_FILE} ...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        extractions = json.load(f)
    print(f"  Batches loaded: {len(extractions)}")

    print("\nBuilding graph ...")
    G = build_graph(extractions)

    print_stats(G)
    save_graph(G, OUTPUT_FILE)

    print("\nPhase 3 complete ✓")
