import networkx as nx
import community.community_louvain as community_louvain
from typing import List, Dict, Set, Any

MAX_NODES = 5000
MAX_EDGES = 25000

def native_pagerank(G: nx.DiGraph, alpha: float = 0.85, max_iter: int = 100, tol: float = 1e-6) -> Dict[str, float]:
    nodes = list(G.nodes())
    num_nodes = len(nodes)
    if num_nodes == 0:
        return {}

    pagerank = {node: 1.0 / num_nodes for node in nodes}
    
    for _ in range(max_iter):
        next_pagerank = {node: 0.0 for node in nodes}
        dangling_sum = sum(pagerank[node] for node in nodes if G.out_degree(node) == 0)
        
        for node in nodes:
            for successor in G.successors(node):
                out_degree = G.out_degree(node)
                edge_weight = G[node][successor].get('weight', 1.0)
                total_out_weight = sum(G[node][tgt].get('weight', 1.0) for tgt in G.successors(node))
                normalized_weight = edge_weight / total_out_weight if total_out_weight > 0 else 1.0 / out_degree
                
                next_pagerank[successor] += pagerank[node] * normalized_weight
                
            next_pagerank[node] += dangling_sum / num_nodes
            next_pagerank[node] = alpha * next_pagerank[node] + (1.0 - alpha) / num_nodes

        err = sum(abs(next_pagerank[node] - pagerank[node]) for node in nodes)
        pagerank = next_pagerank
        if err < tol:
            break
            
    return pagerank

def process_social_graph(merchants: List[Dict[str, Any]], vouches: List[Dict[str, Any]]) -> Dict[str, Any]:
    if len(merchants) > MAX_NODES or len(vouches) > MAX_EDGES:
        raise ValueError("Payload exceeds maximum safe graph dimensions.")

    G = nx.DiGraph()

    for m in merchants:
        G.add_node(m["id"], name=m.get("name", "Unknown"), base_score=m.get("score", 0))

    for v in vouches:
        if v["source"] != v["target"]:
            if G.has_node(v["source"]) and G.has_node(v["target"]):
                G.add_edge(v["source"], v["target"], weight=float(v.get("weight", 1.0)))

    for node in G.nodes():
        outgoing = list(G.out_edges(node, data=True))
        if outgoing:
            total_weight = sum(data['weight'] for _, _, data in outgoing)
            if total_weight > 0:
                for u, v, data in outgoing:
                    G[u][v]['weight'] = data['weight'] / total_weight

    trust_scores = native_pagerank(G, alpha=0.85)

    undirected_G = G.to_undirected()
    fraud_nodes: Set[str] = set()
    
    if len(undirected_G.edges()) > 0:
        partitions = community_louvain.best_partition(undirected_G)
        communities: Dict[int, List[str]] = {}
        for node, comm_id in partitions.items():
            communities.setdefault(comm_id, []).append(node)
            
        for comm_id, members in communities.items():
            if 3 <= len(members) <= 10:
                internal_edges = 0
                external_edges = 0
                for u in members:
                    for v in G.successors(u):
                        if v in members:
                            internal_edges += 1
                        else:
                            external_edges += 1
                            
                # ALGORITHMIC FIX: A closed circular loop must have at least as many edges as nodes.
                # This prevents isolated linear chains (like Saraswati's legitimate community) from being flagged.
                if internal_edges >= len(members) and external_edges == 0:
                    fraud_nodes.update(members)

    nodes_out = []
    for node_id in G.nodes():
        nodes_out.append({
            "id": str(node_id),
            "name": G.nodes[node_id].get("name", "Unknown"),
            "trust": round(trust_scores.get(node_id, 0.0), 4),
            "score": G.nodes[node_id].get("base_score", 0),
            "fraud": node_id in fraud_nodes
        })

    edges_out = [
        {"source": str(u), "target": str(v), "weight": round(d["weight"], 4)}
        for u, v, d in G.edges(data=True)
    ]

    return {
        "nodes": nodes_out,
        "edges": edges_out
    }