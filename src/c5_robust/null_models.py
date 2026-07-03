"""Degree-preserving rewiring null models and a hub-deletion check.

Confirms the A(p) signal exceeds what a random graph with the same degree
sequence would produce, and that removing textbook hubs does not overturn
the result.
"""
import networkx as nx


def degree_preserving_null(graph, n_swaps, seed):
    """Directed double-edge-swap keeping in/out degree fixed."""
    # TODO: nx.directed_edge_swap on a DiGraph copy
    raise NotImplementedError


def hub_deletion_check(graph, top_k):
    raise NotImplementedError


if __name__ == "__main__":
    pass
